from __future__ import annotations

import asyncio
import json
import logging
import os
import re
from typing import (
    TYPE_CHECKING,
    Any,
    AsyncIterable,
    Awaitable,
    Callable,
    Coroutine,
    Generic,
    Iterable,
    TypeVar,
    TypeVarTuple,
    overload,
)

from .conditions import PlainTextCondition, RegexCondition
from .default_events import get_default_events
from .errors import InvalidContextDataReceived, PluginNotInitialized
from .flow import FlowLauncherAPI, FlowSettings, PluginMetadata
from .jsonrpc import (
    ErrorResponse,
    ExecuteResponse,
    JsonRPCClient,
    QueryResponse,
    Result,
)
from .jsonrpc.responses import BaseResponse
from .query import Query
from .search_handler import SearchHandler
from .settings import Settings
from .utils import MISSING, cached_property, coro_or_gen, setup_logging

if TYPE_CHECKING:
    from typing_extensions import TypeVar

    from ._types import RawSettings, SearchHandlerCallback, SearchHandlerCondition

    SettingsT = TypeVar("SettingsT", default=Settings, bound=Settings)
else:
    SettingsT = TypeVar("SettingsT")

TS = TypeVarTuple("TS")
EventCallbackT = TypeVar(
    "EventCallbackT", bound=Callable[..., Coroutine[Any, Any, Any]]
)
LOG = logging.getLogger(__name__)

__all__ = ("Plugin",)


class Plugin(Generic[SettingsT]):
    r"""This class represents your plugin.

    This class implements a generic for a custom :class:`~flogin.settings.Settings` class for typechecking purposes.

    Parameters
    -----------
    settings_no_update: Optional[:class:`bool`]
        Whether or not to let flow update flogin's version of the settings. This can be useful when using a custom settings menu. Defaults to ``False``
    ignore_cancellation_requests: Optional[:class:`bool`]
        Whether or not to ignore cancellation requests sent from flow. Defaults to ``False``

    Attributes
    ----------
    settings: :class:`~flogin.settings.Settings`
        The plugin's settings set by the user
    api: :class:`~flogin.flow.api.FlowLauncherAPI`
        An easy way to acess Flow Launcher's API
    last_query: :class:`~flogin.query.Query` | ``None``
        The last query request that flow sent. This is ``None`` if no query request has been sent yet.
    """

    def __init__(self, **options: Any) -> None:
        self.options = options
        self._metadata: PluginMetadata | None = None
        self._search_handlers: list[SearchHandler] = []
        self._results: dict[str, Result] = {}
        self._settings_are_populated: bool = False
        self.last_query: Query | None = None

        self._events: dict[str, Callable[..., Awaitable[Any]]] = get_default_events(
            self
        )
        self.jsonrpc: JsonRPCClient = JsonRPCClient(self)
        self.api = FlowLauncherAPI(self.jsonrpc)

    @cached_property
    def settings(self) -> SettingsT:
        fp = os.path.join(
            "..", "..", "Settings", "Plugins", self.metadata.name, "Settings.json"
        )
        with open(fp, "r") as f:
            data = json.load(f)
        self._settings_are_populated = True
        LOG.debug(f"Settings filled from file: {data!r}")
        sets = Settings(data, no_update=self.options.get("settings_no_update", False))
        return sets  # type: ignore

    async def _run_event(
        self,
        coro: Callable[..., Awaitable[Any]],
        event_name: str,
        args: Iterable[Any],
        kwargs: dict[str, Any],
        error_handler: Callable[[Exception], Coroutine[Any, Any, Any]] | str = MISSING,
    ) -> Any:
        try:
            return await coro(*args, **kwargs)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            if error_handler is MISSING:
                error_handler = "on_error"
            if isinstance(error_handler, str):
                return await self._events[error_handler](event_name, e, *args, **kwargs)
            else:
                return await error_handler(e)

    def _schedule_event(
        self,
        coro: Callable[..., Awaitable[Any]],
        event_name: str,
        args: Iterable[Any] = MISSING,
        kwargs: dict[str, Any] = MISSING,
        error_handler: Callable[[Exception], Coroutine[Any, Any, Any]] | str = MISSING,
    ) -> asyncio.Task:
        wrapped = self._run_event(
            coro, event_name, args or [], kwargs or {}, error_handler
        )
        return asyncio.create_task(wrapped, name=f"flogin: {event_name}")

    def dispatch(
        self, event: str, *args: Any, **kwargs: Any
    ) -> None | asyncio.Task[None | BaseResponse]:
        method = f"on_{event}"

        # Special Event Cases
        replacements = {
            "on_initialize": "_initialize_wrapper",
        }
        method = replacements.get(method, method)

        LOG.debug("Dispatching event %s", method)

        event_callback = self._events.get(method)
        if event_callback:
            return self._schedule_event(event_callback, method, args, kwargs)

    async def _coro_or_gen_to_results(
        self, coro: Awaitable | AsyncIterable
    ) -> list[Result] | ErrorResponse:
        results = []
        raw_results = await coro_or_gen(coro)

        if raw_results is None:
            return results

        if isinstance(raw_results, ErrorResponse):
            return raw_results
        if isinstance(raw_results, dict):
            res = Result.from_dict(raw_results)
            self._results[res.slug] = res
            results.append(res)
        else:
            if not isinstance(raw_results, list):
                raw_results = [raw_results]
            for raw_res in raw_results:
                res = Result.from_anything(raw_res)
                self._results[res.slug] = res
                results.append(res)
        return results

    async def _initialize_wrapper(self, arg: dict[str, Any]) -> ExecuteResponse:
        LOG.info(f"Initialize: {json.dumps(arg)}")
        self._metadata = PluginMetadata(arg["currentPluginMetadata"], self.api)
        self.dispatch("initialization")
        return ExecuteResponse(hide=False)

    async def process_context_menus(
        self, data: list[Any]
    ) -> QueryResponse | ErrorResponse:
        LOG.debug(f"Context Menu Handler: {data=}")

        if not data:
            raise InvalidContextDataReceived()

        result = self._results.get(data[0])

        if result is not None:
            result.plugin = self
            task = self._schedule_event(
                self._coro_or_gen_to_results,
                event_name=f"ContextMenu-{result.slug}",
                args=[result.context_menu()],
                error_handler=lambda e: self._coro_or_gen_to_results(
                    result.on_context_menu_error(e)
                ),
            )
            results = await task
        else:
            results = []

        if isinstance(results, ErrorResponse):
            return results
        return QueryResponse(results, self.settings._get_updates())

    async def process_search_handlers(
        self, query: Query
    ) -> QueryResponse | ErrorResponse:
        results = []
        for handler in self._search_handlers:
            handler.plugin = self
            if handler.condition(query):
                task = self._schedule_event(
                    self._coro_or_gen_to_results,
                    event_name=f"SearchHandler-{handler.name}",
                    args=[handler.callback(query)],
                    error_handler=lambda e: self._coro_or_gen_to_results(
                        handler.on_error(query, e)
                    ),
                )
                results = await task
                break

        if isinstance(results, ErrorResponse):
            return results
        return QueryResponse(results, self.settings._get_updates())

    @property
    def metadata(self) -> PluginMetadata:
        """
        Returns the plugin's metadata.

        Raises
        --------
        :class:`~flogin.errors.PluginNotInitialized`
            This gets raised if the plugin hasn't been initialized yet
        """
        if self._metadata:
            return self._metadata
        raise PluginNotInitialized()

    async def start(self):
        r"""|coro|

        The default startup/setup method. This can be overriden for advanced startup behavior, but make sure to run ``await super().start()`` to actually start your plugin.
        """

        import aioconsole

        reader, writer = await aioconsole.get_standard_streams()
        await self.jsonrpc.start_listening(reader, writer)

    def run(self, *, setup_default_log_handler: bool = True) -> None:
        r"""The default runner. This runs the :func:`~flogin.plugin.Plugin.start` coroutine, and setups up logging.

        Parameters
        --------
        setup_default_log_handler: :class:`bool`
            Whether to setup the default log handler or not, defaults to `True`.
        """

        if setup_default_log_handler:
            setup_logging()

        try:
            asyncio.run(self.start())
        except Exception as e:
            LOG.exception(
                f"A fatal error has occured which crashed flogin: {e}", exc_info=e
            )

    def register_search_handler(self, handler: SearchHandler[Any]) -> None:
        r"""Register a new search handler

        See the :ref:`search handler section <search_handlers>` for more information about using search handlers.

        Parameters
        -----------
        handler: :class:`~flogin.search_handler.SearchHandler`
            The search handler to be registered
        """

        self._search_handlers.append(handler)
        LOG.info(f"Registered search handler: {handler}")

    def register_search_handlers(self, *handlers: SearchHandler[Any]) -> None:
        r"""Register new search handlers

        See the :ref:`search handler section <search_handlers>` for more information about using search handlers.

        Parameters
        -----------
        *handlers: list[:class:`~flogin.search_handler.SearchHandler`]
            The search handlers to be registered
        """

        for handler in handlers:
            self.register_search_handler(handler)

    def register_event(
        self, callback: Callable[..., Coroutine[Any, Any, Any]], name: str | None = None
    ) -> None:
        """Registers an event to listen for. See the :func:`~flogin.plugin.Plugin.event` decorator for another method of registering events.

        All events must be a :ref:`coroutine <coroutine>`.

        .. NOTE::
            See the :ref:`event reference <events>` to see what valid events there are.

        Parameters
        -----------
        callback: :ref:`coroutine <coroutine>`
            The :ref:`coroutine <coroutine>` to be executed with the event
        name: Optional[:class:`str`]
            The name of the event to be registered. Defaults to the callback's name.
        """

        self._events[name or callback.__name__] = callback

    def event(self, callback: EventCallbackT) -> EventCallbackT:
        """A decorator that registers an event to listen for.

        All events must be a :ref:`coroutine <coroutine>`.

        .. NOTE::
            See the :ref:`event reference <events>` to see what valid events there are.

        Example
        ---------

        .. code-block:: python3

            @plugin.event
            async def on_initialization():
                print('Ready!')

        """

        self.register_event(callback)
        return callback

    @overload
    def search(
        self, condition: SearchHandlerCondition
    ) -> Callable[[SearchHandlerCallback], SearchHandler]: ...

    @overload
    def search(
        self, *, text: str
    ) -> Callable[[SearchHandlerCallback], SearchHandler]: ...

    @overload
    def search(
        self,
        *,
        pattern: re.Pattern | str = MISSING,
    ) -> Callable[[SearchHandlerCallback], SearchHandler]: ...

    @overload
    def search(
        self,
        *,
        keyword: str = MISSING,
    ) -> Callable[[SearchHandlerCallback], SearchHandler]: ...

    @overload
    def search(
        self,
        *,
        allowed_keywords: Iterable[str] = MISSING,
    ) -> Callable[[SearchHandlerCallback], SearchHandler]: ...

    @overload
    def search(
        self,
        *,
        disallowed_keywords: Iterable[str] = MISSING,
    ) -> Callable[[SearchHandlerCallback], SearchHandler]: ...

    @overload
    def search(
        self,
    ) -> Callable[[SearchHandlerCallback], SearchHandler]: ...

    def search(
        self,
        condition: SearchHandlerCondition | None = None,
        *,
        text: str = MISSING,
        pattern: re.Pattern | str = MISSING,
        keyword: str = MISSING,
        allowed_keywords: Iterable[str] = MISSING,
        disallowed_keywords: Iterable[str] = MISSING,
    ) -> Callable[[SearchHandlerCallback], SearchHandler]:
        """A decorator that registers a search handler.

        All search handlers must be a :ref:`coroutine <coroutine>`. See the :ref:`search handler section <search_handlers>` for more information about using search handlers.

        Parameters
        ----------
        condition: Optional[:ref:`condition <condition_example>`]
            The condition to determine which queries this handler should run on. If given, this should be the only argument given.
        text: Optional[:class:`str`]
            A kwarg to quickly add a :class:`~flogin.conditions.PlainTextCondition`. If given, this should be the only argument given.
        pattern: Optional[:class:`re.Pattern` | :class:`str`]
            A kwarg to quickly add a :class:`~flogin.conditions.RegexCondition`. If given, this should be the only argument given.
        keyword: Optional[:class:`str`]
            A kwarg to quickly set the condition to a :class:`~flogin.conditions.KeywordCondition` condition with the ``keyword`` kwarg being the only allowed keyword.
        allowed_keywords: Optional[Iterable[:class:`str`]]
            A kwarg to quickly set the condition to a :class:`~flogin.conditions.KeywordCondition` condition with the kwarg being the list of allowed keywords.
        disallowed_keywords: Optional[Iterable[:class:`str`]]
            A kwarg to quickly set the condition to a :class:`~flogin.conditions.KeywordCondition` condition with the kwarg being the list of disallowed keywords.

        Example
        ---------

        .. code-block:: python3

            @plugin.on_search()
            async def example_search_handler(data: Query):
                return "This is a result!"

        """

        if condition is None:
            condition = SearchHandler._builtin_condition_kwarg_to_obj(
                text=text,
                pattern=pattern,
                keyword=keyword,
                allowed_keywords=allowed_keywords,
                disallowed_keywords=disallowed_keywords,
            )

        def inner(func: SearchHandlerCallback) -> SearchHandler:
            handler = SearchHandler()
            if condition:
                handler.condition = condition  # type: ignore
            handler.callback = func  # type: ignore # type is the same
            self.register_search_handler(handler)
            return handler

        return inner

    def fetch_flow_settings(self) -> FlowSettings:
        """Fetches flow's settings from flow's config file

        Returns
        --------
        :class:`~flogin.flow.settings.FlowSettings`
            A dataclass containing all of flow's settings
        """

        path = os.path.join("..", "..", "Settings", "Settings.json")
        with open(path, "r") as f:
            data = json.load(f)
        return FlowSettings(data)

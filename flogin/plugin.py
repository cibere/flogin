from __future__ import annotations

import asyncio
import json
import logging
import os
from collections.abc import Awaitable, Callable, Coroutine, Iterable
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    Generic,
    Literal,
    TypeVar,
    TypeVarTuple,
    cast,
    overload,
)

from .default_events import get_default_events
from .errors import EnvNotSet, PluginNotInitialized
from .flow import FlowLauncherAPI, FlowSettings, PluginMetadata
from .jsonrpc import (
    ErrorResponse,
    ExecuteResponse,
    JsonRPCClient,
    QueryResponse,
    Result,
)
from .search_handler import SearchHandler
from .settings import Settings
from .utils import (
    MISSING,
    add_classmethod_alt,
    cached_property,
    coro_or_gen,
    decorator,
    func_with_self,
    setup_logging,
)

if TYPE_CHECKING:
    import re
    from asyncio.streams import StreamReader, StreamWriter

    from typing_extensions import TypeVar  # noqa: TC004

    from ._types.search_handlers import (
        ConvertableToResult,
        SearchHandlerCallback,
        SearchHandlerCallbackReturns,
        SearchHandlerCallbackWithSelf,
        SearchHandlerCondition,
    )
    from .query import Query

    SettingsT = TypeVar("SettingsT", default=Settings, bound=Settings)
else:
    SettingsT = TypeVar("SettingsT")

TS = TypeVarTuple("TS")
EventCallbackT = TypeVar(
    "EventCallbackT", bound=Callable[..., Coroutine[Any, Any, Any]]
)
log = logging.getLogger(__name__)

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
    disable_log_override_files: Optional[:class:`bool`]
        Whether or not to disable the log override files. Defaults to ``False``. See :doc:`log-override-files` for more information on this.
    """

    __class_events__: ClassVar[list[str]] = []
    __class_search_handlers__: ClassVar[list[SearchHandler]] = []

    def __init__(self, **options: Any) -> None:
        self.options = options
        self._metadata: PluginMetadata | None = None
        self._search_handlers: list[SearchHandler] = []
        self._results: dict[str, Result] = {}
        self._settings_are_populated: bool = False
        self._last_query: Query | None = None

        self._events: dict[str, Callable[..., Awaitable[Any]]] = get_default_events(
            self
        )
        self.jsonrpc: JsonRPCClient = JsonRPCClient(self)

        for event_name in self.__class_events__:
            self.register_event(getattr(self, event_name))
        for handler in self.__class_search_handlers__:
            setattr(handler.callback, "owner", self)
            self.register_search_handler(handler)

        self.check_for_log_override_files()

    def check_for_log_override_files(self) -> bool | None:
        """None=No-Changes, True=In-Prod, False=In-Debug"""

        if self.options.get("disable_log_override_files"):
            return

        from .utils import _logging_formatter_status

        dir = Path(os.getcwd())

        for _ in dir.glob("*.flogin.debug"):
            if _logging_formatter_status is None:
                setup_logging()
                log.info("Debug file found, logs are now enabled.")
            return False

        for _ in dir.glob("*.flogin.prod"):
            if _logging_formatter_status is not None:
                log.info("Prod file found. Logs are being disabled")
                logger, handler = _logging_formatter_status
                handler.close()
                logger.removeHandler(handler)
            return True

    @property
    def last_query(self) -> Query | None:
        """:class:`~flogin.query.Query` | ``None``: The last query request that flow sent. This is ``None`` if no query request has been sent yet."""
        return self._last_query

    @cached_property
    def api(self) -> FlowLauncherAPI:
        """:class:`~flogin.flow.api.FlowLauncherAPI`: An easy way to acess Flow Launcher's API"""

        return FlowLauncherAPI(self.jsonrpc)

    def _get_env(self, name: str, alternative: str | None = None) -> str:
        try:
            return os.environ[name]
        except KeyError:
            raise EnvNotSet(name, alternative) from None

    @cached_property
    def flow_version(self) -> str:
        """:class:`str`: the flow version from environment variables.

        .. versionadded:: 1.0.1

        Raises
        ------
        :class:`~flogin.errors.EnvNotSet`
            This is raised when the environment variable for this property is not set by flow or the plugin tester.
        """

        return self._get_env("FLOW_VERSION", "flow_version")

    @cached_property
    def flow_application_dir(self) -> Path:
        """:class:`~pathlib.Path`: flow's application directory from environment variables.

        .. versionadded:: 1.0.1

        Raises
        ------
        :class:`~flogin.errors.EnvNotSet`
            This is raised when the environment variable for this property is not set by flow or the plugin tester.
        """

        return Path(self._get_env("FLOW_APPLICATION_DIRECTORY", "flow_application_dir"))

    @cached_property
    def flow_program_dir(self) -> Path:
        """:class:`~pathlib.Path`: flow's application program from environment variables.

        .. versionadded:: 1.0.1

        Raises
        ------
        :class:`~flogin.errors.EnvNotSet`
            This is raised when the environment variable for this property is not set by flow or the plugin tester.
        """

        return Path(self._get_env("FLOW_PROGRAM_DIRECTORY", "flow_program_dir"))

    @cached_property
    def settings(self) -> SettingsT:
        """:class:`~flogin.settings.Settings`: The plugin's settings set by the user"""

        fp = os.path.join(
            "..", "..", "Settings", "Plugins", self.metadata.name, "Settings.json"
        )
        with open(fp) as f:
            data = json.load(f)
        self._settings_are_populated = True
        log.debug("Settings filled from file: %r", data)
        return Settings(data, no_update=self.options.get("settings_no_update", False))  # type: ignore[reportReturnType]

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
            return await error_handler(e)

    def _schedule_event(
        self,
        coro: Callable[..., Awaitable[Any]],
        event_name: str,
        args: Iterable[Any] = MISSING,
        kwargs: dict[str, Any] = MISSING,
        error_handler: Callable[[Exception], Coroutine[Any, Any, Any]] | str = MISSING,
    ) -> asyncio.Task[Any]:
        wrapped = self._run_event(
            coro, event_name, args or [], kwargs or {}, error_handler
        )
        return asyncio.create_task(wrapped, name=f"flogin: {event_name}")

    def dispatch(
        self, event: str, *args: Any, **kwargs: Any
    ) -> None | asyncio.Task[Any]:
        method = f"on_{event}"

        # Special Event Cases
        replacements = {
            "on_initialize": "_initialize_wrapper",
        }
        method = replacements.get(method, method)

        log.debug("Dispatching event %s", method)

        event_callback = self._events.get(method)
        if event_callback:
            return self._schedule_event(event_callback, method, args, kwargs)

    async def _coro_or_gen_to_results(
        self, coro: SearchHandlerCallbackReturns
    ) -> list[Result] | ErrorResponse:
        results: list[Result] = []
        raw_results = await coro_or_gen(coro)

        if raw_results is None:
            return results

        if isinstance(raw_results, ErrorResponse):
            return raw_results
        if not isinstance(raw_results, list):
            raw_results = [raw_results]
        for raw_res in cast("list[ConvertableToResult]", raw_results):
            res = Result.from_anything(raw_res)
            self._results[res.slug] = res
            results.append(res)
        return results

    async def _initialize_wrapper(self, arg: dict[str, Any]) -> ExecuteResponse:
        log.debug("Initialize: %r", arg)
        self._metadata = PluginMetadata(arg["currentPluginMetadata"], self.api)
        self.dispatch("initialization")
        return ExecuteResponse(hide=False)

    async def process_context_menus(
        self, data: list[Any]
    ) -> QueryResponse | ErrorResponse:
        log.debug("Context Menu Handler: data=%r", data)

        results: list[Result]

        if not data:
            results = []
        else:
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
        results: list[Result] = []
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

    async def _action_callback_wrapper(
        self, callback: Callable[[], Awaitable[ExecuteResponse | bool | None]]
    ) -> ExecuteResponse:
        value = await callback()
        if isinstance(value, bool):
            return ExecuteResponse(hide=value)
        if value is None:
            return ExecuteResponse()
        return value

    def process_action(self, method: str) -> asyncio.Task[ExecuteResponse] | None:
        slug = method.removeprefix("flogin.action.")
        result = self._results.get(slug)
        if result is None:
            return

        result.plugin = self
        return self._schedule_event(
            self._action_callback_wrapper,
            method,
            args=[result.callback],
            error_handler=result.on_error,
        )

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

    async def start(self) -> None:
        r"""|coro|

        The default startup/setup method. This can be overriden for advanced startup behavior, but make sure to run ``await super().start()`` to actually start your plugin.
        """

        import aioconsole

        get_standard_streams: Awaitable[tuple[StreamReader, StreamWriter]] = (
            aioconsole.get_standard_streams()  # type: ignore
        )

        reader, writer = await get_standard_streams

        await self.jsonrpc.start_listening(reader, writer)

    def run(self, *, setup_default_log_handler: bool = True) -> None:
        r"""The default runner. This runs the :func:`~flogin.plugin.Plugin.start` coroutine, and setups up logging.

        Parameters
        --------
        setup_default_log_handler: :class:`bool`
            Whether to setup the default log handler or not, defaults to `True`.
        """

        log_status = self.check_for_log_override_files()

        if log_status is None and setup_default_log_handler:
            setup_logging()

        try:
            asyncio.run(self.start())
        except Exception as e:
            log.exception("A fatal error has occurred which crashed flogin", exc_info=e)

    def register_search_handler(self, handler: SearchHandler[Any]) -> None:
        r"""Register a new search handler

        See the :ref:`search handler section <search_handlers>` for more information about using search handlers.

        Parameters
        -----------
        handler: :class:`~flogin.search_handler.SearchHandler`
            The search handler to be registered
        """

        self._search_handlers.append(handler)
        log.debug("Registered search handler: %r", handler)

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

    @classmethod
    def __event_classmethod_deco(cls, callback: EventCallbackT) -> EventCallbackT:
        cls.__class_events__.append(callback.__name__)
        return callback

    @decorator
    @add_classmethod_alt(__event_classmethod_deco)
    def event(self, callback: EventCallbackT) -> EventCallbackT:
        """A decorator that registers an event to listen for. This decorator can be used with a plugin instance or as a classmethod.

        All events must be a :ref:`coroutine <coroutine>`.

        .. versionchanged:: 1.1.0
            The decorator can now be used as a classmethod

        .. NOTE::
            See the :ref:`event reference <events>` to see what valid events there are.

        Example
        ---------

        With a plugin instance:

        .. code-block:: python3

            from flogin.utils import print

            @plugin.event
            async def on_initialization():
                print('Ready!')

        As a classmethod:

        .. code-block:: python3

            from flogin.utils import print

            class MyPlugin(Plugin):
                @Plugin.event
                async def on_initialization(self):
                    print('Ready!')
        """

        self.register_event(callback)
        return callback

    @overload
    @classmethod
    def __handle_search_deco(
        cls,
        registrate: Callable[[SearchHandler], None],
        *,
        add_self: Literal[True],
        condition: SearchHandlerCondition | None = None,
        **kwargs: Any,
    ) -> Callable[[SearchHandlerCallbackWithSelf], SearchHandler]: ...

    @overload
    @classmethod
    def __handle_search_deco(
        cls,
        registrate: Callable[[SearchHandler], None],
        *,
        add_self: Literal[False],
        condition: SearchHandlerCondition | None = None,
        **kwargs: Any,
    ) -> Callable[[SearchHandlerCallback], SearchHandler]: ...

    @classmethod
    def __handle_search_deco(
        cls,
        registrate: Callable[[SearchHandler], None],
        *,
        add_self: bool,
        condition: SearchHandlerCondition | None = None,
        **kwargs: Any,
    ) -> (
        Callable[[SearchHandlerCallbackWithSelf], SearchHandler]
        | Callable[[SearchHandlerCallback], SearchHandler]
    ):
        if condition is None:
            condition = SearchHandler._builtin_condition_kwarg_to_obj(**kwargs)

        def inner(
            func: SearchHandlerCallbackWithSelf | SearchHandlerCallback,
        ) -> SearchHandler:
            handler = SearchHandler()
            if condition:
                setattr(handler, "condition", condition)
            if add_self:
                func = func_with_self(func)  # type: ignore[reportArgumentType]
            setattr(handler, "callback", func)
            registrate(handler)
            return handler

        return inner

    @classmethod
    def __search_classmethod_deco(
        cls,
        condition: SearchHandlerCondition | None = None,
        *,
        text: str = MISSING,
        pattern: re.Pattern[str] | str = MISSING,
        keyword: str = MISSING,
        allowed_keywords: Iterable[str] = MISSING,
        disallowed_keywords: Iterable[str] = MISSING,
    ) -> Callable[[SearchHandlerCallbackWithSelf], SearchHandler]:
        return cls.__handle_search_deco(
            cls.__class_search_handlers__.append,
            add_self=True,
            condition=condition,
            text=text,
            pattern=pattern,
            keyword=keyword,
            allowed_keywords=allowed_keywords,
            disallowed_keywords=disallowed_keywords,
        )

    @decorator
    @add_classmethod_alt(__search_classmethod_deco)
    def search(
        self,
        condition: SearchHandlerCondition | None = None,
        *,
        text: str = MISSING,
        pattern: re.Pattern[str] | str = MISSING,
        keyword: str = MISSING,
        allowed_keywords: Iterable[str] = MISSING,
        disallowed_keywords: Iterable[str] = MISSING,
    ) -> Callable[[SearchHandlerCallback], SearchHandler]:
        """A decorator that registers a search handler.

        All search handlers must be a :ref:`coroutine <coroutine>`. See the :ref:`search handler section <search_handlers>` for more information about using search handlers.

        .. versionchanged:: 2.0.0
            The search decorator can now be used as a classmethod

        .. NOTE::
            This decorator can also be used as a classmethod

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

        With an instance:

        .. code-block:: python3

            @plugin.search()
            async def example_search_handler(data: Query):
                return "This is a result!"

        As a classmethod:

        .. code-block:: python3

            class MyPlugin(Plugin):
                @Plugin.search()
                async def example_search_handler(self, data: Query):
                    return "This is a result!"
        """

        return self.__handle_search_deco(
            self.register_search_handler,
            add_self=False,
            condition=condition,
            text=text,
            pattern=pattern,
            keyword=keyword,
            allowed_keywords=allowed_keywords,
            disallowed_keywords=disallowed_keywords,
        )

    def fetch_flow_settings(self) -> FlowSettings:
        """Fetches flow's settings from flow's config file

        Returns
        --------
        :class:`~flogin.flow.settings.FlowSettings`
            A dataclass containing all of flow's settings
        """

        path = os.path.join("..", "..", "Settings", "Settings.json")
        with open(path) as f:
            data = json.load(f)
        return FlowSettings(data)

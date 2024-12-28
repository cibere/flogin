from __future__ import annotations

import logging
from typing import (
    TYPE_CHECKING,
    Callable,
    Generic,
    TypeVar,
    Unpack,
    TypedDict,
    NotRequired,
    Iterable,
    overload,
)

from ._types import PluginT, SearchHandlerCallbackReturns, SearchHandlerCondition
from .jsonrpc import ErrorResponse
from .utils import copy_doc, MISSING
from .conditions import (
    AllCondition,
    AnyCondition,
    RegexCondition,
    KeywordCondition,
    PlainTextCondition,
)
import re

if TYPE_CHECKING:
    from .query import Query

    ErrorHandlerT = TypeVar(
        "ErrorHandlerT",
        bound=Callable[[Query, Exception], SearchHandlerCallbackReturns],
    )

LOG = logging.getLogger(__name__)

__all__ = ("SearchHandler",)


class SearchHandler(Generic[PluginT]):
    r"""This represents a search handler.

    When creating this on your own, the :func:`~flogin.plugin.Plugin.register_search_handler` method can be used to register it.

    See the :ref:`search handler section <search_handlers>` for more information about using search handlers.

    There is a provided decorator to easily create search handlers: :func:`~flogin.plugin.Plugin.search`

    This class implements a generic for the :attr:`~flogin.search_handler.SearchHandler.plugin` attribute, which will be used for typechecking purposes.

    The keywords in the constructor can also be passed into the subclassed init, like so: ::

        class MyHandler(SearchHandler, text="text"):
            ...

        # is equal to

        class MyHandler(SearchHandler):
            def __init__(self):
                super().__init__(text="text")

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

    Attributes
    ------------
    plugin: :class:`~flogin.plugin.Plugin` | None
        Your plugin instance. This is filled before :func:`~flogin.search_handler.SearchHandler.callback` is triggered.
    """

    @overload
    def __init__(self, condition: SearchHandlerCondition) -> None: ...

    @overload
    def __init__(self, *, text: str) -> None: ...

    @overload
    def __init__(
        self,
        *,
        pattern: re.Pattern | str = MISSING,
    ) -> None: ...

    @overload
    def __init__(
        self,
        *,
        keyword: str = MISSING,
    ) -> None: ...

    @overload
    def __init__(
        self,
        *,
        allowed_keywords: Iterable[str] = MISSING,
    ) -> None: ...

    @overload
    def __init__(
        self,
        *,
        disallowed_keywords: Iterable[str] = MISSING,
    ) -> None: ...

    def __init__(
        self,
        condition: SearchHandlerCondition | None = None,
        *,
        text: str = MISSING,
        pattern: re.Pattern | str = MISSING,
        keyword: str = MISSING,
        allowed_keywords: Iterable[str] = MISSING,
        disallowed_keywords: Iterable[str] = MISSING,
    ) -> None:
        if condition is None:
            condition = self._builtin_condition_kwarg_to_obj(
                text=text,
                pattern=pattern,
                keyword=keyword,
                allowed_keywords=allowed_keywords,
                disallowed_keywords=disallowed_keywords,
            )
        if condition:
            self.condition = condition  # type: ignore

        self.plugin: PluginT | None = None

    @overload
    def __init_subclass__(cls: type[SearchHandler], *, text: str) -> None: ...

    @overload
    def __init_subclass__(
        cls: type[SearchHandler],
        *,
        pattern: re.Pattern | str = MISSING,
    ) -> None: ...

    @overload
    def __init_subclass__(
        cls: type[SearchHandler],
        *,
        keyword: str = MISSING,
    ) -> None: ...

    @overload
    def __init_subclass__(
        cls: type[SearchHandler],
        *,
        allowed_keywords: Iterable[str] = MISSING,
    ) -> None: ...

    @overload
    def __init_subclass__(
        cls: type[SearchHandler],
        *,
        disallowed_keywords: Iterable[str] = MISSING,
    ) -> None: ...

    def __init_subclass__(
        cls: type[SearchHandler],
        *,
        text: str = MISSING,
        pattern: re.Pattern | str = MISSING,
        keyword: str = MISSING,
        allowed_keywords: Iterable[str] = MISSING,
        disallowed_keywords: Iterable[str] = MISSING,
    ) -> None:
        con = cls._builtin_condition_kwarg_to_obj(
            text=text,
            pattern=pattern,
            keyword=keyword,
            allowed_keywords=allowed_keywords,
            disallowed_keywords=disallowed_keywords,
        )
        if con is not None:
            cls.condition = con  # type: ignore

    @classmethod
    def _builtin_condition_kwarg_to_obj(
        cls: type[SearchHandler],
        *,
        text: str = MISSING,
        pattern: re.Pattern | str = MISSING,
        keyword: str = MISSING,
        allowed_keywords: Iterable[str] = MISSING,
        disallowed_keywords: Iterable[str] = MISSING,
    ) -> SearchHandlerCondition | None:
        if text is not MISSING:
            return PlainTextCondition(text)
        elif pattern is not MISSING:
            if isinstance(pattern, str):
                pattern = re.compile(pattern)
            return RegexCondition(pattern)
        elif keyword is not MISSING:
            return KeywordCondition(allowed_keywords=[keyword])
        elif allowed_keywords is not MISSING:
            return KeywordCondition(allowed_keywords=allowed_keywords)
        elif disallowed_keywords is not MISSING:
            return KeywordCondition(disallowed_keywords=disallowed_keywords)

    def condition(self, query: Query) -> bool:
        r"""A function that determines whether or not to fire off this search handler for a given query

        Parameters
        ----------
        query: :class:`~flogin.query.Query`
            The query object for the query request

        Returns
        --------
        :class:`bool`
            Whether or not to fire off this handler for the given query.
        """

        return True

    def callback(self, query: Query) -> SearchHandlerCallbackReturns:
        r"""|coro|

        Override this function to add the search handler behavior you want for the set condition.

        This method can return/yield almost anything, and flogin will convert it into a list of :class:`~flogin.jsonrpc.results.Result` objects before sending it to flow.

        Returns
        -------
        list[:class:`~flogin.jsonrpc.results.Result`] | :class:`~flogin.jsonrpc.results.Result` | str | Any
            A list of results, an results, or something that can be converted into a list of results.

        Yields
        ------
        :class:`~flogin.jsonrpc.results.Result` | str | Any
            A result object or something that can be converted into a result object.
        """
        ...

    def on_error(self, query: Query, error: Exception) -> SearchHandlerCallbackReturns:
        r"""|coro|

        Override this function to add an error response behavior to this handler's callback.

        If the error was handled:
            You can return/yield almost anything, and flogin will convert it into a list of :class:`~flogin.jsonrpc.results.Result` objects before sending it to flow.

        If the error was not handled:
            Return a :class:`~flogin.jsonrpc.responses.ErrorResponse` object

        Parameters
        ----------
        query: :class:`~flogin.query.Query`
            The query that was being handled when the error occured.
        error: :class:`Exception`
            The error that occured

        Returns
        -------
        :class:`~flogin.jsonrpc.responses.ErrorResponse` | list[:class:`~flogin.jsonrpc.results.Result`] | :class:`~flogin.jsonrpc.results.Result` | str | Any
            A list of results, an results, or something that can be converted into a list of results.

        Yields
        ------
        :class:`~flogin.jsonrpc.results.Result` | str | Any
            A result object or something that can be converted into a result object.
        """
        ...

    if not TYPE_CHECKING:

        @copy_doc(callback)
        async def callback(self, query: Query):
            raise RuntimeError("Callback was not overriden")

        @copy_doc(on_error)
        async def on_error(self, query: Query, error: Exception):
            LOG.exception(
                f"Ignoring exception in reuslt callback ({self!r})", exc_info=error
            )
            return ErrorResponse.internal_error(error)

    @property
    def name(self) -> str:
        """:class:`str`: The name of the search handler's callback"""
        return self.callback.__name__

    def error(self, func: ErrorHandlerT) -> ErrorHandlerT:
        """A decorator that registers a error handler for this search handler.

        For more information see :class:`~flogin.search_handler.SearchHandler.on_error`

        Example
        ---------

        .. code-block:: python3

            @plugin.search()
            async def my_hander(query):
                ..

            @my_handler.error
            async def my_error_handler(query, error):
                ...

        """

        self.on_error = func  # type: ignore
        return func

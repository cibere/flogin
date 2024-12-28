from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Callable, Generic, TypeVar

from ._types import PluginT, SearchHandlerCallbackReturns, SearchHandlerCondition
from .jsonrpc import ErrorResponse
from .utils import copy_doc

if TYPE_CHECKING:
    from .query import Query

    ErrorHandlerT = TypeVar(
        "ErrorHandlerT",
        bound=Callable[[Query, Exception], SearchHandlerCallbackReturns],
    )

LOG = logging.getLogger(__name__)

__all__ = ("SearchHandler",)


def _default_condition(q: Query) -> bool:
    return True


class SearchHandler(Generic[PluginT]):
    r"""This represents a search handler.

    When creating this on your own, the :func:`~flogin.plugin.Plugin.register_search_handler` method can be used to register it.

    See the :ref:`search handler section <search_handlers>` for more information about using search handlers.

    There is a provided decorator to easily create search handlers: :func:`~flogin.plugin.Plugin.search`

    This class implements a generic for the :attr:`~flogin.search_handler.SearchHandler.plugin` attribute, which will be used for typechecking purposes.

    Attributes
    ------------
    condition: :ref:`condition <condition_example>`
        A function which is used to determine if this search handler should be used to handle a given query or not
    plugin: :class:`~flogin.plugin.Plugin` | None
        Your plugin instance. This is filled before :func:`~flogin.search_handler.SearchHandler.callback` is triggered.
    """

    def __init__(
        self,
        condition: SearchHandlerCondition | None = None,
    ) -> None:
        if condition is None:
            condition = _default_condition

        self.condition = condition
        self.plugin: PluginT | None = None

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

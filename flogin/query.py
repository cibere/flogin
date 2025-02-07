from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generic, TypedDict, TypeVar

from .utils import MISSING

if TYPE_CHECKING:
    from typing_extensions import TypeVar  # noqa: TC004

    from ._types.search_handlers import PluginT
    from .jsonrpc.results import Result

    ConditionDataT = TypeVar("ConditionDataT", default=Any)

else:
    ConditionDataT = TypeVar("ConditionDataT")

__all__ = ("Query",)


class RawQuery(TypedDict):
    search: str
    rawQuery: str
    isReQuery: bool
    actionKeyword: str


class Query(Generic[ConditionDataT]):
    r"""This class represents the query data sent from flow launcher

    .. container:: operations

        .. describe:: x == y

            Compare the keywords, text, and is_query values of two query objects.

        .. describe:: hash(x)

            Gets the hash of the query's raw text

    Attributes
    ----------
    raw_text: :class:`str`:
        The raw and complete query, which includes the keyword
    is_requery: :class:`bool`
        Whether the query is a requery or not
    text: :class:`str`
        The actual query, excluding any keywords
    keyword: :class:`str`
        The keyword used to initiate the query
    """

    def __init__(self, data: RawQuery, plugin: PluginT) -> None:
        self.__search_condition_data: ConditionDataT | None = None
        self._data = data
        self.plugin = plugin

    @property
    def condition_data(self) -> ConditionDataT | None:
        """:class:`Any` | ``None``: If used in a :class:`~flogin.search_handler.SearchHandler`, this attribute will return any extra data that the condition gave."""
        return self.__search_condition_data

    @condition_data.setter
    def condition_data(self, value: ConditionDataT) -> None:
        self.__search_condition_data = value

    @property
    def is_requery(self) -> bool:
        return self._data["isReQuery"]

    @property
    def keyword(self) -> str:
        return self._data["actionKeyword"] or "*"

    @property
    def raw_text(self) -> str:
        return self._data["rawQuery"]

    @property
    def text(self) -> str:
        return self._data["search"]

    def __eq__(self, other: Any) -> bool:
        return (
            isinstance(other, Query)
            and other.raw_text == self.raw_text
            and other.is_requery == self.is_requery
        )

    def __hash__(self) -> int:
        return hash(self.raw_text)

    def __repr__(self) -> str:
        return f"<Query {self.raw_text=} {self.text=} {self.keyword=} {self.is_requery=} {self.condition_data=}>"

    async def update_results(self, results: list[Result]) -> None:
        r"""|coro|

        Tells flow to change the results shown to the user, using the query from this query object.

        This method provides quick acess to :func:`flogin.flow.api.FlowLauncherAPI.update_results`. Because of that, this method will only take affect if the user has not changed the query.

        Parameters
        ----------
        results: list[:class:`~flogin.jsonrpc.results.Result`]
            The new results

        Raises
        -------
        :class:`~flogin.jsonrpc.errors.JsonRPCException`
            This is raised when an error happens with the JsonRPC pipe while attempting to call this API method.

        Returns
        -------
        ``None``
        """

        return await self.plugin.api.update_results(self.raw_text, results)

    async def update(
        self,
        *,
        text: str | None = MISSING,
        keyword: str | None = MISSING,
        requery: bool = False,
    ) -> None:
        r"""|coro|

        Applies updates to the query with flow, and to this object.

        This method provides quick access to :func:`flogin.flow.api.FlowLauncherAPI.change_query`

        Parameters
        ----------
        text: Optional[:class:`str` | ``None``]
            The text that will be used with the query.

            .. versionchanged:: 2.0.0
                ``text`` can now be ``None``, and is now optional
        keyword: Optional[:class:`str` | ``None``]
            The keyword that will be used with the query. Defaults to the pre-existing value of :attr:`Query.keyword`. Set this to ``None`` or ``*`` for no keyword to be used.
        requery: Optional[:class:`bool`]
            Whether or not to re-send a query request in the event that the new query is the same as the current query. Defaults to ``False``

        Raises
        -------
        :class:`~flogin.jsonrpc.errors.JsonRPCException`
            This is raised when an error happens with the JsonRPC pipe while attempting to call this API method.

        Returns
        --------
        ``None``
        """

        if keyword is not MISSING:
            self._data["actionKeyword"] = "*" if keyword is None else keyword

        if text is not MISSING:
            self._data["search"] = text or ""

        self._data["rawQuery"] = (
            f"{'' if self.keyword == '*' else self.keyword} {self.text}".strip()
        )

        return await self.plugin.api.change_query(self.raw_text, requery=requery)

    async def back_to_query_results(self) -> None:
        r"""|coro|
        
        This coroutine tells flow to exit the context menu and go back to the query results.

        This method provides quick access to :meth:`flogin.flow.api.FlowLauncherAPI.back_to_query_results`

        .. versionadded:: 2.0.0
        
        Raises
        -------
        :class:`~flogin.jsonrpc.errors.JsonRPCException`
            This is raised when an error happens with the JsonRPC pipe while attempting to call this API method.

        Returns
        --------
        ``None``
        """

        await self.plugin.api.back_to_query_results()
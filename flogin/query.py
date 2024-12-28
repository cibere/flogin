from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generic, TypedDict, TypeVar

from ._types import PluginT
from .utils import MISSING

if TYPE_CHECKING:
    from .jsonrpc.results import Result

T = TypeVar("T")

__all__ = ("Query",)


class RawQuery(TypedDict):
    search: str
    rawQuery: str
    isReQuery: bool
    actionKeyword: str


class Query(Generic[T]):
    r"""This class represents the query data sent from flow launcher

    This class implements a generic for the :attr:`~flogin.query.Query.condition_data` attribute, which will be used for typechecking purposes.

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
        self.__search_condition_data: T | None = None
        self._data = data
        self.plugin = plugin

    @property
    def condition_data(self) -> T | None:
        """Any | None: If used in a :class:`~flogin.search_handler.SearchHandler`, this attribute will return any extra data that the condition gave."""
        return self.__search_condition_data

    @condition_data.setter
    def condition_data(self, value: T) -> None:
        self.__search_condition_data = value

    @property
    def is_requery(self) -> bool:
        return self._data["isReQuery"]

    @property
    def keyword(self) -> str:
        return self._data["actionKeyword"]

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

        Returns
        -------
        None
        """

        return await self.plugin.api.update_results(self.raw_text, results)

    async def update(
        self, *, text: str, keyword: str | None = MISSING, requery: bool = False
    ) -> None:
        r"""|coro|

        Applies updates to the query with flow, and to this object.

        This method provides quick acess to :func:`flogin.flow.api.FlowLauncherAPI.change_query`

        Parameters
        ----------
        text: :class:`str`
            The text that will be used with the query.
        keyword: :class:`str`
            The keyword that will be used with the query. Defaults to the pre-existing value of :attr:`Query.keyword`. Set this to ``None`` or `"*"` for no keyword to be used.
        requery: :class:`bool`
            Whether or not to re-send a query request in the event that the new query is the same as the current query

        Returns
        --------
        None
        """

        if keyword is MISSING:
            keyword = self.keyword

        if keyword is None or keyword == "*":
            raw_text = text
            self._data["actionKeyword"] = "*"
        else:
            raw_text = f"{keyword} {text}"
            self._data["actionKeyword"] = keyword

        self._data["rawQuery"] = raw_text
        self._data["search"] = text
        self._data["isReQuery"] = requery

        return await self.plugin.api.change_query(raw_text, requery=requery)

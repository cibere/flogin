from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generic, Self

from ._types import (
    PluginT,
    SearchHandlerCallback,
    SearchHandlerCallbackReturns,
)
from .jsonrpc.results import Result
from .search_handler import SearchHandler
from .utils import (
    MISSING,
    decorator,
)

if TYPE_CHECKING:
    from .query import Query

__all__ = ("SearchGroup",)


class SearchGroup(SearchHandler[PluginT], Generic[PluginT]):
    r"""A subclass of :class:`~flogin.search_handler.SearchHandler` to let you easily create a nested command structure.

    The keywords in the constructor can also be passed into the subclassed init, like so: ::

        class MyGroup(SearchGroup, prefix="text"):
            ...

        # is equal to

        class MyGroup(SearchGroup):
            def __init__(self):
                super().__init__(prefix="text")

    .. versionadded:: 2.0.0

    Example
    -------
    Adding a subcommand named ``cmd``

    .. code-block:: py3
        :linenos:

        from flogin import SearchGroup

        group = SearchGroup("foo")

        @group.sub("cmd")
        async def cmd(query):
            return "Hi from cmd"

        # cmd can be invoked with "foo cmd"

    Adding nested subgroups

    .. code-block:: py3
        :linenos:

        from flogin import SearchGroup

        group = SearchGroup("foo")
        sub = group.sub("sub")

        @sub.sub("cmd2")
        async def cmd2(query):
            return "Hi from cmd2 under cmd1"

        # cmd2 can be invoked with "foo sub cmd2"

    Attributes
    ----------
    prefix: :class:`str`
        The prefix used to trigger the search group
    sep: :class:`str`
        The character that seperates the group's prefix and subhandler's prefixes during validation. Defaults to a space.
    """

    prefix: str
    sep: str = " "

    def __init__(self, prefix: str = MISSING, sep: str = MISSING) -> None:
        if prefix is not MISSING:
            self.prefix = prefix
        else:
            if not hasattr(self, "prefix"):
                raise ValueError(
                    "Prefix arg must be provided in __init__ or __init_subclass__"
                )
        if sep is not MISSING:
            self.sep = sep

        self.parent: SearchGroup | None = None
        self._subgroups: dict[str, SearchGroup] = {}

    def __init_subclass__(cls, prefix: str = MISSING, sep: str = MISSING) -> None:
        cls.prefix = prefix
        cls.sep = " " if sep is MISSING else sep

    def condition(self, query: Query) -> bool:
        try:
            return f"{query.text}{self.sep}".startswith(f"{self.prefix}{self.sep}")
        except IndexError:
            return False

    @property
    def subgroups(self) -> dict[str, SearchGroup]:
        r"""dict[:class:`str`, :class:`~flogin.search_group.SearchGroup`]: A copied version of the subgroups that have been registered to this group."""
        return self._subgroups.copy()

    @property
    def signature(self) -> str:
        r""":class:`str` the group's signature. This property will grab all of the group's parent's prefixes, and join them together using the :attr:`~flogin.search_group.SearchGroup.sep` attribute"""

        parts = []
        parent = self

        while parent:
            parts.append(parent.prefix)
            parent = parent.parent
        return self.sep.join(reversed(parts))

    def create_result(self, key: str, query: Query) -> Result:
        r"""This is a method that is used by the default root callback and can be overriden.

        It is used to turn the key of one of the subhandlers into a result object that is returned. The default result that is returned has the title set to the key, with the ``auto_complete_text`` and callback set to properly change the query to trigger the subhander.

        Parameters
        ----------
        key: :class:`str`
            The key to generate the result for
        query: :class:`~flogin.query.Query`
            The query that this is being generated for

        Returns
        -------
        :class:`~flogin.jsonrpc.results.Result`
            The generated result object
        """

        assert self.plugin
        assert self.plugin.last_query

        new = f"{self.plugin.last_query.keyword} {self.signature}{self.sep}{key}{self.sep}"

        async def callback() -> bool:
            assert self.plugin

            await self.plugin.api.change_query(new)
            return False

        return Result.create_with_partial(
            callback,
            title=key,
            auto_complete_text=new,
        )

    async def root_handler(self, query: Query) -> list[Result]:
        return [self.create_result(key, query) for key in self._subgroups]

    def callback(self, query: Query) -> SearchHandlerCallbackReturns:
        parts = query.text.split(self.sep)
        query._data["search"] = query.text.removeprefix(self.prefix).removeprefix(
            self.sep
        )

        try:
            handler = self._subgroups[parts[1]]
        except (KeyError, IndexError):
            handler = self.root_handler

        if isinstance(handler, SearchGroup):
            handler.plugin = self.plugin
            handler = handler.callback

        return handler(query)

    def __call__(self, callback: SearchHandlerCallback) -> Self:
        setattr(self, "root_handler", callback)
        return self

    @decorator(is_factory=True)
    def sub(self, prefix: str) -> SearchGroup:
        r"""Adds a subgroup to the search group.

        Parameters
        ----------
        prefix: :class:`str`
            The prefix used to trigger the subgroup

        Raises
        ------
        :class:`ValueError`
            This is raised when the given prefix is already associated with a subgroup.

        Example
        -------
        .. code-block:: py3
            :linenos:

            group = SearchGroup(...)

            @group.sub("prefix")
            async def subgroup(query):
                ...
        """

        if prefix in self._subgroups:
            raise ValueError(
                f"A subgroup with the {prefix!r} prefix has already been registered"
            )

        group = SearchGroup(prefix, self.sep)
        group.parent = self
        self._subgroups[prefix] = group
        return group

    def get_tree(self) -> dict[str, Any]:
        return {
            "prefix": self.prefix,
            "children": {
                name: value.get_tree()
                if isinstance(value, SearchGroup)
                else repr(value)
                for name, value in self._subgroups.items()
            },
        }

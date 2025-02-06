from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar, Generic, Self, TypeVar

from ._types import (
    PluginT,
    SearchHandlerCallback,
    SearchHandlerCallbackReturns,
    SearchHandlerCallbackWithSelf,
)
from .jsonrpc.results import Result
from .search_handler import SearchHandler
from .utils import (
    MISSING,
    add_classmethod_alt,
    decorator,
    func_with_self,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from .query import Query

SearchHandlerCallbackT = TypeVar("SearchHandlerCallbackT", bound=SearchHandlerCallback)
SearchHandlerCallbackWithSelfT = TypeVar(
    "SearchHandlerCallbackWithSelfT", bound=SearchHandlerCallbackWithSelf
)

__all__ = ("SearchGroup",)


class SearchGroup(SearchHandler[PluginT], Generic[PluginT]):
    prefix: str
    sep: str = " "
    __class_subhandlers__: ClassVar[
        dict[str, SearchHandlerCallbackWithSelf | SearchGroup]
    ] = {}

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
        self._subhandlers: dict[str, SearchHandlerCallback | SearchGroup] = {}

        for key, func in self.__class_subhandlers__.items():
            if isinstance(func, SearchGroup):
                func.parent = self
            else:
                func = func_with_self(func, owner=self)
            self._subhandlers[key] = func

    def __init_subclass__(cls, prefix: str = MISSING, sep: str = MISSING) -> None:
        cls.__class_subhandlers__ = {}
        cls.prefix = prefix
        cls.sep = " " if sep is MISSING else sep

    def condition(self, query: Query) -> bool:
        try:
            return f"{query.text}{self.sep}".startswith(f"{self.prefix}{self.sep}")
        except IndexError:
            return False

    @property
    def signature(self) -> str:
        r""":class:`str` the group's signature. This property will grab all of the group's parent's prefixes, and join them together using :attr:`SearchGroup.sep`"""

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
        query: :class:`Query`
            The query that this is being generated for

        Returns
        -------
        :class:`Result`
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

    async def _default_root_handler(self, query: Query) -> list[Result]:
        return [self.create_result(key, query) for key in self._subhandlers]

    def callback(self, query: Query) -> SearchHandlerCallbackReturns:
        parts = query.text.split(self.sep)
        query._data["search"] = query.text.removeprefix(self.prefix).removeprefix(
            self.sep
        )

        try:
            handler = self._subhandlers[parts[1]]
        except (KeyError, IndexError):
            handler = self._subhandlers.get("", self._default_root_handler)

        if isinstance(handler, SearchGroup):
            handler.plugin = self.plugin
            handler = handler.callback

        return handler(query)

    def __call__(self, callback: SearchHandlerCallback) -> Self:
        self._subhandlers[""] = callback
        return self

    @classmethod
    def __subhandler_classmethod_deco(
        cls, prefix: str
    ) -> Callable[[SearchHandlerCallbackWithSelf], SearchHandlerCallbackWithSelf]:
        def deco(
            func: SearchHandlerCallbackWithSelfT,
        ) -> SearchHandlerCallbackWithSelfT:
            cls.__class_subhandlers__[prefix] = func
            return func

        return deco

    @decorator(is_factory=True)
    @add_classmethod_alt(__subhandler_classmethod_deco)
    def subhandler(
        self, prefix: str
    ) -> Callable[[SearchHandlerCallbackT], SearchHandlerCallbackT]:
        r"""Adds a subhandler to the search group.

        .. NOTE::
            This can also be used as a classmethod

        Parameters
        ----------
        prefix: :class:`str`
            The prefix used to trigger the subhandler

        Example
        -------
        .. details:: Using with an instance

            .. code-block:: py3
                :linenos:

                group = SearchGroup(...)

                @group.subhandler("prefix")
                async def subhandler(query):
                    ...

        .. details:: Using as a classmethod

            .. code-block:: py3
                :linenos:

                class MyHandler(SearchHandler):
                    @SearchGroup.subhandler("prefix")
                    async def subhandler(self, query):
                        ...
        """

        def deco(func: SearchHandlerCallbackT) -> SearchHandlerCallbackT:
            self._subhandlers[prefix] = func
            return func

        return deco

    def subgroup(self, prefix: str) -> SearchGroup:
        r"""Creates a subgroup with the given prefix.

        Parameters
        ----------
        prefix: :class:`str`
            The prefix to attach to the new subgroup

        Example
        -------
        .. details:: Using the default root callback

            .. code-block:: py3
                :linenos:

                group = SearchGroup(...)
                subgroup = group.subgroup("prefix")

        .. details:: With a custom root callback

            .. code-block:: py3
                :linenos:

                group = SearchGroup(...)

                @group.subgroup("prefix")
                async def custom_root_callback(query: Query):
                    ...

        Returns
        -------
        :class:`SearchGroup`
        """

        group = SearchGroup(prefix, self.sep)
        group.parent = self
        self._subhandlers[prefix] = group
        return group

    def get_tree(self) -> dict[str, Any]:
        return {
            "prefix": self.prefix,
            "children": {
                name: value.get_tree()
                if isinstance(value, SearchGroup)
                else repr(value)
                for name, value in self._subhandlers.items()
            },
        }

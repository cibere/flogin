from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar

if TYPE_CHECKING:
    from collections.abc import AsyncIterable, Callable, Coroutine, Iterable

    from typing_extensions import Protocol, TypeVar  # noqa: TC004

    from ..jsonrpc.results import Result as _Result
    from ..plugin import Plugin
    from ..query import Query
    from .jsonrpc.result import RawResult

    class StringCastable(Protocol):
        def __str__(self) -> str: ...

    PluginT = TypeVar("PluginT", bound=Plugin[Any], default=Plugin[Any], covariant=True)
    T = TypeVar("T", default=Any)

    ConvertableToResult = str | int | RawResult | StringCastable | _Result[PluginT]
    ConvertableToResults = ConvertableToResult | Iterable[ConvertableToResult]
    SearchHandlerCallbackReturns = (
        Coroutine[Any, Any, ConvertableToResults] | AsyncIterable[ConvertableToResults]
    )
    SearchHandlerCallback = Callable[[Query[T]], SearchHandlerCallbackReturns]
    SearchHandlerCallbackWithSelf = Callable[
        [Any, Query[T]], SearchHandlerCallbackReturns
    ]
    SearchHandlerCondition = Callable[[Query[T]], bool]
else:
    ConvertableToResult = ConvertableToResults = SearchHandlerCallbackReturns = (
        SearchHandlerCallback
    ) = SearchHandlerCallbackWithSelf = SearchHandlerCondition = Any
    PluginT = TypeVar("PluginT")

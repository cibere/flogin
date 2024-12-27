from __future__ import annotations

from typing import TYPE_CHECKING, Any, AsyncIterable, Callable, Coroutine, TypeVar

if TYPE_CHECKING:
    from typing_extensions import TypeVar

    from .plugin import Plugin
    from .query import Query

    PluginT = TypeVar("PluginT", bound=Plugin[Any], default=Plugin[Any], covariant=True)
else:
    Query = Any
    PluginT = TypeVar("PluginT")

SearchHandlerCallbackReturns = Coroutine[Any, Any, Any] | AsyncIterable[Any]
SearchHandlerCallback = Callable[[Query], SearchHandlerCallbackReturns]
SearchHandlerCondition = Callable[[Query], bool]
RawSettings = dict[str, Any]

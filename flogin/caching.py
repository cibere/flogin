from __future__ import annotations
import logging
import logging.handlers
from functools import _make_key as make_cached_key
from typing import (
    TYPE_CHECKING,
    Any,
    AsyncGenerator,
    Awaitable,
    Callable,
    Coroutine,
    TypeVar,
    overload,
)
from .utils import coro_or_gen, MISSING

Coro = TypeVar("Coro", bound=Callable[..., Coroutine[Any, Any, Any]])
AGenT = TypeVar("AGenT", bound=Callable[..., AsyncGenerator[Any, Any]])
T = TypeVar("T")

LOG = logging.getLogger(__name__)


class _cached_property:
    def __init__(self, function) -> None:
        self.function = function
        self.__doc__ = getattr(function, "__doc__")

    def __get__(self, instance, owner):
        if instance is None:
            return self

        value = self.function(instance)
        setattr(instance, self.function.__name__, value)

        return value


if TYPE_CHECKING:
    from functools import cached_property as cached_property
else:
    cached_property = _cached_property

__all__ = ("cached_property", "cached_coro", "cached_gen", "clear_cache")
from collections import defaultdict

__cached_objects__: defaultdict[Any, list[BaseCachedObject]] = defaultdict(list)


def clear_cache(key: str | None = MISSING) -> None:
    if key is MISSING:
        items = []
        for section in __cached_objects__.values():
            items.extend(section)
    else:
        items = __cached_objects__[key]

    for cached_obj in items:
        cached_obj.cache.clear()


class BaseCachedObject:
    def __init__(self, obj: Callable, name: str | None = None) -> None:
        self.obj = obj
        self.name = name or obj.__name__
        self.cache = {}
        __cached_objects__[name].append(self)

    def __call__(self, *args, **kwargs):
        key = make_cached_key(args, kwargs, False)
        return self.call(key, args, kwargs)

    def call(self, key, args, kwargs):
        raise NotImplementedError


class CachedCoro(BaseCachedObject):
    async def call(self, key, args, kwargs):
        try:
            return self.cache[key]
        except KeyError:
            self.cache[key] = await coro_or_gen(self.obj(*args, **kwargs))
            return self.cache[key]


class CachedGen(BaseCachedObject):
    async def call(self, key, args, kwargs):
        try:
            for item in self.cache[key]:
                yield item
        except KeyError:
            self.cache[key] = await coro_or_gen(self.obj(*args, **kwargs))
            for item in self.cache[key]:
                yield item


def _cached_deco(cls: type[BaseCachedObject]):
    def deco(obj: str | Callable | None = None):
        if isinstance(obj, str) or obj is None:

            def inner(obj2: Callable):
                return cls(obj2, obj)

            return inner
        else:
            return cls(obj)

    return deco


if TYPE_CHECKING:
    T = TypeVar("T")
    CallableT = TypeVar("CallableT", bound=Callable[..., Awaitable[Any]])

    @overload
    def cached_coro(obj: str | None = None) -> Callable[[T], T]: ...

    @overload
    def cached_coro(obj: CallableT) -> CallableT: ...

    def cached_coro(obj: str | Callable | None = None) -> Any: ...

else:
    cached_coro = _cached_deco(CachedCoro)

if TYPE_CHECKING:
    T = TypeVar("T")
    GenT = TypeVar("GenT", bound=Callable[..., AsyncGenerator[Any, Any]])

    @overload
    def cached_gen(obj: str | None = None) -> Callable[[T], T]: ...

    @overload
    def cached_gen(obj: GenT) -> GenT: ...

    def cached_gen(obj: str | Callable | None = None) -> Any: ...

else:
    cached_gen = _cached_deco(CachedGen)

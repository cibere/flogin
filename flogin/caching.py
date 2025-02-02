# ruff: noqa: ANN001, ANN002, ANN003, ANN202

from __future__ import annotations

from collections import defaultdict
from collections.abc import (
    AsyncGenerator,
    AsyncIterator,
    Awaitable,
    Callable,
    Coroutine,
    Hashable,
)
from functools import _make_key as make_cached_key
from typing import (
    TYPE_CHECKING,
    Any,
    Generic,
    ParamSpec,
    Self,
    TypeVar,
    overload,
)

from .utils import MISSING, decorator

Coro = TypeVar("Coro", bound=Callable[..., Coroutine[Any, Any, Any]])
AGenT = TypeVar("AGenT", bound=Callable[..., AsyncGenerator[Any, Any]])

if TYPE_CHECKING:
    from typing_extensions import ParamSpec, TypeVar  # noqa: TC004

    T = TypeVar("T", default=Any)
    RT = TypeVar("RT", default=Any)
    CT = TypeVar("CT", default=Any)
    P = ParamSpec("P", default=...)
else:
    T = TypeVar("T")
    RT = TypeVar("RT")
    CT = TypeVar("CT")
    P = ParamSpec("P")


__all__ = (
    "cached_callable",
    "cached_coro",
    "cached_gen",
    "cached_property",
    "clear_cache",
)

__cached_objects__: defaultdict[Any, list[BaseCachedObject]] = defaultdict(list)


def clear_cache(key: str | None = MISSING) -> None:
    r"""This function is used to clear the cache of items that have been cached with this module.

    The caching decorators provide an optional positional argument that acts as a ``name`` argument, which is used in combination of this function.

    Parameters
    ----------
    key: Optional[:class:`str` | ``None``]
        If :class:`str` is passed, every cached item with a name equal to ``key`` will have their cache cleared. If ``None`` is passed, every cached item with a name equal to ``None`` will have their cache cleared (default value for a cached item's name is ``None``). Lastly, if the ``key`` parameter is not passed at all, all caches will be cleared.
    """

    if key is MISSING:
        items: list[BaseCachedObject] = []
        for section in __cached_objects__.values():
            items.extend(section)
    else:
        items = __cached_objects__[key]

    for cached_obj in items:
        cached_obj.clear_cache()


class BaseCachedObject(Generic[RT, CT, P]):
    def __init__(self, obj: Callable[P, RT], name: str | None = None) -> None:
        self.obj = obj
        self.name = name or obj.__name__
        self.cache: dict[Hashable, CT] = {}
        __cached_objects__[name].append(self)

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> RT:
        key = make_cached_key(args, kwargs, False)
        return self.call(key, *args, **kwargs)

    def call(self, key: Hashable, *args: P.args, **kwargs: P.kwargs) -> RT:
        raise NotImplementedError

    def clear_cache(self) -> None:
        self.cache.clear()


class CachedCoro(BaseCachedObject[Awaitable[T], T, P], Generic[T, P]):
    async def call(self, key: Hashable, *args: P.args, **kwargs: P.kwargs):
        try:
            return self.cache[key]
        except KeyError:
            self.cache[key] = await self.obj(*args, **kwargs)
            return self.cache[key]


class CachedGen(BaseCachedObject[AsyncIterator[T], list[T], P], Generic[T, P]):
    async def call(self, key: Hashable, *args: P.args, **kwargs: P.kwargs):
        try:
            for item in self.cache[key]:
                yield item
        except KeyError:
            self.cache[key] = [val async for val in self.obj(*args, **kwargs)]
            for item in self.cache[key]:
                yield item


class CachedProperty(BaseCachedObject, Generic[T]):
    value: T

    @overload
    def __get__(self, instance: None, owner: type[Any] | None = None) -> Self: ...

    @overload
    def __get__(self, instance: object, owner: type[Any] | None = None) -> T: ...

    def __get__(
        self, instance: object | None, owner: type[Any] | None = None
    ) -> T | Self:
        if instance is None:
            return self

        try:
            return self.value
        except AttributeError:
            self.value = self.obj(instance)
            return self.value

    def clear_cache(self):
        try:
            del self.value
        except AttributeError:
            pass


class CachedCallable(BaseCachedObject[T, T, P], Generic[T, P]):
    def call(self, key: Hashable, *args: P.args, **kwargs: P.kwargs):
        try:
            return self.cache[key]
        except KeyError:
            self.cache[key] = self.obj(*args, **kwargs)
            return self.cache[key]


def _cached_deco(cls: type[BaseCachedObject], doc: str | None = None):
    def inner(obj: str | Callable[..., Any] | None = None):
        if isinstance(obj, str) or obj is None:

            def inner(obj2: Callable[..., Any]):
                return cls(obj2, obj)

            return inner
        return cls(obj)

    inner.__doc__ = doc
    return decorator(inner)


CoroT = TypeVar("CoroT", bound=Callable[..., Awaitable[Any]])
GenT = TypeVar("GenT", bound=Callable[..., AsyncGenerator[Any, Any]])
CallableT = TypeVar("CallableT", bound=Callable[..., Any])


@overload
def cached_coro(obj: str | None = None) -> Callable[[CoroT], CoroT]: ...


@overload
def cached_coro(obj: CoroT) -> CoroT: ...


@decorator
def cached_coro(obj: str | None | CoroT = None) -> Callable[[CoroT], CoroT] | CoroT:
    r"""A decorator to cache a coroutine's contents based on the passed arguments. This decorator can also be called with the optional positional argument acting as a ``name`` argument. This is useful when using :func:`~flogin.caching.clear_cache` as it lets you choose which items you want to clear the cache of.

    .. NOTE::
        The arguments passed to the coroutine must be hashable.

    Example
    --------
    .. code-block:: python3

        @plugin.search()
        @cached_coro
        async def handler(query):
            ...

    .. code-block:: python3

        @plugin.search()
        @cached_coro("search-handler")
        async def handler(query):
            ...
    """
    ...  # cov: skip


@overload
def cached_gen(obj: str | None = None) -> Callable[[GenT], GenT]: ...


@overload
def cached_gen(obj: GenT) -> GenT: ...


@decorator
def cached_gen(obj: str | GenT | None = None) -> Callable[[GenT], GenT] | GenT:
    r"""A decorator to cache the contents of an async generator based on the passed arguments. This decorator can also be called with the optional positional argument acting as a ``name`` argument. This is useful when using :func:`~flogin.caching.clear_cache` as it lets you choose which items you want to clear the cache of.

    .. NOTE::
        The arguments passed to the generator must be hashable.

    Example
    --------
    .. code-block:: python3

        @plugin.search()
        .cached_gen
        async def handler(query):
            ...

    .. code-block:: python3

        @plugin.search()
        @cached_gen("search-handler")
        async def handler(query):
            ...
    """
    ...  # cov: skip


@overload
def cached_property(
    obj: str | None = None,
) -> Callable[[Callable[[Any], T]], CachedProperty[T]]: ...


@overload
def cached_property(obj: Callable[[Any], T]) -> CachedProperty[T]: ...


@decorator
def cached_property(
    obj: str | Callable[[Any], T] | None = None,
) -> Callable[[Callable[[Any], T]], CachedProperty[T]] | CachedProperty[T]:
    r"""A decorator that is similar to the builtin `functools.cached_property <https://docs.python.org/3/library/functools.html#functools.cached_property>`__ decorator, but is async-safe and implements the ability to use :func:`~flogin.caching.clear_cache`.

    This decorator can also be called with the optional positional argument acting as a ``name`` argument. This is useful when using :func:`~flogin.caching.clear_cache` as it lets you choose which items you want to clear the cache of.

    Example
    --------
    .. code-block:: python3

        class X:
            @cached_property
            def test(self):
                ...

    .. code-block:: python3

        class X:
            @cached_property("test_prop")
            def test(self):
                ...
    """

    return _cached_deco(CachedProperty)(obj)  # type: ignore[reportReturnType]


@overload
def cached_callable(obj: str | None = None) -> Callable[[CallableT], CallableT]: ...


@overload
def cached_callable(obj: CallableT) -> CallableT: ...


@decorator
def cached_callable(
    obj: str | CallableT | None = None,
) -> CallableT | Callable[[CallableT], CallableT]:
    r"""A decorator to cache a callable's output based on the passed arguments. This decorator can also be called with the optional positional argument acting as a ``name`` argument. This is useful when using :func:`~flogin.caching.clear_cache` as it lets you choose which items you want to clear the cache of.

    .. NOTE::
        The arguments passed to the callable must be hashable.

    Example
    --------
    .. code-block:: python3

        @cached_callable
        def foo(bar):
            ...

    .. code-block:: python3

        @cached_callable("search-handler")
        def foo(bar):
            ...
    """
    ...  # cov: skip


if not TYPE_CHECKING:
    cached_coro = _cached_deco(CachedCoro, cached_coro.__doc__)
    cached_gen = _cached_deco(CachedGen, cached_gen.__doc__)
    cached_callable = _cached_deco(CachedCallable, cached_callable.__doc__)

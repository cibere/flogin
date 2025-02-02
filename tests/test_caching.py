# pyright: basic

import secrets
from collections.abc import AsyncGenerator, AsyncIterator, Callable
from typing import Any, Protocol

import pytest

from flogin import caching


class RandomHexFunc(Protocol):
    def __call__(self, size: int = 16) -> str: ...


def random_hex(size: int = 16):
    return secrets.token_hex(size)


class TestCachedCallable:
    @pytest.fixture(
        params=[
            (None, random_hex),
            ("some-name", random_hex),
        ]
    )
    def cached_callable(self, request: pytest.FixtureRequest):
        return caching.cached_callable(request.param[0])(request.param[1])

    def test_storage(self, cached_callable: RandomHexFunc) -> None:
        assert cached_callable() == cached_callable()
        assert cached_callable(5) != cached_callable()
        assert cached_callable(5) == cached_callable(5)

    def test_clear(self, cached_callable: RandomHexFunc) -> None:
        before = cached_callable()

        assert before == cached_callable()
        caching.clear_cache()
        assert before != cached_callable()


class PropertyClassTester(Protocol):
    foo: caching.CachedProperty[str]


class TestCachedProperty:
    @pytest.fixture(params=[0, 1])
    def cached_property_class(
        self, request: pytest.FixtureRequest
    ) -> type[PropertyClassTester]:
        class BlankTest:
            @caching.cached_property
            def foo(self) -> str:
                return random_hex()

        class NamedTest:
            @caching.cached_property("boo")
            def foo(self) -> str:
                return random_hex()

        return [BlankTest, NamedTest][request.param]

    def test_storage(self, cached_property_class: type[PropertyClassTester]) -> None:
        assert cached_property_class.foo == cached_property_class.foo
        instance = cached_property_class()
        assert instance.foo == instance.foo

    def test_clear(self, cached_property_class: type[PropertyClassTester]) -> None:
        instance = cached_property_class()
        before = instance.foo
        assert before == instance.foo
        caching.clear_cache()
        assert before != instance.foo


class RandomHexCoro(Protocol):
    async def __call__(self, size: int = 16) -> str: ...


async def random_hex_coro(size: int = 16) -> str:
    return random_hex(size)


class TestCachedCoro:
    @pytest.fixture(
        params=[
            (None, random_hex_coro),
            ("some-name", random_hex_coro),
        ]
    )
    def cached_coro(self, request: pytest.FixtureRequest) -> RandomHexCoro:
        return caching.cached_coro(request.param[0])(request.param[1])

    @pytest.mark.asyncio
    async def test_storage(self, cached_coro: RandomHexCoro) -> None:
        assert await cached_coro() == await cached_coro()
        assert await cached_coro(5) != await cached_coro()
        assert await cached_coro(5) == await cached_coro(5)

    @pytest.mark.asyncio
    async def test_clear(self, cached_coro: RandomHexCoro) -> None:
        before = await cached_coro()

        assert before == await cached_coro()
        caching.clear_cache()
        assert before != await cached_coro()


class RandomHexGen(Protocol):
    def __call__(self, size: int = 16) -> AsyncIterator[str]: ...


async def random_hex_gen(size: int = 16) -> AsyncGenerator[str, Any]:
    for char in random_hex(size):
        yield char


class TestCachedGen:
    @pytest.fixture(
        params=[
            (None, random_hex_gen),
            ("some-name", random_hex_gen),
        ]
    )
    def cached_gen(self, request: pytest.FixtureRequest) -> RandomHexGen:
        return caching.cached_gen(request.param[0])(request.param[1])

    async def flatten(self, gen: AsyncIterator[str]) -> str:
        return "".join([x async for x in gen])

    @pytest.mark.asyncio
    async def test_storage(self, cached_gen: RandomHexGen) -> None:
        assert await self.flatten(cached_gen()) == await self.flatten(cached_gen())
        assert await self.flatten(cached_gen(5)) != await self.flatten(cached_gen())
        assert await self.flatten(cached_gen(5)) == await self.flatten(cached_gen(5))

    @pytest.mark.asyncio
    async def test_clear(self, cached_gen: RandomHexGen) -> None:
        before = await self.flatten(cached_gen())

        assert before == await self.flatten(cached_gen())
        caching.clear_cache()
        assert before != await self.flatten(cached_gen())


class TestClearCache:
    @pytest.fixture(scope="class")
    def named_cached_callable(self) -> Callable[[], str]:
        @caching.cached_callable("test")
        def func():
            return random_hex()

        return func

    def test_named(self, named_cached_callable: Callable[[], str]) -> None:
        before = named_cached_callable()
        assert before == named_cached_callable()

        caching.clear_cache("something else")
        assert before == named_cached_callable()

        caching.clear_cache("test")
        assert before != named_cached_callable()

    def test_global(self, named_cached_callable: Callable[[], str]) -> None:
        before = named_cached_callable()
        assert before == named_cached_callable()

        caching.clear_cache()
        assert before != named_cached_callable()

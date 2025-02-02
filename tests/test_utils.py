# pyright: basic

import asyncio
import logging
import logging.handlers
import random
from collections.abc import AsyncIterator, Awaitable, Callable
from typing import Self

import pytest
import pytest_asyncio

from flogin import utils


@pytest.fixture
def rand_func() -> Callable[[], int]:
    return lambda: random.randint(0, 100)  # nosec


def test_cached_property(rand_func: Callable[[], int]) -> None:
    class Test:
        @utils.cached_property
        def prop(self):
            return rand_func()

    test = Test()
    assert test.prop == test.prop
    assert isinstance(Test.prop, utils.cached_property)


def test_copy_doc() -> None:
    def orig():
        """this is a test"""

    @utils.copy_doc(orig)
    def new(): ...

    assert orig.__doc__ == new.__doc__


class TestSetupLogging:
    @pytest.fixture(scope="class", autouse=True)
    def ensure_null_status(self):
        utils._logging_formatter_status = None

    def test_default(self):
        utils.setup_logging()
        assert utils._logging_formatter_status is not None
        logger, handler = utils._logging_formatter_status
        assert isinstance(logger, logging.RootLogger)
        assert isinstance(handler, logging.handlers.RotatingFileHandler)
        handler.close()
        logger.removeHandler(handler)

    def test_custom_handler(self):
        handler = logging.StreamHandler()
        utils.setup_logging(handler=handler)
        assert utils._logging_formatter_status is not None
        logger, handler = utils._logging_formatter_status

        assert handler == handler
        assert isinstance(logger, logging.RootLogger)
        handler.close()
        logger.removeHandler(handler)

    def test_custom_formatter(self):
        formatter = logging.Formatter("{message}", style="{")
        utils.setup_logging(formatter=formatter)
        assert utils._logging_formatter_status is not None
        logger, handler = utils._logging_formatter_status

        assert isinstance(handler, logging.handlers.RotatingFileHandler)
        assert isinstance(logger, logging.RootLogger)
        assert handler.formatter == formatter

        handler.close()
        logger.removeHandler(handler)

    def test_custom_logger(self):
        before_logger = logging.getLogger("some-custom-name")
        utils.setup_logging(logger=before_logger)
        assert utils._logging_formatter_status is not None
        logger, handler = utils._logging_formatter_status

        assert isinstance(handler, logging.handlers.RotatingFileHandler)
        assert logger is before_logger

        handler.close()
        logger.removeHandler(handler)


class TestCoroOrGen:
    @pytest.fixture(scope="class", params=["coro", "gen"])
    def coro_or_gen(
        self, request: pytest.FixtureRequest
    ) -> Callable[[], AsyncIterator[str] | Awaitable[str]]:
        async def testinp1():
            return ["foo", "bar"]

        async def testinp2():
            yield "foo"
            yield "bar"

        return {"coro": testinp1, "gen": testinp2}[request.param]

    @pytest.mark.asyncio
    async def test_coro_or_gen(
        self, coro_or_gen: Callable[[], AsyncIterator[str] | Awaitable[str]]
    ) -> None:
        res = await utils.coro_or_gen(coro_or_gen())
        assert res == ["foo", "bar"]

    @pytest.mark.asyncio
    async def test_invalid_obj(self) -> None:
        with pytest.raises(TypeError, match="Not a coro or gen:"):
            await utils.coro_or_gen(None)  # type: ignore


class TestVersionInfo:
    @pytest.fixture(
        scope="class",
        params=[
            (utils.VersionInfo._from_str("1.0.0"), 1, 0, 0, "final"),
            (utils.VersionInfo._from_str("1.0.0a"), 1, 0, 0, "alpha"),
            (utils.VersionInfo._from_str("1.0.1b"), 1, 0, 1, "beta"),
            (utils.VersionInfo._from_str("1.0.2c"), 1, 0, 2, "candidate"),
        ],
    )
    def versioninfo_test_info(
        self, request: pytest.FixtureRequest
    ) -> tuple[utils.VersionInfo, int, int, int, str]:
        return request.param

    def test_final_release(
        self, versioninfo_test_info: tuple[utils.VersionInfo, int, int, int, str]
    ) -> None:
        ver, major, minor, micro, level = versioninfo_test_info
        assert ver.major == major
        assert ver.minor == minor
        assert ver.micro == micro
        assert ver.releaselevel == level

    def test_validation(self) -> None:
        with pytest.raises(ValueError, match="Invalid major version,"):
            utils.VersionInfo._from_str("a.0.0")
        with pytest.raises(ValueError, match="Invalid minor version,"):
            utils.VersionInfo._from_str("1.a.0")
        with pytest.raises(ValueError, match="Invalid micro version,"):
            utils.VersionInfo._from_str("1.0.a")


class TestInstanceOrClassmethod:
    def test_no_params(self) -> None:
        class TestClass:
            @classmethod
            def __classmethod(cls):
                return "foo"

            @utils.add_classmethod_alt(__classmethod)
            def instance(self):
                return "foo"

        assert TestClass.instance() == "foo"
        assert TestClass().instance() == "foo"

    def test_different_params(self) -> None:
        class TestClass:
            @classmethod
            def __classmethod(cls, prefix: str):
                return f"{prefix}-foo"

            @utils.add_classmethod_alt(__classmethod)
            def instance(self, suffix: str):
                return f"foo-{suffix}"

        with pytest.raises(TypeError):
            TestClass.instance()  # type: ignore
            TestClass.instance(suffix="test")  # type: ignore

            TestClass().instance()  # type: ignore
            TestClass().instance(prefix="car")  # type: ignore

        assert TestClass.instance(prefix="car") == "car-foo"
        assert TestClass().instance(suffix="car") == "foo-car"

    def test_same_params(self) -> None:
        class TestClass:
            @classmethod
            def __classmethod(cls, rand: int):
                return f"{rand}-foo"

            @utils.add_classmethod_alt(__classmethod)
            def instance(self, rand: int):
                return f"{rand}-foo"

        assert TestClass.instance(rand=5) == "5-foo"
        assert TestClass().instance(rand=5) == "5-foo"

    def test_docstring(self) -> None:
        class TestClass:
            @classmethod
            def __classmethod(cls):
                """classmethod docstring"""

            @utils.add_classmethod_alt(__classmethod)
            def instance(self):
                """instance docstring"""

        assert TestClass.instance.__doc__ == "instance docstring"


class TestPrint:
    @pytest_asyncio.fixture(scope="function", loop_scope="function")
    async def handler_future(self) -> AsyncIterator[asyncio.Future[logging.LogRecord]]:
        future = asyncio.Future()

        class CustomHandler(logging.Handler):
            def emit(self, record: logging.LogRecord):
                print(future)
                future.set_result(record)

        logger = logging.getLogger()
        handler = CustomHandler()

        logger.addHandler(handler)
        yield future
        logger.removeHandler(handler)

    @pytest.fixture(
        params=[
            (("foo",), utils.MISSING, "test-name"),
            (("foo", "bar", "car"), "|", "test-name"),
            (("foo", "bar", "car"), utils.MISSING, "test-name"),
            (("foo",), utils.MISSING, (utils.MISSING, __file__)),
        ]
    )
    def print_test_case(
        self, request: pytest.FixtureRequest
    ) -> tuple[tuple[str, ...], str, str | tuple[str, str]]:
        return request.param

    @pytest.mark.asyncio
    async def test_print(
        self,
        print_test_case: tuple[tuple[str, ...], str, str | tuple[str, str]],
        handler_future: asyncio.Future[logging.LogRecord],
    ) -> None:
        args, sep, name_info = print_test_case
        if isinstance(name_info, str):
            given_name = test_name = name_info
        else:
            given_name, test_name = name_info

        utils.print(*args, sep=sep, name=given_name)
        async with asyncio.timeout(2):
            msg = await handler_future
            assert msg.msg == (" " if sep is utils.MISSING else sep).join(args)
            assert msg.name == test_name


def test_decorator():
    def func(inp):
        return inp

    deco = utils.decorator(func)

    assert getattr(deco, "__is_decorator__", False) is True
    assert deco == func
    assert deco(5) == 5


class TestFuncWithSelf:
    @pytest.fixture
    def func_with_self_instance(self) -> utils.func_with_self:
        return utils.func_with_self(TestFuncWithSelf.basic_method)

    def basic_method(self) -> tuple[str, Self]:
        """some docstring"""
        return "foo", self

    def test_func_with_self(
        self, func_with_self_instance: utils.func_with_self
    ) -> None:
        func_with_self_instance.owner = self

        assert func_with_self_instance.__doc__ == TestFuncWithSelf.basic_method.__doc__
        assert func_with_self_instance() == ("foo", self)

    def test_no_owner(self, func_with_self_instance: utils.func_with_self) -> None:
        with pytest.raises(RuntimeError, match="Owner has not been set"):
            func_with_self_instance()


def test_missing():
    assert isinstance(utils.MISSING, utils._MissingSentinel)
    assert repr(utils.MISSING) == "..."
    assert not utils.MISSING
    assert utils.MISSING != "str"

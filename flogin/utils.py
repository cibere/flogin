from __future__ import annotations

import logging
import logging.handlers
from collections.abc import (
    AsyncGenerator,
    AsyncIterable,
    Awaitable,
    Callable,
    Coroutine,
)
from functools import update_wrapper, wraps
from inspect import isasyncgen, iscoroutine
from inspect import signature as _signature
from inspect import stack as _stack
from typing import (
    TYPE_CHECKING,
    Any,
    Concatenate,
    Generic,
    Literal,
    NamedTuple,
    ParamSpec,
    TypeVar,
    overload,
)

Coro = TypeVar("Coro", bound=Callable[..., Coroutine[Any, Any, Any]])
AGenT = TypeVar("AGenT", bound=Callable[..., AsyncGenerator[Any, Any]])
T = TypeVar("T")


class _cached_property(Generic[T]):
    def __init__(self, function: Callable[..., T]) -> None:
        self.function = function
        self.__doc__ = getattr(function, "__doc__")

    def __get__(self, instance: object | None, owner: type[object]) -> Any:
        if instance is None:
            return self

        value = self.function(instance)
        setattr(instance, self.function.__name__, value)

        return value


if TYPE_CHECKING:
    from functools import cached_property as cached_property
else:
    cached_property = _cached_property

__all__ = ("MISSING", "coro_or_gen", "print", "setup_logging")


def copy_doc(original: Callable[..., Any]) -> Callable[[T], T]:
    def decorator(overridden: T) -> T:
        overridden.__doc__ = original.__doc__
        setattr(overridden, "__sigature__", _signature(original))
        return overridden

    return decorator


class _MissingSentinel:
    """A type safe sentinel used in the library to represent something as missing. Used to distinguish from ``None`` values."""

    def __bool__(self) -> bool:
        return False

    def __eq__(self, other: Any) -> bool:
        return False

    def __repr__(self) -> str:
        return "..."


MISSING: Any = _MissingSentinel()

_logging_formatter_status: tuple[logging.Logger, logging.Handler] | None = None


def setup_logging(
    *,
    formatter: logging.Formatter | None = None,
    handler: logging.Handler | None = None,
    logger: logging.Logger | None = None,
) -> tuple[logging.Logger, logging.Handler]:
    r"""Sets up flogin's default logger.

    .. versionchanged:: 2.0.0
        :func:`setup_logging` now returns tuple[:class:`logging.Logger`, :class:`logging.Handler`]

    Parameters
    ----------
    formatter: Optional[:class:`logging.Formatter`]
        The formatter to use, incase you don't want to use the default file formatter.
    handler: Optional[:class:`logging.Handler`]
        The handler object that should be added to the logger. Defaults to :class:`logging.handlers.RotatingFileHandler` with the following arguments:

        .. code-block:: py3

            filename="flogin.log", maxBytes=1000000, encoding="UTF-8", backupCount=1

        .. versionadded:: 2.0.0
    logger: Optional[:class:`logging.Logger`]
        The logger object that the handler/formatter should be added to.

        .. versionadded:: 2.0.0

    Returns
    -------
    tuple[:class:`logging.Logger`, :class:`logging.Handler`]
        The logger and handler used to setup the logs.
    """

    level = logging.DEBUG

    if handler is None:
        handler = logging.handlers.RotatingFileHandler(
            filename="flogin.log", maxBytes=1000000, encoding="UTF-8", backupCount=1
        )

    if formatter is None:
        dt_fmt = "%Y-%m-%d %H:%M:%S"
        formatter = logging.Formatter(
            "[{asctime}] [{levelname:<8}] {name}: {message}", dt_fmt, style="{"
        )

    if logger is None:
        logger = logging.getLogger()

    handler.setFormatter(formatter)
    logger.setLevel(level)
    logger.addHandler(handler)

    global _logging_formatter_status
    _logging_formatter_status = logger, handler
    return _logging_formatter_status


async def coro_or_gen(coro: Awaitable[T] | AsyncIterable[T]) -> list[T] | T:
    """|coro|

    Executes an AsyncIterable or a Coroutine, and returns the result

    Parameters
    -----------
    coro: :class:`typing.Awaitable` | :class:`typing.AsyncIterable`
        The coroutine or asynciterable to be ran

    Raises
    --------
    TypeError
        Neither a :class:`typing.Coroutine` or an :class:`typing.AsyncIterable` was passed

    Returns
    --------
    Any
        Whatever was given from the :class:`typing.Coroutine` or :class:`typing.AsyncIterable`.
    """

    if iscoroutine(coro):
        return await coro
    if isasyncgen(coro):
        return [item async for item in coro]
    raise TypeError(f"Not a coro or gen: {coro!r}")


ReleaseLevel = Literal["alpha", "beta", "candidate", "final"]


class VersionInfo(NamedTuple):
    major: int
    minor: int
    micro: int
    releaselevel: ReleaseLevel

    @classmethod
    def _from_str(cls, txt: str) -> VersionInfo:
        raw_major, raw_minor, raw_micro_w_rel = txt.split(".")

        rlevel_shorthands: dict[str, ReleaseLevel] = {
            "a": "alpha",
            "b": "beta",
            "c": "candidate",
        }
        release_level = rlevel_shorthands.get(raw_micro_w_rel[-1], "final")

        if release_level != "final":
            raw_micro = raw_micro_w_rel.removesuffix(raw_micro_w_rel[-1])
        else:
            raw_micro = raw_micro_w_rel

        try:
            major = int(raw_major)
        except ValueError:
            raise ValueError(
                f"Invalid major version, {raw_major!r} is not a valid integer"
            ) from None
        try:
            minor = int(raw_minor)
        except ValueError:
            raise ValueError(
                f"Invalid minor version, {raw_minor!r} is not a valid integer"
            ) from None
        try:
            micro = int(raw_micro)
        except ValueError:
            raise ValueError(
                f"Invalid micro version, {raw_micro!r} is not a valid integer"
            ) from None

        return cls(major=major, minor=minor, micro=micro, releaselevel=release_level)


OwnerT = TypeVar("OwnerT")
# Instance signature
P = ParamSpec("P")
ReturnT = TypeVar("ReturnT")
InstanceMethodT = Callable[Concatenate[OwnerT, P], ReturnT]
# classmethod signature
PC = ParamSpec("PC")
ReturnCT = TypeVar("ReturnCT")
ClassMethodT = Callable[Concatenate[type[OwnerT], P], ReturnT]


class InstanceOrClassmethod(Generic[OwnerT, P, ReturnT, PC, ReturnCT]):
    def __init__(
        self,
        instance_func: InstanceMethodT[OwnerT, P, ReturnT],
        classmethod_func: ClassMethodT[OwnerT, PC, ReturnCT],
    ) -> None:
        self.__instance_func__: InstanceMethodT[OwnerT, P, ReturnT] = instance_func
        self.__classmethod_func__: ClassMethodT[OwnerT, PC, ReturnCT] = getattr(
            classmethod_func, "__func__", classmethod_func
        )

        self.__doc__ = self.__instance_func__.__doc__

    @overload
    def __get__(
        self, instance: None, owner: type[OwnerT]
    ) -> Callable[PC, ReturnCT]: ...

    @overload
    def __get__(
        self, instance: OwnerT, owner: type[OwnerT]
    ) -> Callable[P, ReturnT]: ...

    def __get__(self, instance: OwnerT | None, owner: type[OwnerT]) -> Any:
        @wraps(self.__instance_func__)
        def wrapper(*args: Any, **kwargs: Any) -> ReturnCT | ReturnT:
            if instance is not None:
                return self.__instance_func__(instance, *args, **kwargs)
            return self.__classmethod_func__(owner, *args, **kwargs)

        return wrapper


def add_classmethod_alt(
    classmethod_func: ClassMethodT[OwnerT, PC, ReturnCT],
) -> Callable[
    [InstanceMethodT[OwnerT, P, ReturnT]],
    InstanceOrClassmethod[OwnerT, P, ReturnT, PC, ReturnCT],
]:
    def decorator(
        instance_func: InstanceMethodT[OwnerT, P, ReturnT],
    ) -> InstanceOrClassmethod[OwnerT, P, ReturnT, PC, ReturnCT]:
        return InstanceOrClassmethod(instance_func, classmethod_func)

    return decorator


def print(*values: object, sep: str = MISSING, name: str = MISSING) -> None:
    r"""A function that acts similar to the `builtin print function <https://docs.python.org/3/library/functions.html#print>`__, but uses the `logging <https://docs.python.org/3/library/logging.html#module-logging>`__ module instead.

    This helper function is provided to easily "print" text without having to setup a logging object, because the builtin print function does not work as expected due to the jsonrpc pipes.

    .. versionadded:: 1.1.0
    .. versionchanged:: 2.0.0
        The default log name now defaults to the filepath of the file that called the function opposed to ``printing``.

    Parameters
    -----------
    \*values: :class:`object`
        A list of values to print
    sep: Optional[:class:`str`]
        The character that is used as the seperator between the values. Defaults to a space.
    name: Optional[:class:`str`]
        The name of the logger. Defaults to the filepath of the file the function is called from.

        .. versionadded:: 2.0.0
    """

    if sep is MISSING:
        sep = " "
    if name is MISSING:
        name = _stack()[1].filename

    logging.getLogger(name).info(sep.join(str(val) for val in values))


def decorator(deco: T) -> T:
    setattr(deco, "__is_decorator__", True)
    return deco


class func_with_self(Generic[P, ReturnT, OwnerT]):
    def __init__(self, func: Callable[Concatenate[OwnerT, P], ReturnT]) -> None:
        self.func = func
        self.owner: OwnerT | None = None

        update_wrapper(wrapped=func, wrapper=self)

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> ReturnT:
        if self.owner is None:
            raise RuntimeError("Owner has not been set")

        return self.func(self.owner, *args, **kwargs)

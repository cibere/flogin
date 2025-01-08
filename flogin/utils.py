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
from typing import (
    TYPE_CHECKING,
    Any,
    Concatenate,
    Generic,
    Literal,
    NamedTuple,
    ParamSpec,
    Self,
    TypeVar,
    overload,
)

Coro = TypeVar("Coro", bound=Callable[..., Coroutine[Any, Any, Any]])
AGenT = TypeVar("AGenT", bound=Callable[..., AsyncGenerator[Any, Any]])
T = TypeVar("T")

LOG = logging.getLogger(__name__)
_print_log = logging.getLogger("printing")


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


def setup_logging(
    *,
    formatter: logging.Formatter | None = None,
    handler: logging.Handler | None = None,
) -> None:
    r"""Sets up flogin's default logger.

    Parameters
    ----------
    formatter: Optional[:class:`logging.Formatter`]
        The formatter to use, incase you don't want to use the default file formatter.
    """

    level = logging.DEBUG

    if handler is None:
        handler = logging.handlers.RotatingFileHandler(
            "flogin.log", maxBytes=1000000, encoding="UTF-8"
        )

    if formatter is None:
        dt_fmt = "%Y-%m-%d %H:%M:%S"
        formatter = logging.Formatter(
            "[{asctime}] [{levelname:<8}] {name}: {message}", dt_fmt, style="{"
        )

    logger = logging.getLogger()
    handler.setFormatter(formatter)
    logger.setLevel(level)
    logger.addHandler(handler)


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

    def __call__(self, func: Callable) -> Self:
        self.__doc__ = func.__doc__
        return self

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


def print(*values: object, sep: str = MISSING) -> None:
    r"""A function that acts similar to the `builtin print function <https://docs.python.org/3/library/functions.html#print>`__, but uses the `logging <https://docs.python.org/3/library/logging.html#module-logging>`__ module instead.

    This helper function is provided to easily "print" text without having to setup a logging object, because the builtin print function does not work as expected due to the jsonrpc pipes.

    .. versionadded:: 1.1.0

    .. NOTE::
        The log/print statements can be viewed in your ``flogin.log`` file under the name ``printing``

    Parameters
    -----------
    \*values: :class:`object`
        A list of values to print
    sep: Optional[:class:`str`]
        The character that is used as the seperator between the values. Defaults to a space.
    """

    if sep is MISSING:
        sep = " "

    _print_log.info(sep.join(str(val) for val in values))


@overload
def decorator(*, is_factory: bool) -> Callable[[T], T]: ...


@overload
def decorator(deco: T) -> T: ...


def decorator(deco: T = MISSING, *, is_factory: bool = False) -> T | Callable[[T], T]:
    def inner(func: T) -> T:
        setattr(func, "__decorator_factory_status__", is_factory)
        return func

    if deco is not MISSING:
        return inner(deco)
    return inner


class func_with_self(Generic[P, ReturnT, OwnerT]):
    def __init__(self, func: Callable[Concatenate[OwnerT, P], ReturnT]) -> None:
        self.func = func
        self.owner: OwnerT | None = None

        update_wrapper(wrapped=func, wrapper=self)

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> ReturnT:
        if self.owner is None:
            raise RuntimeError("Owner has not been set")

        return self.func(self.owner, *args, **kwargs)

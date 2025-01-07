import logging
import logging.handlers
from functools import wraps
from inspect import isasyncgen, iscoroutine
from inspect import signature as _signature
from typing import (
    TYPE_CHECKING,
    Any,
    AsyncGenerator,
    AsyncIterable,
    Awaitable,
    Callable,
    Coroutine,
    Generic,
    Literal,
    NamedTuple,
    Self,
    TypeVar,
    overload,
)

Coro = TypeVar("Coro", bound=Callable[..., Coroutine[Any, Any, Any]])
AGenT = TypeVar("AGenT", bound=Callable[..., AsyncGenerator[Any, Any]])
T = TypeVar("T")
OwnerT = TypeVar("OwnerT")
FuncT = TypeVar("FuncT")
ReturnT = TypeVar("ReturnT")
ClassMethodT = Callable[[type[OwnerT], FuncT], ReturnT]
InstanceMethodT = Callable[[OwnerT, FuncT], ReturnT]

LOG = logging.getLogger(__name__)
_print_log = logging.getLogger("printing")


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

__all__ = ("setup_logging", "coro_or_gen", "MISSING", "print")


def copy_doc(original: Callable[..., Any]) -> Callable[[T], T]:
    def decorator(overridden: T) -> T:
        overridden.__doc__ = original.__doc__
        overridden.__signature__ = _signature(original)  # type: ignore
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
    elif isasyncgen(coro):
        return [item async for item in coro]
    else:
        raise TypeError(f"Not a coro or gen: {coro!r}")


ReleaseLevel = Literal["alpha", "beta", "candidate", "final"]


class VersionInfo(NamedTuple):
    major: int
    minor: int
    micro: int
    releaselevel: ReleaseLevel

    @classmethod
    def _from_str(cls, txt: str):
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


class decorator(Generic[OwnerT, FuncT, ReturnT]):
    @overload
    def __init__(self, /, *, is_factory: bool = True) -> None: ...
    @overload
    def __init__(
        self, instance_func: InstanceMethodT[OwnerT, FuncT, ReturnT], /
    ) -> None: ...
    def __init__(
        self,
        instance_func: InstanceMethodT[OwnerT, FuncT, ReturnT] | None = None,
        /,
        *,
        is_factory: bool = True,
    ) -> None:
        self.__instance_func__: InstanceMethodT[OwnerT, FuncT, ReturnT] | None = (
            instance_func
        )
        self.__classmethod_func__: ClassMethodT[OwnerT, FuncT, ReturnT] | None = None
        self.is_factory = is_factory

        if self.__instance_func__ is None:
            self.__doc__ = None
        else:
            self.__doc__ = self.__instance_func__.__doc__

    def __call__(self, instance_func: InstanceMethodT[OwnerT, FuncT, ReturnT]) -> Self:
        self.__instance_func__ = instance_func
        self.__doc__ = self.__instance_func__.__doc__
        return self

    @overload
    def __get__(
        self, instance: None, owner: type[OwnerT]
    ) -> Callable[[FuncT], ReturnT]: ...

    @overload
    def __get__(
        self, instance: OwnerT, owner: type[OwnerT]
    ) -> Callable[[FuncT], ReturnT]: ...

    def __get__(self, instance: OwnerT | None, owner: type[OwnerT]) -> Any:
        instance_func = self.__instance_func__
        if instance_func is None:
            raise RuntimeError("Instance Function is NoneType")

        @wraps(instance_func)
        def wrapper(func):
            if instance is not None:
                return instance_func(instance, func)
            if self.__classmethod_func__ is not None:
                return self.__classmethod_func__(owner, func)
            raise RuntimeError("Decorator useage as a classmethod is not supported")

        return wrapper

    def classmethod(self, func: T) -> T:
        if isinstance(func, classmethod):
            func = func.__func__
        self.__classmethod_func__ = func  # type: ignore
        return func


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

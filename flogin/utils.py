import functools
import logging
import logging.handlers
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
    TypeVar,
)

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

__all__ = (
    "setup_logging",
    "coro_or_gen",
    "MISSING",
)


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

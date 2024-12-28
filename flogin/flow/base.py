from __future__ import annotations

from inspect import getmembers
from typing import Any, Callable

from ..utils import MISSING

ValidCls = Callable[[Any], Any]


def _convert_cls(orig: ValidCls, is_list: bool) -> ValidCls:
    if orig is MISSING:
        return lambda x: x
    if orig is not MISSING and is_list is True:
        return lambda item: [orig(x) for x in item]
    return orig


def _get_prop_func(cls: ValidCls, name: str, *, default: Any = MISSING):
    if default is MISSING:

        def func(self):
            return cls(self._data[name])

    else:

        def func(self):
            return cls(self._data.get(name, default))

    return func


def add_prop(
    name: str,
    *,
    default: Any = MISSING,
    cls: ValidCls = MISSING,
    is_list: bool = False,
) -> Any:
    cls = _convert_cls(cls, is_list)
    func = _get_prop_func(cls, name, default=default)

    return property(func)


class Base:
    __slots__ = ("_data", "__repr_attributes__")

    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data
        self.__repr_attributes__ = [
            entry[0]
            for entry in getmembers(
                self.__class__, lambda other: isinstance(other, property)
            )
        ]

    def __repr__(self) -> str:
        args = []
        for item in self.__repr_attributes__:
            args.append(f"{item}={getattr(self, item)!r}")
        return f"<{self.__class__.__name__} {' '.join(args)}>"

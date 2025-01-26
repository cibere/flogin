from __future__ import annotations

import logging
from typing import TYPE_CHECKING, TypeVar, overload

log = logging.getLogger(__name__)

if TYPE_CHECKING:
    from ._types.json import Jsonable
    from ._types.settings import RawSettings

T = TypeVar("T")

__all__ = ("Settings",)


class Settings:
    r"""This class represents the settings that you user has chosen.

    If a setting is not found, ``None`` is returned instead.

    .. versionchanged:: 2.0.0
        Expand the value typehint to anything json seriable

    .. container:: operations

        .. describe:: x['setting name']

            Get a setting by key similiar to a dictionary

        .. describe:: x['setting name', 'default']

            Get a setting by key similiar to a dictionary, with a custom default.

        .. describe:: x['setting name'] = "new value"

            Change a settings value like a dictionary

        .. describe:: x.setting_name

            Get a setting by name like an attribute

        .. describe:: x.setting_name = "new value"

            Change a settings value like an attribute
    """

    _data: RawSettings
    _changes: RawSettings

    def __init__(self, data: RawSettings, *, no_update: bool = False) -> None:
        self._data = data
        self._changes = {}
        self._no_update = no_update

    @overload
    def __getitem__(self, key: str, /) -> Jsonable: ...

    @overload
    def __getitem__(self, key: tuple[str, T], /) -> Jsonable | T: ...

    def __getitem__(self, key: tuple[str, T] | str) -> Jsonable | T:
        if isinstance(key, str):
            default = None
        else:
            key, default = key
        return self._data.get(key, default)

    def __setitem__(self, key: str, value: Jsonable) -> None:
        self._data[key] = value
        self._changes[key] = value

    def __getattribute__(self, name: str) -> Jsonable:
        if name.startswith("_"):
            try:
                return super().__getattribute__(name)
            except AttributeError as e:
                raise AttributeError(
                    f"{e}. Settings that start with an underscore (_) can only be accessed by the __getitem__ method. Ex: settings['_key']"
                ) from None
        return self.__getitem__(name)

    def __setattr__(self, name: str, value: Jsonable) -> None:
        if name.startswith("_"):
            return super().__setattr__(name, value)
        self.__setitem__(name, value)

    def _update(self, data: RawSettings) -> None:
        if self._no_update:
            log.debug("Received a settings update, ignoring. data=%r", data)
        else:
            log.debug("Updating settings. Before: %s, after: %s", self._data, data)
            self._data = data

    def _get_updates(self) -> RawSettings:
        try:
            return self._changes
        finally:
            log.debug("Resetting setting changes: %s", self._changes)
            self._changes = {}

    def __repr__(self) -> str:
        return f"<Settings current={self._data!r}, pending_changes={self._changes}>"

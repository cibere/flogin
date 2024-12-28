from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, overload

if TYPE_CHECKING:
    from ._types import RawSettings

LOG = logging.getLogger(__name__)

__all__ = ("Settings",)


class Settings:
    r"""This class represents the settings that you user has chosen.

    If a setting is not found, ``None`` is returned instead.

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
    def __getitem__(self, key: str, /) -> Any: ...

    @overload
    def __getitem__(self, key: tuple[str, Any], /) -> Any: ...

    def __getitem__(self, key: tuple[str, Any] | str) -> Any:
        if isinstance(key, str):
            default = None
        else:
            key, default = key
        return self._data.get(key, default)

    def __setitem__(self, key: str, value: Any) -> None:
        self._data[key] = value
        self._changes[key] = value

    def __getattribute__(self, name: str) -> Any:
        if name.startswith("_"):
            try:
                return super().__getattribute__(name)
            except AttributeError as e:
                raise AttributeError(
                    f"{e}. Settings that start with an underscore (_) can only be accessed by the __getitem__ method. Ex: settings['_key']"
                ) from None
        return self.__getitem__(name)

    def __setattr__(self, name: str, value: Any) -> None:
        if name.startswith("_"):
            return super().__setattr__(name, value)
        self.__setitem__(name, value)

    def _update(self, data: RawSettings) -> None:
        if self._no_update:
            LOG.debug(f"Received a settings update, ignoring. {data=}")
        else:
            LOG.debug(f"Updating settings. Before: {self._data}, after: {data}")
            self._data = data

    def _get_updates(self) -> RawSettings:
        try:
            return self._changes
        finally:
            LOG.debug(f"Resetting setting changes: {self._changes}")
            self._changes = {}

    def __repr__(self) -> str:
        return f"<Settings current={self._data!r}, pending_changes={self._changes}>"

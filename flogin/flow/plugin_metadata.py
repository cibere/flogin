from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, Awaitable, Literal

from .base import Base, add_prop

if TYPE_CHECKING:
    from .api import FlowLauncherAPI

__all__ = ("PluginMetadata",)


class PluginMetadata(Base):
    r"""This class represents a plugin's metadata

    Attributes
    --------
    id: :class:`str`
        The plugin's ID
    name: :class:`str`
        The plugin's name
    author: :class:`str`
        The name of the plugin's author
    version: :class:`str`
        The current version of the plugin
    language: :class:`str`
        The language that the plugin is written in. Possible values: "csharp", "executable", "fsharp", "python", "javascript", "typescript", "python_v2", "executable_v2", "javascript_v2", "typescript_v2".
    description: :class:`str`
        The plugin's description
    website: :class:`str`
        A link to the plugin's website
    disabled: :class:`bool`
        Whether the plugin is disabled or not
    directory: :class:`str`
        The path to the plugin's directory
    keywords: list[:class:`str`]
        A list of the plugin's keywords
    main_keyword: :class:`str`
        The plugin's main keyword
    """

    def __init__(self, data: dict[str, Any], flow_api: FlowLauncherAPI) -> None:
        super().__init__(data)
        self._flow_api = flow_api

    id: str = add_prop("id")
    name: str = add_prop("name")
    author: str = add_prop("author")
    version: str = add_prop("version")
    language: Literal[
        "csharp",
        "executable",
        "fsharp",
        "python",
        "javascript",
        "typescript",
        "python_v2",
        "executable_v2",
        "javascript_v2",
        "typescript_v2",
    ] = add_prop("language")
    description: str = add_prop("description")
    website: str = add_prop("website")
    disabled: bool = add_prop("disabled")
    directory: str = add_prop("pluginDirectory")
    keywords: list[str] = add_prop("actionKeywords")
    main_keyword: str = add_prop("actionKeyword")

    @property
    def executable(self) -> Path:
        r""":class:`pathlib.Path`: The path to the plugin's executable file"""
        return Path(self._data["executeFilePath"]).absolute()

    @property
    def icon(self) -> Path:
        r""":class:`pathlib.Path`: The path to the plugin's icon file"""
        return Path(self._data["icoPath"]).absolute()

    def add_keyword(self, keyword: str) -> Awaitable[None]:
        r"""|coro|

        Registers a new keyword with flow for the plugin.

        This is a shortcut to :func:`~flogin.flow.api.FlowLauncherAPI.add_keyword`

        Parameters
        --------
        keyword: :class:`str`
            The keyword to be added

        Returns
        --------
        None
        """

        return self._flow_api.add_keyword(self.id, keyword)

    def remove_keyword(self, keyword: str) -> Awaitable[None]:
        """|coro|

        Removes a keyword from the plugin.

        This is a shortcut to :func:`~flogin.flow.api.FlowLauncherAPI.remove_keyword`

        Parameters
        --------
        keyword: :class:`str`
            The keyword to be removed

        Returns
        --------
        None
        """

        return self._flow_api.remove_keyword(self.id, keyword)

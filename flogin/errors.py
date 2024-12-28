from __future__ import annotations

__all__ = (
    "PluginException",
    "PluginNotInitialized",
)


class PluginException(Exception):
    r"""A class that represents exceptions with your plugin"""


class PluginNotInitialized(PluginException):
    r"""This is raised when you try to access something that needs data from the initialize method, and it hasn't been called yet."""

    def __init__(self):
        return super().__init__("The plugin hasn't been initialized yet")


class ContextMenuHandlerException(PluginException):
    r"""This is a base class for errors related to context menu handlers."""

    ...


class InvalidContextDataReceived(ContextMenuHandlerException):
    r"""Invalid context menu data was provided"""

    def __init__(self):
        return super().__init__(f"Invalid context menu data received")

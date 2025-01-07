from __future__ import annotations

__all__ = ("PluginException", "PluginNotInitialized", "EnvNotSet")


class PluginException(Exception):
    r"""A class that represents exceptions with your plugin"""


class PluginNotInitialized(PluginException):
    r"""This is raised when you try to access something that needs data from the initialize method, and it hasn't been called yet."""

    def __init__(self):
        return super().__init__("The plugin hasn't been initialized yet")


class EnvNotSet(PluginException):
    """This is raised when an environment variable that flow automatically sets is not set and can not be retrieved. This should only get raised when your plugin gets run, but not by flow.

    .. versionadded: 1.1.0

    Attributes
    -----------
    name: :class:`str`
        The name of the environment variable that was not found
    alternative: Optional[:class:`str`]
        Optionally, the name of the keyword argument in the :class:`~flogin.testing.plugin_tester.PluginTester` constructor that will set the variable for you.
    """

    def __init__(self, name: str, alternative: str | None = None) -> None:
        self.name = name
        self.alternative = alternative
        alt = (
            f"If you ran your plugin via the plugin tester, you can use the {alternative!r} keyword argument to quickly set this."
            if alternative
            else ""
        )
        super().__init__(
            f"The {name!r} environment variable is not set. These should be set by flow when it runs your plugin. {alt}"
        )

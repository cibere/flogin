from __future__ import annotations

TYPE_CHECKING = False
if TYPE_CHECKING:
    from subprocess import (
        CalledProcessError,  # noqa: TC003 # https://github.com/astral-sh/ruff/issues/15681
    )

    import requests  # noqa: TC002 # https://github.com/astral-sh/ruff/issues/15681

__all__ = (
    "EnvNotSet",
    "PipException",
    "PipExecutionError",
    "PluginException",
    "PluginNotInitialized",
    "UnableToDownloadPip",
)


class PluginException(Exception):
    r"""A class that represents exceptions with your plugin"""


class PluginNotInitialized(PluginException):
    r"""This is raised when you try to access something that needs data from the initialize method, and it hasn't been called yet."""

    def __init__(self) -> None:
        super().__init__("The plugin hasn't been initialized yet")


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


class PipException(Exception):
    r"""This is a base class to represent errors derived from the :class:`~flogin.pip.Pip` object.

    .. versionadded:: 2.0.0
    """


class UnableToDownloadPip(PipException):
    r"""This is an exception which is used to indicate that an error occurred while attempting to download pip.

    .. versionadded:: 2.0.0

    Attributes
    ----------
    error: :class:`requests.exceptions.HTTPError` | :class:`requests.Timeout` | :class:`requests.ConnectionError`
        The error that was raised by the :doc:`req:index` module.
    """

    def __init__(
        self, err: requests.HTTPError | requests.Timeout | requests.ConnectionError
    ) -> None:
        super().__init__(err)
        self.error = err


class PipExecutionError(PipException):
    r"""This is an exception which is raised whenever :meth:`flogin.pip.Pip.run` gets a return code that isn't ``0``.

    .. versionadded:: 2.0.0

    Attributes
    ----------
    error: :class:`subprocess.CalledProcessError`
        The original error that was raised by subprocess
    """

    def __init__(self, err: CalledProcessError) -> None:
        super().__init__(f"An error occurred while attempting to use pip: {err.stderr}")
        self.error = err

    @property
    def output(self) -> str:
        """:class:`str` The output from :attr:`subprocess.CalledProcessError.output`"""
        return self.error.output

    @property
    def returncode(self) -> int:
        """:class:`int` The returncode from :attr:`subprocess.CalledProcessError.returncode`"""
        return self.error.returncode

    @property
    def stderr(self) -> str:
        """:class:`str` The stderr from :attr:`subprocess.CalledProcessError.stderr`"""
        return self.error.stderr

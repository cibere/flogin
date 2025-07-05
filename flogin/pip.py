from __future__ import annotations

import logging
import subprocess
import sys
import tempfile
from pathlib import Path

from .utils import MISSING

try:
    import requests
except ImportError:  # cov: skip
    requests = MISSING

from .errors import PipExecutionError, UnableToDownloadPip

TYPE_CHECKING = False
if TYPE_CHECKING:
    from types import (
        TracebackType,  # noqa: TC003 # https://github.com/astral-sh/ruff/issues/15681
    )
    from typing import Self

__all__ = ("Pip",)

log = logging.getLogger(__name__)


class Pip:
    r"""This is a helper class for dealing with pip in a production environment.

    When flow launcher installs python, it does not install pip. Because of that, this class will temp-install pip while you need it, then delete it when you're done with it.

    .. versionadded:: 2.0.0

    .. WARNING::
        This class is blocking, and should only be used before you load your plugin.

    Parameters
    -----------
    libs_dir: Optional[:class:`pathlib.Path` | :class:`str`]
        The directory that your plugin's dependencies are installed to. Defaults to ``lib``.

    Example
    -------
    This should be used before your plugin gets loaded. Here is an example of what your main file might look like when using pip:

    .. code-block:: py3

        # Add your paths
        sys.path.append(...)
        sys.path.append(...)

        from flogin import Pip

        with Pip() as pip:
            pip.ensure_installed("msgspec") # ensure the msgspec package is installed correctly

        # import and run your plugin
        from plugin.plugin import YourPlugin
        YourPlugin().run()

    .. container::

        .. describe:: with Pip(...) as pip:

            :class:`Pip` can be used as a context manager, with :meth:`Pip.download_pip` being called on enter and :meth:`Pip.delete_pip` being called on exit.
    """

    _libs_dir: Path

    def __init__(self, libs_dir: Path | str = "lib") -> None:
        if requests is MISSING:
            raise ImportError(
                "Pip's Extra Dependencies are not installed. You can install them with flogin[pip]"
            )

        self._pip_fp: Path | None = None
        self.libs_dir = libs_dir
        self.pip_download_err: BaseException | None = None

    @property
    def libs_dir(self) -> Path:
        """:class:`pathlib.Path`: The directory that your plugin's dependencies are installed to."""
        return self._libs_dir

    @libs_dir.setter
    def libs_dir(self, new: Path | str) -> None:
        if isinstance(new, str):
            new = Path(new)

        if not new.exists():
            # Despite the fact that installing works perfectly fine with a nonexistent directory
            # adding it to path before its created then trying to import from it doesn't.
            raise ValueError(f"Directory Not Found: {new}")

        self._libs_dir = new

    def download_pip(self) -> bool:
        r"""Downloads the temp version of pip from pypa.

        .. NOTE::
            This is automatically called when using :class:`Pip` as a context manager.

        Raises
        ------
        :class:`UnableToDownloadPip`
            This is raised when an error occured while attempting to download pip.

        Returns
        -------
        :class:`bool`
            ``True`` indicates successful download of pip
            ``False`` indicates download of pip failed due an error in self.pip_download_err
        """
        try:
            res = requests.get("https://bootstrap.pypa.io/pip/pip.pyz", timeout=10)
            res.raise_for_status()
        except requests.RequestException as error:
            self.pip_download_err = error
            log.exception(f"Saving pip failed due {type(self.pip_download_err)}", exc_info=self.pip_download_err)
            return False
        
        with tempfile.NamedTemporaryFile("wb", suffix="-pip.pyz", delete=False) as f:
            try:
                f.write(res.content)
                self._pip_fp = Path(f.name)
            except BaseException as e:
                self.pip_download_err = e

        if self.pip_download_err:
            Path(f.name).unlink(missing_ok=True)
            log.exception(f"Saving pip failed due {type(self.pip_download_err)}", exc_info=self.pip_download_err)
            return False
        return True

    def delete_pip(self) -> None:
        r"""Deletes the temp version of pip installed on the system.

        .. NOTE::
            This is automatically called when using :class:`Pip` as a context manager.

        Returns
        --------
        ``None``
        """

        if self._pip_fp:
            self._pip_fp.unlink(missing_ok=True)
            log.info("Pip deleted from %s", self._pip_fp)

    def __enter__(self) -> Self:
        self.download_pip()
        return self

    def __exit__(
        self,
        type_: type[BaseException] | None,
        value: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool:
        self.delete_pip()
        return False

    def run(self, *args: str) -> str:
        r"""Runs a pip CLI command.

        This method is used to interact directly with pip.

        .. NOTE::
            This method can not be used until :meth:`download_pip` is ran, which you can do by calling it manually or using :class:`Pip` as a context manager.

        Parameters
        -----------
        \*args: :class:`str`
            The args that should be passed to pip. Ex: ``help``.

        Raises
        ------
        :class:`~flogin.errors.PipExecutionError`
            This is raised when the returncode that pip gives indicates an error.
        :class:`RuntimeError`
            This is raised when :meth:`Pip.download_pip` has not ran yet.

        Returns
        --------
        :class:`str`
            The output from pip.
        """

        if self._pip_fp is None and self.pip_download_err:
            raise UnableToDownloadPip(self.pip_download_err) from self.pip_download_err
        elif self._pip_fp is None:
            raise RuntimeError("Pip has not been installed")

        pip = self._pip_fp.as_posix()
        cmd = [sys.executable, pip, *args]
        log.debug("Sending command: %r", cmd)

        try:
            proc = subprocess.run(cmd, capture_output=True, check=True)
        except subprocess.CalledProcessError as e:
            log.debug("Pip command failed. stdout: %r, stderr: %r", e.output, e.stderr)
            raise PipExecutionError(e)

        output = proc.stdout.decode()
        log.debug("Pip stdout: %r", output)
        if proc.stderr:
            log.debug("Pip stderr: %r", proc.stderr)

        return output

    def install_packages(self, *packages: str) -> None:
        r"""An easy way to install packages for your plugin.

        .. NOTE::
            The packages will be installed to the directory set in :attr:`Pip.libs_dir`.

        Parameters
        ----------
        \*packages: :class:`str`
            The name of the packages on PyPi that you want to install.

        Raises
        ------
        :class:`PipException`
            This is raised when the returncode that pip gives indicates an error.

        Returns
        -------
        ``None``
        """

        self.run(
            "install",
            "--upgrade",
            "--force-reinstall",
            *packages,
            "-t",
            self.libs_dir.as_posix(),
        )

    def ensure_installed(self, package: str, *, module: str | None = None) -> bool:
        r"""Ensures a package is properly installed, and if not, reinstalls it.

        Parameters
        ----------
        package: :class:`str`
            The name of the package on PyPi that you want to install.
        module: Optional[:class:`str`]
            The name of the module you want to check to see if its installed. Defaults to the ``package`` value.

        Raises
        ------
        :class:`PipException`
            This is raised when the returncode that pip gives indicates an error.

        Returns
        -------
        :class:`bool`
            ``True`` indicates that the package wasn't properly installed, and was successfully reinstalled.
            ``False`` indicates that the package was already properly installed.
        """

        try:
            __import__(module or package)
        except (ImportError, ModuleNotFoundError):
            self.install_packages(package)
            return True
        return False

    def freeze(self) -> list[str]:
        r"""Returns a list of installed packages from ``pip freeze``.

        .. NOTE::
            The directory checked for packages is set in :attr:`Pip.libs_dir`.

        Raises
        ------
        :class:`PipException`
            This is raised when the returncode that pip gives indicates an error.

        Returns
        --------
        list[:class:`str`]
            The list of packages and versions.
        """

        return self.run("freeze", "--path", self.libs_dir.as_posix()).splitlines()

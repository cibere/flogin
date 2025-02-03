# pyright: basic

"""
Originally generated by coderabbitai
https://www.coderabbit.ai/
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path
from subprocess import CalledProcessError
from unittest.mock import MagicMock, patch

import pytest
import requests

from flogin import Pip
from flogin.errors import PipExecutionError, UnableToDownloadPip
from flogin.utils import MISSING


@pytest.fixture
def temp_dir(tmp_path):
    lib_dir = tmp_path / "lib"
    lib_dir.mkdir()
    yield lib_dir
    lib_dir.rmdir()


@pytest.fixture
def pip(temp_dir):
    pip_instance = Pip(temp_dir)
    yield pip_instance
    pip_instance.delete_pip()


def test_libs_dir_property(temp_dir):
    pip = Pip(temp_dir)
    assert pip.libs_dir == temp_dir

    pip = Pip(str(temp_dir))
    assert pip.libs_dir == temp_dir

    lib_dir = Path("lib")
    lib_dir_exists = lib_dir.exists()
    if not lib_dir_exists:
        lib_dir.mkdir()

    pip = Pip()
    assert pip.libs_dir == Path("lib")

    if not lib_dir_exists:
        lib_dir.rmdir()


def test_libs_dir_invalid_path():
    with pytest.raises(ValueError, match="Directory Not Found"):
        Pip("nonexistent_dir")


@patch("requests.get")
def test_download_pip_success(mock_get, pip):
    mock_response = MagicMock()
    mock_response.content = b"mock pip content"
    mock_get.return_value = mock_response

    pip.download_pip()
    assert pip._pip_fp is not None
    assert pip._pip_fp.exists()


@patch("requests.get")
def test_download_pip_http_error(mock_get, pip):
    mock_get.side_effect = requests.HTTPError()

    with pytest.raises(UnableToDownloadPip):
        pip.download_pip()


@patch("requests.get")
def test_download_pip_temp_file_error(mock_get, pip: Pip):
    class MockResponse(MagicMock):
        @property
        def content(self) -> str:
            raise RuntimeError("foo")

    mock_response = MockResponse()
    mock_get.return_value = mock_response

    with pytest.raises(RuntimeError, match="foo"):
        pip.download_pip()


def test_delete_pip(pip):
    # Create a mock pip file
    temp_file = Path("temp_pip.pyz")
    temp_file.write_text("mock content")
    pip._pip_fp = temp_file

    pip.delete_pip()
    assert not temp_file.exists()


@patch("requests.get")
def test_context_manager(mock_get, pip):
    mock_response = MagicMock()
    mock_response.content = b"mock pip content"
    mock_get.return_value = mock_response

    with pip as pip:
        assert pip._pip_fp is not None
        assert pip._pip_fp.exists()

    assert not pip._pip_fp.exists()


@patch("subprocess.run")
def test_run_success(mock_run, pip):
    mock_process = MagicMock()
    mock_process.stdout = b"success output"
    mock_run.return_value = mock_process

    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.content = b"mock pip content"
        mock_get.return_value = mock_response
        pip.download_pip()

    output = pip.run("install", "package")
    assert output == "success output"


def test_run_without_download(pip):
    with pytest.raises(RuntimeError, match="Pip has not been installed"):
        pip.run("install", "package")


@patch("subprocess.run")
def test_run_pip_error(mock_run, pip):
    mock_run.side_effect = subprocess.CalledProcessError(
        1, [], output=b"output", stderr=b"error"
    )

    # Mock pip download
    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.content = b"mock pip content"
        mock_get.return_value = mock_response
        pip.download_pip()

    with pytest.raises(PipExecutionError) as exc_info:
        pip.run("install", "package")

    assert exc_info.type == PipExecutionError
    assert isinstance(exc_info.value.error, CalledProcessError)
    assert exc_info.value.returncode == 1
    assert exc_info.value.output == "output"
    assert exc_info.value.stderr == "error"


@patch("subprocess.run")
def test_install_packages(mock_run, pip):
    mock_process = MagicMock()
    mock_process.stdout = b"installed successfully"
    mock_run.return_value = mock_process

    # Mock pip download
    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.content = b"mock pip content"
        mock_get.return_value = mock_response
        pip.download_pip()

    pip.install_packages("package1", "package2")

    # Verify correct command was called
    mock_run.assert_called_once()
    cmd_args = mock_run.call_args[0][0]
    assert "install" in cmd_args
    assert "package1" in cmd_args
    assert "package2" in cmd_args
    assert pip.libs_dir.as_posix() in cmd_args


@patch("subprocess.run")
def test_ensure_installed(mock_run, pip):
    mock_process = MagicMock()
    mock_process.stdout = b"installed successfully"
    mock_run.return_value = mock_process

    # Mock pip download
    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.content = b"mock pip content"
        mock_get.return_value = mock_response
        pip.download_pip()

    # Test package that needs installation
    with patch("builtins.__import__", side_effect=ImportError):
        result = pip.ensure_installed("nonexistent_package")
        assert result is True

    # Test already installed package
    with patch("builtins.__import__", return_value=None):
        result = pip.ensure_installed("existing_package")
        assert result is False


@patch("subprocess.run")
def test_ensure_installed_different_module(mock_run, pip):
    mock_process = MagicMock()
    mock_process.stdout = b"installed successfully"
    mock_run.return_value = mock_process

    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.content = b"mock pip content"
        mock_get.return_value = mock_response
        pip.download_pip()

    # Test package with different module name
    with patch("builtins.__import__", side_effect=ImportError):
        result = pip.ensure_installed("python-dateutil", module="dateutil")
        assert result is True


@patch("subprocess.run")
def test_freeze(mock_run, pip):
    mock_process = MagicMock()
    mock_process.stdout = b"package1==1.0.0\npackage2==2.0.0"
    mock_run.return_value = mock_process

    # Mock pip download
    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.content = b"mock pip content"
        mock_get.return_value = mock_response
        pip.download_pip()

    result = pip.freeze()
    assert result == ["package1==1.0.0", "package2==2.0.0"]


def test_missing_dep():
    from flogin import pip

    pip.requests = MISSING

    with pytest.raises(
        ImportError,
        match=re.escape(
            "Pip's Extra Dependencies are not installed. You can install them with flogin[pip]"
        ),
    ):
        pip.Pip()

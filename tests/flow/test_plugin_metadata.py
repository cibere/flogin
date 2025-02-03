# pyright: basic

from pathlib import Path

import pytest

from flogin.flow import PluginMetadata
from flogin.utils import MISSING


@pytest.fixture
def metadata() -> PluginMetadata:
    return PluginMetadata(
        {
            "id": "test",
            "name": "name",
            "author": "author",
            "version": "1.0.0a",
            "language": "python_v2",
            "description": "foo",
            "website": "https://google.com",
            "disabled": False,
            "pluginDirectory": "c:/plugin",
            "actionKeywords": ["foo", "bar"],
            "actionKeyword": "chore",
            "executeFilePath": "c:/plugin/exe.py",
            "icoPath": "c:/plugin/ico.png",
        },
        MISSING,
    )


def test_props(metadata: PluginMetadata) -> None:
    assert metadata.id == "test"
    assert metadata.name == "name"
    assert metadata.author == "author"
    assert metadata.version == "1.0.0a"
    assert metadata.language == "python_v2"
    assert metadata.description == "foo"
    assert metadata.website == "https://google.com"
    assert metadata.disabled is False
    assert metadata.directory == "c:/plugin"
    assert metadata.keywords == ["foo", "bar"]
    assert metadata.main_keyword == "chore"
    assert metadata.executable == Path("c:/plugin/exe.py")
    assert metadata.icon == Path("c:/plugin/ico.png")


@pytest.mark.asyncio
async def test_add_keyword(metadata: PluginMetadata) -> None:
    class MockApi:
        async def add_keyword(self, plugin_id: str, keyword: str) -> None:
            assert plugin_id == "test"
            assert keyword == "new_keyword"

    metadata._flow_api = MockApi()  # type: ignore

    await metadata.add_keyword("new_keyword")


@pytest.mark.asyncio
async def test_remove_keyword(metadata: PluginMetadata) -> None:
    class MockApi:
        async def remove_keyword(self, plugin_id: str, keyword: str) -> None:
            assert plugin_id == "test"
            assert keyword == "new_keyword"

    metadata._flow_api = MockApi()  # type: ignore

    await metadata.remove_keyword("new_keyword")

# pyright: basic

from collections.abc import Awaitable, Callable
from typing import Any

import pytest

from flogin import ErrorResponse, Plugin, Query, QueryResponse
from flogin.default_events import get_default_events
from flogin.jsonrpc.enums import ErrorCode
from flogin.query import RawQuery


@pytest.fixture
def plugin() -> Plugin:
    return Plugin()


@pytest.mark.asyncio
async def test_on_error(plugin: Plugin) -> None:
    default_events = get_default_events(plugin)
    on_error_event = default_events["on_error"]

    event_name = "test_event"
    error = TypeError("boo")

    resp = await on_error_event(event_name, error)
    assert isinstance(resp, ErrorResponse)
    assert resp.code == ErrorCode.server_error_start.value
    assert resp.data == error


class TestOnQuery:
    @pytest.fixture(params=["first", "second"])
    def on_query_case(
        self, request: pytest.FixtureRequest
    ) -> tuple[
        Callable[[RawQuery, dict[str, Any]], Awaitable[ErrorResponse | QueryResponse]],
        Plugin,
    ]:
        match request.param:
            case "first":

                class TestPlugin(Plugin):
                    async def process_search_handlers(
                        self, query: Query
                    ) -> ErrorResponse | QueryResponse:
                        return QueryResponse([])

                plugin = TestPlugin()
            case "second":

                class TestSecondPlugin(Plugin):
                    async def process_search_handlers(
                        self, query: Query
                    ) -> ErrorResponse | QueryResponse:
                        return QueryResponse([])

                class SettingsMock:
                    def _update(self, data: dict[str, Any]):
                        assert data == {}

                plugin = TestSecondPlugin()
                plugin._settings_are_populated = True
                plugin.settings = SettingsMock()  # type: ignore

        return get_default_events(plugin)["on_query"], plugin

    @pytest.mark.asyncio
    async def test_first_trigger(
        self,
        on_query_case: tuple[
            Callable[
                [RawQuery, dict[str, Any]], Awaitable[ErrorResponse | QueryResponse]
            ],
            Plugin,
        ],
    ) -> None:
        on_query_event, plugin = on_query_case

        raw_query: RawQuery = {
            "actionKeyword": "bar",
            "isReQuery": False,
            "rawQuery": "bar foo",
            "search": "foo",
        }
        resp = await on_query_event(raw_query, {})

        assert isinstance(resp, QueryResponse)
        assert resp.results == []

        assert plugin._settings_are_populated is True


@pytest.mark.asyncio
async def test_on_context_menu() -> None:
    class TestPlugin(Plugin):
        async def process_context_menus(
            self, data: list[str]
        ) -> ErrorResponse | QueryResponse:
            return QueryResponse(data)  # type: ignore

    plugin = TestPlugin()

    event: Callable[[list[str]], Awaitable[ErrorResponse | QueryResponse]] = (
        get_default_events(plugin)["on_context_menu"]
    )

    data = ["test"]
    resp = await event(data)

    assert isinstance(resp, QueryResponse)
    assert resp.results == data

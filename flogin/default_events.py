from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from .jsonrpc import ErrorResponse, QueryResponse
from .query import Query, RawQuery
from .settings import Settings

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from .plugin import Plugin


log = logging.getLogger(__name__)

__all__ = ("on_error",)


async def on_error(
    event_method: str, error: Exception, *args: Any, **kwargs: Any
) -> ErrorResponse:
    """gets called when an error occurs in an event"""
    log.exception("Ignoring exception in event %r", event_method, exc_info=error)
    return ErrorResponse.internal_error(error)


def get_default_events(plugin: Plugin[Any]) -> dict[str, Callable[..., Awaitable[Any]]]:
    def on_query(
        data: RawQuery, raw_settings: dict[str, Any]
    ) -> Awaitable[ErrorResponse | QueryResponse]:
        query = Query(data, plugin)
        plugin._last_query = query
        plugin._results.clear()

        if plugin._settings_are_populated is False:
            log.info("Settings have not been populated yet, creating a new instance")
            plugin._settings_are_populated = True
            plugin.settings = Settings(
                raw_settings, no_update=plugin.options.get("settings_no_update", False)
            )
        else:
            plugin.settings._update(raw_settings)
        return plugin.process_search_handlers(query)

    def on_context_menu(data: list[str]) -> Awaitable[ErrorResponse | QueryResponse]:
        return plugin.process_context_menus(data)

    return {
        event.__name__: event
        for event in (
            on_error,
            on_query,
            on_context_menu,
            plugin._initialize_wrapper,
        )
    }

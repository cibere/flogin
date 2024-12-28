from __future__ import annotations

import json
import os
import random
import sys
import uuid
from typing import TYPE_CHECKING, Any, Generic

from .._types import PluginT, RawSettings
from ..flow.plugin_metadata import PluginMetadata
from ..query import Query
from ..settings import Settings
from ..utils import MISSING
from .filler import FillerObject

if TYPE_CHECKING:
    from ..jsonrpc.responses import QueryResponse
    from ..jsonrpc.results import Result

API_FILLER_TEXT = "FlowLauncherAPI is unavailable during testing. Consider passing the 'flow_api_client' arg into PluginTester to implement your own flow api client."
CHARACTERS = "qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLLZXCVBNM1234567890"

__all__ = ("PluginTester",)


class PluginTester(Generic[PluginT]):
    r"""This can be used to write tests for your plugins.

    See the :doc:`testing` guide for more information on writing tests.

    This class implements a generic for the :attr:`~flogin.testing.plugin_tester.PluginTester.plugin` attribute, which will be used for typechecking purposes.

    Parameters
    ----------
    plugin: :class:`~flogin.plugin.Plugin`
        Your plugin
    metadata: :class:`~flogin.flow.plugin_metadata.PluginMetadata` | dict[str, Any] | None
        Your plugin's metadata. If ``None`` is passed, flogin will attempt to get the metadata from your ``plugin.json`` file. The :func:`PluginTester.create_plugin_metadata` and :func:`PluginTester.create_bogus_plugin_metadata` classmethods have been provided for creating :class:`~flogin.flow.plugin_metadata.PluginMetadata` objects.
    flow_api_client: Optional[Any]
        If not passed, flogin will use a filler class which will raise a runtime error whenever an attribute is accessed. If passed, you should be passing an instance of a class which will replace :class:`~flogin.flow.api.FlowLauncherAPI`, so make sure to implement the methods you need and handle them accordingly.

    Attributes
    ----------
    plugin: :class:`~flogin.plugin.Plugin`
        Your plugin
    """

    plugin: PluginT

    def __init__(
        self,
        plugin: PluginT,
        *,
        metadata: PluginMetadata | dict[str, Any] | None,
        flow_api_client: Any = MISSING,
    ) -> None:
        self.plugin = plugin

        if metadata is None:
            if not os.path.exists("plugin.json"):
                raise ValueError(
                    "plugin.json file can not be located, consider passing the metadata instead"
                )
            with open("plugin.json", "r") as f:
                metadata = json.load(f)
            assert metadata

        if isinstance(metadata, dict):
            metadata = PluginMetadata(metadata, self.plugin.api)

        self.plugin._metadata = metadata

        self.set_flow_api_client(flow_api_client)

    def set_flow_api_client(self, flow_api_client: Any = MISSING) -> None:
        r"""This sets the flow api client that the tests should use.

        Parameters
        ----------
        flow_api_client: Optional[Any]
            If not passed, flogin will use a filler class which will raise a runtime error whenever an attribute is accessed. If passed, you should be passing an instance of a class which will replace :class:`~flogin.flow.api.FlowLauncherAPI`, so make sure to implement the methods you need and handle them accordingly.
        """
        if flow_api_client is MISSING:
            flow_api_client = FillerObject(API_FILLER_TEXT)

        self.plugin.api = flow_api_client
        self.plugin.metadata._flow_api = flow_api_client

    async def test_query(
        self,
        text: str,
        *,
        keyword: str = "*",
        is_requery: bool = False,
        settings: Settings | RawSettings | None = MISSING,
    ) -> QueryResponse:
        r"""|coro|

        This coroutine can be used to send your plugin a query, and get the response.

        Parameters
        ----------
        query: :class:`~flogin.query.Query`
            The query object that should be passed to your search handlers.
        settings: Optional[:class:`~flogin.settings.Settings` | dict[str, Any] | None]
            This will represent the settings that flogin will use when executing your search handlers. If not passed, flogin will not use any settings. If ``None`` is passed, flogin will get the settings from the settings file (this is incompatible with :func:`PluginTester.create_bogus_plugin_metadata`). If a dict or :class:`~flogin.settings.Settings` object is passed, those are the settings that will be put in :attr:`~flogin.plugin.Plugin.settings` before executing your search handlers.

        Returns
        -------
        :class:`~flogin.jsonrpc.responses.QueryResponse`
            The query response object that would normally be sent to flow.
        """

        if isinstance(settings, dict):
            settings = Settings(settings)
        if settings is MISSING:
            settings = Settings({})

        if isinstance(settings, Settings):
            self.plugin.settings = settings
            self.plugin._settings_are_populated = True

        query = Query(
            {
                "rawQuery": f"{keyword} {text}",
                "search": text,
                "actionKeyword": keyword,
                "isReQuery": is_requery,
            },
            self.plugin,
        )

        coro = self.plugin.process_search_handlers(query)

        if coro is None:
            raise RuntimeError("Query event handler not found")

        return await coro  # type: ignore

    async def test_context_menu(
        self, result: Result, *, bypass_registration: bool = False
    ) -> QueryResponse:
        r"""|coro|

        This coroutine can be used to send a result's context menu, and get the response.

        .. NOTE::
            You should use this to test your context menus instead of invoking them directly because this method implements the post-processing that flogin puts onto your context menu and query methods.

        Parameters
        ----------
        result: :class:`~flogin.jsonrpc.results.Result`
            The result you want to invoke the context menu for.
        bypass_registration: :class:`bool`
            Whether or not to bypass the ``Result has not been registered`` error.

        Raises
        ------
        ValueError
            This will be raised when ``bypass_registration`` is set to ``False``, and the given result has not been registered.

        Returns
        -------
        :class:`~flogin.jsonrpc.responses.QueryResponse`
            The query response object that would normally be sent to flow.
        """

        coro = self.plugin.dispatch("context_menu", [result.slug])

        if coro is None:
            if bypass_registration:
                self.plugin._results[result.slug] = result
                return await self.test_context_menu(result)

            raise ValueError("Result has not been registered.")

        return await coro  # type: ignore

    @classmethod
    def create_bogus_plugin_metadata(cls: type[PluginTester]) -> PluginMetadata:
        r"""This classmethod can be used to easily and quickly create a :class:`~flogin.flow.plugin_metadata.PluginMetadata` object that can be used for testing.

        .. NOTE::
            Since the information that this classmethod generates is bogus, it is not recommended to use this when your plugin relies on the plugin metadata. Consider using :func:`PluginTester.create_plugin_metadata` instead.

        Returns
        --------
        :class:`~flogin.flow.plugin_metadata.PluginMetadata`
            The :class:`~flogin.flow.plugin_metadata.PluginMetadata` instance with your bogus information.
        """

        return cls.create_plugin_metadata(
            id=str(uuid.uuid4()),
            name="".join(random.choices(CHARACTERS, k=10)),
            author="".join(random.choices(CHARACTERS, k=5)),
            version="1.0.0",
            description="A plugin with bogus metadata to test",
        )

    @classmethod
    def create_plugin_metadata(
        cls: type[PluginTester],
        *,
        id: str,
        name: str,
        author: str,
        version: str,
        description: str,
        website: str | None = None,
        disabled: bool = False,
        directory: str | None = None,
        keywords: list[str] | None = None,
        main_keyword: str | None = None,
        icon_path: str | None = None,
    ) -> PluginMetadata:
        r"""This classmethod can be used to easily create a valid :class:`~flogin.flow.plugin_metadata.PluginMetadata` object that has correct data.

        Parameters
        -----------
        id: :class:`str`
            The plugin's id
        name: :class:`str`
            The plugin's name
        author: :class:`str`
            The plugin's author
        version: :class:`str`
            The plugin's version
        description: :class:`str`
            The plugin's description
        website: Optional[:class:`str`]
            The plugin's website. If not given, the following fstring will be used instead: ``f"https://github.com/{author}/{name}"``
        disabled: Optional[:class:`bool`]
            Whether or not to mark the plugin as disabled. Defaults to ``False``
        directory: Optional[:class:`str`]
            The plugin's directory. Defaults to the current working directory.
        keywords: Optional[list[:class:`str`]]
            The plugin's keywords. Defaults to ``["*"]``
        main_keyword: Optional[:class:`str`]
            The plugin's main keyword. Defaults to the first keyword in the keywords parameter
        icon_path: Optional[:class:`str`]
            The plugin's icon. Defaults to an invalid icon path.

        Returns
        --------
        :class:`~flogin.flow.plugin_metadata.PluginMetadata`
            Your new metadata class.
        """

        action_keywords: list[str] = keywords or ["*"]
        try:
            main_keyword = main_keyword or action_keywords[0]
        except IndexError:
            main_keyword = "*"

        data = {
            "id": id,
            "name": name,
            "author": author,
            "version": version,
            "language": "python_v2",
            "description": description,
            "website": website or f"https://github.com/{author}/{name}",
            "disabled": disabled,
            "pluginDirectory": directory or os.getcwd(),
            "actionKeywords": action_keywords,
            "main_keyword": main_keyword,
            "executeFilePath": sys.argv[0],
            "icoPath": icon_path or "",
        }

        return PluginMetadata(data, FillerObject(API_FILLER_TEXT))  # type: ignore

    def __repr__(self):
        return f"<PluginTester id={id(self)} {self.plugin=}>"

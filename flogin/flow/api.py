from __future__ import annotations

import asyncio
import inspect
from typing import TYPE_CHECKING, ParamSpec, TypeVar

from .fuzzy_search import FuzzySearchResult
from .method import FlowAPIMethod, Gen, _flow_api_method, flow_api_method
from .plugin_metadata import PluginMetadata

ATS = ParamSpec("ATS")
T = TypeVar("T")
if TYPE_CHECKING:
    from ..jsonrpc import JsonRPCClient, Result

__all__ = ("FlowLauncherAPI",)


class FlowLauncherAPI:
    r"""This class is a wrapper around Flow's API to make it easy to make requests and receive results.

    .. NOTE::
        Do not initialize this class yourself, instead use :class:`~flogin.plugin.Plugin`'s :attr:`~flogin.plugin.Plugin.api` attribute to get an instance.
    """

    def __init__(self, jsonrpc: JsonRPCClient):
        self.jsonrpc = jsonrpc
        for name, value in inspect.getmembers(
            self, lambda d: isinstance(d, _flow_api_method)
        ):
            value.parent = self

    async def __call__(self, *methods: FlowAPIMethod[T]) -> list[T]:
        from ..jsonrpc import ErrorResponse  # circular import

        params = []
        after: list[asyncio.Future] = []
        tasks: list[asyncio.Task] = []
        for method in methods:
            api_fut, data_fut, task = method._prep_batch()
            params.append(await data_fut)
            after.append(api_fut)
            tasks.append(task)

        resp = await self.jsonrpc.request("BatchRequest", params)
        assert not isinstance(resp, ErrorResponse)

        for result, fut in zip(resp["result"], after):
            fut.set_result(result)

        return await asyncio.gather(*tasks)

    @flow_api_method
    def fuzzy_search(
        self, text: str, text_to_compare_it_to: str
    ) -> Gen[FuzzySearchResult]:
        r"""|coro|

        Asks flow how similiar two strings are.

        Parameters
        --------
        text: :class:`str`
            The text
        text_to_compare_it_to: :class:`str`
            The text you want to compare the other text to

        Returns
        --------
        :class:`~flogin.flow.fuzzy_search.FuzzySearchResult`
        """

        from ..jsonrpc import ErrorResponse  # circular import

        res = yield "FuzzySearch", [text, text_to_compare_it_to]
        assert not isinstance(res, ErrorResponse)
        return FuzzySearchResult(res["result"])

    @flow_api_method
    def change_query(self, new_query: str, requery: bool = False) -> Gen[None]:
        r"""|coro|

        Change the query in flow launcher's menu.

        Parameters
        --------
        new_query: :class:`str`
            The new query to change it to
        requery: :class:`bool`
            Whether or not to re-send a query request in the event that the `new_query` is the same as the current query

        Returns
        --------
        None
        """

        from ..jsonrpc import ErrorResponse  # circular import

        res = yield "ChangeQuery", [new_query, requery]
        assert not isinstance(res, ErrorResponse)

    @flow_api_method
    def show_error_message(self, title: str, text: str) -> Gen[None]:
        r"""|coro|

        Triggers an error message in the form of a windows notification

        Parameters
        --------
        title: :class:`str`
            The title of the notification
        text: :class:`str`
            The content of the notification

        Returns
        --------
        None
        """

        from ..jsonrpc import ErrorResponse  # circular import

        res = yield "ShowMsgError", [title, text]
        assert not isinstance(res, ErrorResponse)

    @flow_api_method
    def show_notification(
        self,
        title: str,
        content: str,
        icon: str = "",
        use_main_window_as_owner: bool = True,
    ) -> Gen[None]:
        r"""|coro|

        Creates a notification window in the bottom right hand of the user's screen

        Parameters
        --------
        title: :class:`str`
            The notification's title
        content: :class:`str`
            The notification's content
        icon: :class:`str`
            The icon to be shown with the notification, defaults to `""`
        use_main_window_as_owner: :class:`bool`
            Whether or not to use the main flow window as the notification's owner. Defaults to `True`

        Returns
        --------
        None
        """

        from ..jsonrpc import ErrorResponse  # circular import

        res = yield ("ShowMsg", [title, content, icon, use_main_window_as_owner])
        assert not isinstance(res, ErrorResponse)

    @flow_api_method
    def open_settings_menu(self) -> Gen[None]:
        r"""|coro|

        This method tells flow to open up the settings menu.

        Returns
        --------
        None
        """

        from ..jsonrpc import ErrorResponse  # circular import

        res = yield "OpenSettingDialog", []
        assert not isinstance(res, ErrorResponse)

    @flow_api_method
    def open_url(self, url: str, in_private: bool = False) -> Gen[None]:
        r"""|coro|

        Open up a url in the user's preferred browser, which was set in their Flow Launcher settings.

        Parameters
        --------
        url: :class:`str`
            The url to be opened in the webbrowser
        in_private: :class:`bool`
            Whether or not to open up the url in a private window

        Returns
        --------
        None
        """

        from ..jsonrpc import ErrorResponse  # circular import

        res = yield ("OpenUrl", [url, in_private])
        assert not isinstance(res, ErrorResponse)

    @flow_api_method
    def run_shell_cmd(self, cmd: str, filename: str = "cmd.exe") -> Gen[None]:
        r"""|coro|

        Tell flow to run a shell command

        Parameters
        --------
        cmd: :class:`str`
            The command to be run
        filename: :class:`str`
            The name of the command prompt instance, defaults to `cmd.exe`

        Returns
        --------
        None
        """

        from ..jsonrpc import ErrorResponse  # circular import

        res = yield ("ShellRun", [cmd, filename])
        assert not isinstance(res, ErrorResponse)

    @flow_api_method
    def restart_flow_launcher(self) -> Gen[None]:
        r"""|coro|

        This method tells flow launcher to initiate a restart of flow launcher.

        .. WARNING::
            Expect this method to never finish, so clean up and prepare for the plugin to be shut down before calling this.
        """

        from ..jsonrpc import ErrorResponse  # circular import

        res = yield ("RestartApp", [])
        assert not isinstance(res, ErrorResponse)

    @flow_api_method
    def save_all_app_settings(self) -> Gen[None]:
        r"""|coro|

        This method tells flow to save all app settings.

        Returns
        --------
        None
        """

        from ..jsonrpc import ErrorResponse  # circular import

        res = yield ("SaveAppAllSettings", [])
        assert not isinstance(res, ErrorResponse)

    @flow_api_method
    def save_plugin_settings(self) -> Gen[None]:
        r"""|coro|

        This method tells flow to save plugin settings

        Returns
        --------
        None
        """

        from ..jsonrpc import ErrorResponse  # circular import

        res = yield ("SavePluginSettings", [])
        assert not isinstance(res, ErrorResponse)

    @flow_api_method
    def reload_all_plugin_data(self) -> Gen[None]:
        r"""|coro|

        This method tells flow to trigger a reload of all plugins.

        Returns
        --------
        None
        """

        from ..jsonrpc import ErrorResponse  # circular import

        res = yield ("ReloadAllPluginDataAsync", [])
        assert not isinstance(res, ErrorResponse)

    @flow_api_method
    def show_main_window(self) -> Gen[None]:
        """|coro|

        This method tells flow to show the main window

        Returns
        --------
        None
        """

        from ..jsonrpc import ErrorResponse  # circular import

        res = yield ("ShowMainWindow", [])
        assert not isinstance(res, ErrorResponse)

    @flow_api_method
    def hide_main_window(self) -> Gen[None]:
        r"""|coro|

        This method tells flow to hide the main window

        Returns
        --------
        None
        """

        from ..jsonrpc import ErrorResponse  # circular import

        res = yield ("HideMainWindow", [])
        assert not isinstance(res, ErrorResponse)

    @flow_api_method
    def is_main_window_visible(self) -> Gen[bool]:
        r"""|coro|

        This method asks flow if the main window is visible or not

        Returns
        --------
        :class:`bool`
        """

        from ..jsonrpc import ErrorResponse  # circular import

        res = yield ("IsMainWindowVisible", [])
        assert not isinstance(res, ErrorResponse)
        return res["result"]

    @flow_api_method
    def check_for_updates(self) -> Gen[None]:
        r"""|coro|

        This tells flow launcher to check for updates to flow launcher

        .. NOTE::
            This tells flow launcher to check for updates to flow launcher, not your plugin

        Returns
        --------
        None
        """

        from ..jsonrpc import ErrorResponse  # circular import

        res = yield ("CheckForNewUpdate", [])
        assert not isinstance(res, ErrorResponse)

    @flow_api_method
    def get_all_plugins(self) -> Gen[list[PluginMetadata]]:
        r"""|coro|

        Get the metadata of all plugins that the user has installed

        Returns
        --------
        list[:class:`~flogin.flow.plugin_metadata.PluginMetadata`]
        """

        from ..jsonrpc import ErrorResponse  # circular import

        res = yield ("GetAllPlugins", [])
        assert not isinstance(res, ErrorResponse)
        return [PluginMetadata(plugin["metadata"], self) for plugin in res["result"]]

    @flow_api_method
    def add_keyword(self, plugin_id: str, keyword: str) -> Gen[None]:
        r"""|coro|

        Registers a new keyword for a plugin with flow launcher.

        Parameters
        --------
        plugin_id: :class:`str`
            The id of the plugin that you want the keyword added to
        keyword: :class:`str`
            The keyword to add

        Returns
        --------
        None
        """

        from ..jsonrpc import ErrorResponse  # circular import

        res = yield ("AddActionKeyword", [plugin_id, keyword])
        assert not isinstance(res, ErrorResponse)

    @flow_api_method
    def remove_keyword(self, plugin_id: str, keyword: str) -> Gen[None]:
        r"""|coro|

        Unregisters a keyword for a plugin with flow launcher.

        Parameters
        --------
        plugin_id: :class:`str`
            The ID of the plugin that you want to remove the keyword from
        keyword: :class:`str`
            The keyword that you want to remove

        Returns
        --------
        None
        """

        from ..jsonrpc import ErrorResponse  # circular import

        res = yield ("RemoveActionKeyword", [plugin_id, keyword])
        assert not isinstance(res, ErrorResponse)

    @flow_api_method
    def open_directory(self, directory: str, file: str | None = None) -> Gen[None]:
        r"""|coro|

        Opens up a folder in file explorer. If a file is provided, the file will be pre-selected.

        Parameters
        --------
        directory: :class:`str`
            The directory you want to open
        file: Optional[:class:`str`]
            The file in the directory that you want to highlight, defaults to `None`

        Returns
        --------
        None
        """

        from ..jsonrpc import ErrorResponse  # circular import

        res = yield ("OpenDirectory", [directory, file])
        assert not isinstance(res, ErrorResponse)

    @flow_api_method
    def update_results(self, raw_query: str, results: list[Result]) -> Gen[None]:
        r"""|coro|

        Tells flow to change the results shown to the user

        .. NOTE::
            The ``raw_query`` parameter is required by flow launcher, and must be the same as the current raw query in flow launcher for the results to successfully update.

        Parameters
        ----------
        raw_query: :class:`str`
            Only change the results if the current raw query is the same as this
        results: list[:class:`~flogin.jsonrpc.results.Result`]
            The new results

        Returns
        -------
        None
        """

        from ..jsonrpc import ErrorResponse, QueryResponse  # circular import

        res = yield ("UpdateResults", [raw_query, QueryResponse(results).to_dict()])
        self.jsonrpc.plugin._results.update({res.slug: res for res in results})
        assert not isinstance(res, ErrorResponse)

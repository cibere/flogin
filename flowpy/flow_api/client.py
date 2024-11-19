from __future__ import annotations

from typing import TYPE_CHECKING, Any, ParamSpec

from .fuzzy_search import FuzzySearchResult
from .plugin_metadata import PluginMetadata

ATS = ParamSpec("ATS")

if TYPE_CHECKING:
    from ..jsonrpc import ExecuteResponse, JsonRPCClient

__all__ = ("FlowLauncherAPI",)


class FlowLauncherAPI:
    r"""This class is a wrapper around Flow's API to make it easy to make requests and receive results.

    .. NOTE::
        Do not initialize this class yourself, use :obj:`Plugin.api` to get an instance instead.
    """

    def __init__(self, jsonrpc: JsonRPCClient):
        self.jsonrpc = jsonrpc

    async def __call__(self, method: str, *args: Any, **kwargs: Any) -> ExecuteResponse:
        from ..jsonrpc import ExecuteResponse

        await getattr(self, method)(*args, **kwargs)
        return ExecuteResponse()

    async def fuzzy_search(
        self, text: str, text_to_compare_it_to: str
    ) -> FuzzySearchResult:
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
        :class:`FuzzySearchResult`
        """

        from ..jsonrpc import Result  # circular import

        res = await self.jsonrpc.request("FuzzySearch", [text, text_to_compare_it_to])
        assert isinstance(res, Result)
        return FuzzySearchResult(res.data)

    async def change_query(self, new_query: str, requery: bool = False) -> None:
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

        from ..jsonrpc import Result  # circular import

        res = await self.jsonrpc.request("ChangeQuery", [new_query, requery])
        assert isinstance(res, Result)

    async def show_error_message(self, title: str, text: str) -> None:
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

        from ..jsonrpc import Result  # circular import

        res = await self.jsonrpc.request("ShowMsgError", [title, text])
        assert isinstance(res, Result)

    async def show_notification(
        self,
        title: str,
        content: str,
        icon: str = "",
        use_main_window_as_owner: bool = True,
    ) -> None:
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

        from ..jsonrpc import Result  # circular import

        res = await self.jsonrpc.request(
            "ShowMsg", [title, content, icon, use_main_window_as_owner]
        )
        assert isinstance(res, Result)

    async def open_settings_menu(self) -> None:
        r"""|coro|

        This method tells flow to open up the settings menu.

        Returns
        --------
        None
        """

        from ..jsonrpc import Result  # circular import

        res = await self.jsonrpc.request("OpenSettingDialog")
        assert isinstance(res, Result)

    async def open_url(self, url: str, in_private: bool = False) -> None:
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

        from ..jsonrpc import Result  # circular import

        res = await self.jsonrpc.request("OpenUrl", [url, in_private])
        assert isinstance(res, Result)

    async def run_shell_cmd(self, cmd: str, filename: str = "cmd.exe") -> None:
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

        from ..jsonrpc import Result  # circular import

        res = await self.jsonrpc.request("ShellRun", [cmd, filename])
        assert isinstance(res, Result)

    async def restart_flow_launcher(self) -> None:
        r"""|coro|

        This method tells flow launcher to initiate a restart of flow launcher.

        .. WARNING::
            Expect this method to never finish, so clean up and prepare for the plugin to be shut down before calling this.
        """

        from ..jsonrpc import Result  # circular import

        res = self.jsonrpc.request("RestartApp")
        assert isinstance(res, Result)

    async def save_all_app_settings(self) -> None:
        r"""|coro|

        This method tells flow to save all app settings.

        Returns
        --------
        None
        """

        from ..jsonrpc import Result  # circular import

        res = await self.jsonrpc.request("SaveAppAllSettings")
        assert isinstance(res, Result)

    async def save_plugin_settings(self) -> Any:
        r"""|coro|

        This method tells flow to save plugin settings

        Returns
        --------
        None
        """

        from ..jsonrpc import Result  # circular import

        res = await self.jsonrpc.request("SavePluginSettings")
        assert isinstance(res, Result)
        return res.data

    async def reload_all_plugin_data(self) -> None:
        r"""|coro|

        This method tells flow to trigger a reload of all plugins.

        Returns
        --------
        None
        """

        from ..jsonrpc import Result  # circular import

        res = await self.jsonrpc.request("ReloadAllPluginDataAsync")
        assert isinstance(res, Result)

    async def show_main_window(self) -> None:
        """|coro|

        This method tells flow to show the main window

        Returns
        --------
        None
        """

        from ..jsonrpc import Result  # circular import

        res = await self.jsonrpc.request("ShowMainWindow")
        assert isinstance(res, Result)

    async def hide_main_window(self) -> None:
        r"""|coro|

        This method tells flow to hide the main window

        Returns
        --------
        None
        """

        from ..jsonrpc import Result  # circular import

        res = await self.jsonrpc.request("HideMainWindow")
        assert isinstance(res, Result)

    async def is_main_window_visible(self) -> bool:
        r"""|coro|

        This method asks flow if the main window is visible or not

        Returns
        --------
        :class:`bool`
        """

        from ..jsonrpc import Result  # circular import

        res = await self.jsonrpc.request("IsMainWindowVisible")
        assert isinstance(res, Result)
        return res.data

    async def check_for_updates(self) -> None:
        r"""|coro|

        This tells flow launcher to check for updates to flow launcher

        .. NOTE::
            This tells flow launcher to check for updates to flow launcher, not your plugin

        Returns
        --------
        None
        """

        from ..jsonrpc import Result  # circular import

        res = await self.jsonrpc.request("CheckForNewUpdate")
        assert isinstance(res, Result)

    async def get_all_plugins(self) -> list[PluginMetadata]:
        r"""|coro|

        Get the metadata of all plugins that the user has installed

        Returns
        --------
        list[:class:`PluginMetadata`]
        """

        from ..jsonrpc import Result  # circular import

        res = await self.jsonrpc.request("GetAllPlugins")
        assert isinstance(res, Result)
        return [PluginMetadata(plugin["metadata"], self) for plugin in res.data]

    async def add_keyword(self, plugin_id: str, keyword: str) -> None:
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

        from ..jsonrpc import Result  # circular import

        res = await self.jsonrpc.request("AddActionKeyword", [plugin_id, keyword])
        assert isinstance(res, Result)

    async def remove_keyword(self, plugin_id: str, keyword: str) -> None:
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

        from ..jsonrpc import Result  # circular import

        res = await self.jsonrpc.request("RemoveActionKeyword", [plugin_id, keyword])
        assert isinstance(res, Result)

    async def open_directory(self, directory: str, file: str | None = None) -> None:
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

        from ..jsonrpc import Result  # circular import

        res = await self.jsonrpc.request("OpenDirectory", [directory, file])
        assert isinstance(res, Result)

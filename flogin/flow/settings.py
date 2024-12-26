from .base import Base, add_prop
from .enums import (
    AnimationSpeeds,
    LastQueryMode,
    SearchPrecisionScore,
    SearchWindowAligns,
    SearchWindowScreens,
)

Double = (
    int | float
)  # C# doubles are just floats in python, however there is some typemismatch, so some "doubles" are integers.

__all__ = (
    "CustomFileManager",
    "CustomBrowser",
    "CustomPluginHotkey",
    "CustomQueryShortcut",
    "HttpProxy",
    "PartialPlugin",
    "PluginsSettings",
    "FlowSettings",
)


class CustomFileManager(Base):
    """This is a replica of the ``CustomExplorerViewModel`` dataclass in flow.

    This is an entry for a custom file manager, which is under the ``Default File Manager`` option in flow's ui settings.

    Attributes
    -----------
    name: :class:`str`
        The name of the filemanager
    path: :class:`str`
        The path to the filemanager
    file_argument: :class:`str`
        How to tell the filemanager which file to open
    directory_argument: :class:`str`
        How to tell the filemanager which directory to open
    editable: :class:`bool`
        Whether or not the user can edit this entry in the ui
    """

    name: str = add_prop("Name")
    path: str = add_prop("Path")
    file_argument: str = add_prop("FileArgument")
    directory_argument: str = add_prop("DirectoryArgument")
    editable: bool = add_prop("Editable")


class CustomBrowser(Base):
    """This is a replica of the ``CustomBrowserViewModel`` dataclass in flow.

    This represents an entry for a custom browser, which is under the ``Default Web Browser`` option in flow's ui settings.

    Attributes
    -----------
    name: :class:`str`
        The name of the browser
    path: :class:`str`
        The path to the browser's executable
    private_arg: :class:`str`
        The argument that is used to tell the browser to open in incognito/private mode
    enable_private: :class:`bool`
        Whether or not to open the browser in private/incognito mode
    open_in_tab: :class:`bool`
        Whether to open the link in a new tab or browser window
    editable: :class:`bool`
        Whether the user can edit this entry in the ui
    """

    name: str = add_prop("Name")
    path: str = add_prop("Path")
    private_arg: str = add_prop("PrivateArg")
    enable_private: bool = add_prop("EnablePrivate")
    open_in_tab: bool = add_prop("OpenInTab")
    editable: bool = add_prop("Editable")


class CustomPluginHotkey(Base):
    """This is a replica of the ``CustomPluginHotkey`` dataclass in flow.

    Attributes
    -----------
    hotkey: :class:`str`
    keyword: :class:`str`
    """

    hotkey: str = add_prop("Hotkey")
    keyword: str = add_prop("ActionKeyword")


class CustomQueryShortcut(Base):
    """This is a replica of the ``CustomShortcutModel`` dataclass in flow.

    This represents a custom shortcut in flow's config file.

    Attributes
    -----------
    value: :class:`str`
        The shortcut's value, which in the ui is called the ``Expansion``
    key: :class:`str`
        The shortcut's key, which in the ui is called the `Shortcut``
    """

    value: str = add_prop("Value")
    key: str = add_prop("Key")


class HttpProxy(Base):
    """This represents the user's proxy info

    Attributes
    -----------
    enabled: :class:`bool`
        Whether or not the proxy is active
    server: :class:`str` | ``None``
        The proxy's server
    port: :class:`int` | ``None``
        The proxy's port
    username: :class:`str` | ``None``
        The proxy's username
    password: :class:`str` | ``None``
        The proxy's password
    """

    enabled: bool = add_prop("Enabled")
    server: str | None = add_prop("Server")
    port: int | None = add_prop("Port")
    username: str | None = add_prop("UserName")
    password: str | None = add_prop("Password")


class PartialPlugin(Base):
    """This is a partial plugin from flow.

    Attributes
    -----------
    id: :class:`str`
        The plugin's ID
    name: :class:`str`
        The plugin's name
    version: :class:`str`
        The plugin's version
    priority: :class:`int`
        The plugin's priority
    disabled: :class:`bool`
        Whether or not the plugin is disabled
    keywords: list[:class:`str`]
        The plugin's keywords
    """

    id: str = add_prop("ID")
    name: str = add_prop("Name")
    version: str = add_prop("Version")
    priority: int = add_prop("Priority")
    disabled: bool = add_prop("Disabled")
    keywords: list[str] = add_prop("ActionKeywords")


class PluginsSettings(Base):
    """This represents the user's plugin settings from the general flow config file.

    Attributes
    -----------
    python_executable: :class:`str`
        The location of the user's python executable. If there is none, this attribute will be an empty string.
    node_executable: :class:`str`
        The location of the user's node executable. If there is none, this attribute will be an empty string.
    plugins: list[:class:`PartialPlugin`]
        A list of the user's plugins, in partial form.
    """

    python_executable: str = add_prop("PythonExecutablePath")
    node_executable: str = add_prop("NodeExecutablePath")
    plugins: dict[str, PartialPlugin] = add_prop(
        "Plugins", cls=lambda x: [PartialPlugin(value) for value in x.values()]
    )


class FlowSettings(Base):
    """This is a class which represents the settings that flow launcher saves in config files.

    Attributes
    -----------
    hotkey: :class:`str`
    open_result_modifiers: :class:`str`
    color_scheme: :class:`str`
    show_open_result_gotkey: :class:`bool`
    window_size: :class:`int` | :class:`float`
    preview_hotkey: :class:`str`
    autocomplete_hotkey: :class:`str`
    autocomplete_hotkey_2: :class:`str`
    select_next_item_hotkey: :class:`str`
    select_next_item_hotkey_2: :class:`str`
    select_previous_item_hotkey: :class:`str`
    select_previous_item_hotkey_2: :class:`str`
    select_next_page_hotkey: :class:`str`
    select_previous_page_hotkey: :class:`str`
    open_context_menu_hotkey: :class:`str`
    setting_window_hotkey: :class:`str`
    cycle_history_up_hotkey: :class:`str`
    cycle_history_down_hotkey: :class:`str`
    language: :class:`str`
    theme: :class:`str`
    use_drop_shadow_effect: :class:`bool`
    window_height_size: :class:`int` | :class:`float`
    item_height_size: :class:`int` | :class:`float`
    query_box_font_size: :class:`int` | :class:`float`
    result_item_font_size: :class:`int` | :class:`float`
    result_sub_item_font_size: :class:`int` | :class:`float`
    query_box_font: :class:`str` | ``None``
    query_box_font_style: :class:`str` | ``None``
    query_box_font_weight: :class:`str` | ``None``
    query_box_font_stretch: :class:`str` | ``None``
    result_font: :class:`str` | ``None``
    result_font_style: :class:`str` | ``None``
    result_font_weight: :class:`str` | ``None``
    result_font_stretch: :class:`str` | ``None``
    result_sub_font: :class:`str` | ``None``
    result_sub_font_style: :class:`str` | ``None``
    result_sub_font_weight: :class:`str` | ``None``
    result_sub_font_stretch: :class:`str` | ``None``
    use_glyph_icons: :class:`bool`
    use_animation: :class:`bool`
    use_sound: :class:`bool`
    sound_volume: :class:`int` | :class:`float`
    use_clock: :class:`bool`
    use_date: :class:`bool`
    time_format: :class:`str`
    date_format: :class:`str`
    first_launch: :class:`bool`
    setting_window_width: :class:`int` | :class:`float`
    setting_window_height: :class:`int` | :class:`float`
    setting_window_top: :class:`int` | :class:`float` | None
    setting_window_left: :class:`int` | :class:`float` | None
    setting_window_state: :class:`int`
    custom_explorer_index: :class:`int`
    custom_explorer_list: list[:class:`CustomFileManager`]
    custom_browser_index: :class:`int`
    custom_browser_list: list[:class:`CustomBrowser`]
    should_use_pinyin: :class:`bool`
    always_preview: :class:`bool`
    always_start_en: :class:`bool`
    query_search_precision: :class:`SearchPrecisionScore`
    auto_updates: :class:`bool`
    window_left: :class:`int` | :class:`float`
    window_top: :class:`int` | :class:`float`
    custom_window_left: :class:`int` | :class:`float`
    custom_window_top: :class:`int` | :class:`float`
    keep_max_results: :class:`bool`
    max_results_to_show: :class:`int`
    activate_times: :class:`int`
    custom_plugin_hotkeys: list[:class:`CustomPluginHotkey`]
    custom_shortcuts: list[:class:`CustomQueryShortcut`]
    dont_prompt_update_msg: :class:`bool`
    enable_update_log: :class:`bool`
    start_flow_launcher_on_system_startup: :class:`bool`
    hide_on_startup: :class:`bool`
    hide_notify_icon: :class:`bool`
    leave_cmd_open: :class:`bool`
    hide_when_deactivated: :class:`bool`
    search_window_screen: :class:`SearchWindowScreens`
    search_window_align: :class:`SearchWindowAligns`
    custom_screen_number: :class:`int`
    ignore_hotkeys_on_fullscreen: :class:`bool`
    proxy: :class:`HttpProxy`
    last_query_mode: :class:`LastQueryMode`
    animation_speed: :class:`AnimationSpeeds`
    custom_animation_length: :class:`int`
    plugin_settings: :class:`PluginsSettings`
    """

    hotkey: str = add_prop("Hotkey")
    open_result_modifiers: str = add_prop("OpenResultModifiers")
    color_scheme: str = add_prop("ColorScheme")
    show_open_result_gotkey: bool = add_prop("ShowOpenResultHotkey")
    window_size: Double = add_prop("WindowSize")
    preview_hotkey: str = add_prop("PreviewHotkey")
    autocomplete_hotkey: str = add_prop("AutoCompleteHotkey")
    autocomplete_hotkey_2: str = add_prop("AutoCompleteHotkey2")
    select_next_item_hotkey: str = add_prop("SelectNextItemHotkey")
    select_next_item_hotkey_2: str = add_prop("SelectNextItemHotkey2")
    select_previous_item_hotkey: str = add_prop("SelectPrevItemHotkey")
    select_previous_item_hotkey_2: str = add_prop("SelectPrevItemHotkey2")
    select_next_page_hotkey: str = add_prop("SelectNextPageHotkey")
    select_previous_page_hotkey: str = add_prop("SelectPrevPageHotkey")
    open_context_menu_hotkey: str = add_prop("OpenContextMenuHotkey")
    setting_window_hotkey: str = add_prop("SettingWindowHotkey")
    cycle_history_up_hotkey: str = add_prop("CycleHistoryUpHotkey")
    cycle_history_down_hotkey: str = add_prop("CycleHistoryDownHotkey")
    language: str = add_prop("Language")
    theme: str = add_prop("Theme")
    use_drop_shadow_effect: bool = add_prop("UseDropShadowEffect")
    window_height_size: Double = add_prop("WindowHeightSize")
    item_height_size: Double = add_prop("ItemHeightSize")
    query_box_font_size: Double = add_prop("QueryBoxFontSize")
    result_item_font_size: Double = add_prop("ResultItemFontSize")
    result_sub_item_font_size: Double = add_prop("ResultSubItemFontSize")
    query_box_font: str | None = add_prop("QueryBoxFont")
    query_box_font_style: str | None = add_prop("QueryBoxFontStyle")
    query_box_font_weight: str | None = add_prop("QueryBoxFontWeight")
    query_box_font_stretch: str | None = add_prop("QueryBoxFontStretch")
    result_font: str | None = add_prop("ResultFont")
    result_font_style: str | None = add_prop("ResultFontStyle")
    result_font_weight: str | None = add_prop("ResultFontWeight")
    result_font_stretch: str | None = add_prop("ResultFontStretch")
    result_sub_font: str | None = add_prop("ResultSubFont")
    result_sub_font_style: str | None = add_prop("ResultSubFontStyle")
    result_sub_font_weight: str | None = add_prop("ResultSubFontWeight")
    result_sub_font_stretch: str | None = add_prop("ResultSubFontStretch")
    use_glyph_icons: bool = add_prop("UseGlyphIcons")
    use_animation: bool = add_prop("UseAnimation")
    use_sound: bool = add_prop("UseSound")
    sound_volume: Double = add_prop("SoundVolume")
    use_clock: bool = add_prop("UseClock")
    use_date: bool = add_prop("UseDate")
    time_format: str = add_prop("TimeFormat")
    date_format: str = add_prop("DateFormat")
    first_launch: bool = add_prop("FirstLaunch")
    setting_window_width: Double = add_prop("SettingWindowWidth")
    setting_window_height: Double = add_prop("SettingWindowHeight")
    setting_window_top: Double | None = add_prop("SettingWindowTop", default=None)
    setting_window_left: Double | None = add_prop("SettingWindowLeft", default=None)
    setting_window_state: int = add_prop("SettingWindowState")
    custom_explorer_index: int = add_prop("CustomExplorerIndex")
    custom_explorer_list: list[CustomFileManager] = add_prop(
        "CustomExplorerList", cls=CustomFileManager, is_list=True
    )
    custom_browser_index: int = add_prop("CustomBrowserIndex")
    custom_browser_list: list[CustomBrowser] = add_prop(
        "CustomBrowserList", cls=CustomBrowser, is_list=True
    )
    should_use_pinyin: bool = add_prop("ShouldUsePinyin")
    always_preview: bool = add_prop("AlwaysPreview")
    always_start_en: bool = add_prop("AlwaysStartEn")
    query_search_precision: SearchPrecisionScore = add_prop(
        "QuerySearchPrecision", cls=lambda x: SearchPrecisionScore[x.lower()]
    )
    auto_updates: bool = add_prop("AutoUpdates")
    window_left: Double = add_prop("WindowLeft")
    window_top: Double = add_prop("WindowTop")
    custom_window_left: Double = add_prop("CustomWindowLeft")
    custom_window_top: Double = add_prop("CustomWindowTop")
    keep_max_results: bool = add_prop("KeepMaxResults")
    max_results_to_show: int = add_prop("MaxResultsToShow")
    activate_times: int = add_prop("ActivateTimes")
    custom_plugin_hotkeys: list[CustomPluginHotkey] = add_prop(
        "CustomPluginHotkeys", cls=CustomPluginHotkey, is_list=True
    )
    custom_shortcuts: list[CustomQueryShortcut] = add_prop(
        "CustomShortcuts", cls=CustomQueryShortcut, is_list=True
    )
    dont_prompt_update_msg: bool = add_prop("DontPromptUpdateMsg")
    enable_update_log: bool = add_prop("EnableUpdateLog")
    start_flow_launcher_on_system_startup: bool = add_prop(
        "StartFlowLauncherOnSystemStartup"
    )
    hide_on_startup: bool = add_prop("HideOnStartup")
    hide_notify_icon: bool = add_prop("HideNotifyIcon")
    leave_cmd_open: bool = add_prop("LeaveCmdOpen")
    hide_when_deactivated: bool = add_prop("HideWhenDeactivated")
    search_window_screen: SearchWindowScreens = add_prop(
        "SearchWindowScreen", cls=SearchWindowScreens
    )
    search_window_align: SearchWindowAligns = add_prop(
        "SearchWindowAlign", cls=SearchWindowAligns
    )
    custom_screen_number: int = add_prop("CustomScreenNumber")
    ignore_hotkeys_on_fullscreen: bool = add_prop("IgnoreHotkeysOnFullscreen")
    proxy: HttpProxy = add_prop("Proxy", cls=HttpProxy)
    last_query_mode: LastQueryMode = add_prop("LastQueryMode", cls=LastQueryMode)
    animation_speed: AnimationSpeeds = add_prop("AnimationSpeed", cls=AnimationSpeeds)
    custom_animation_length: int = add_prop("CustomAnimationLength")
    plugin_settings: PluginsSettings = add_prop("PluginSettings", cls=PluginsSettings)

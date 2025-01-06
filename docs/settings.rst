.. currentmodule:: flogin

Plugin Settings
===============

For your plugin to have settings, you need to make a ``SettingsTemplate.yaml`` file.

SettingsTemplate.yaml
---------------------

The ``SettingsTemplate.yaml`` file is how to tell flow what settings to display in the settings menu.

- `Flow Launcher Guide on SettingsTemplate.yaml <https://www.flowlauncher.com/docs/#/json-rpc-settings?id=settingstemplateyaml>`__
- `JSON Schema <https://www.flowlauncher.com/schemas/settings-template.schema.json>`__

Settings API
------------
To access the settings from your plugin, you can use the :attr:`flogin.plugin.Plugin.settings` attribute to get a :class:`~flogin.settings.Settings` instance, which you will use to access your plugin's settings.

Typing
~~~~~~
To add proper typing to your settings instance, create a subclass of :class:`~flogin.settings.Settings` and add your settings. Example:

.. code-block:: python3
    :linenos:

    from flogin import Settings

    class MySettings(Settings):
        my_setting: str | None

To register your subclass, pass it as a generic argument to your plugin. For example:

.. code-block:: python3
    :linenos:

    from flogin import Plugin
    from settings import MySettings # import my new settings object

    class MyPlugin(Plugin[MySettings]):
        ...

or as an instance:

.. code-block:: python3
    :linenos:

    plugin: Plugin[MySettings] = Plugin(...)
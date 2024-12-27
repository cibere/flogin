Whats New
==========

This page keeps a detailed human friendly rendering of what's new and changed in specific versions.

v0.1.0
------

Breaking Changes
~~~~~~~~~~~~~~~~

- Move :class:`flogin.jsonrpc.results.Glyph` support from :attr:`flogin.jsonrpc.results.Result.icon` to :class:`flogin.jsonrpc.results.Result.gylph`
- Return ``None`` if a setting is not found in :class:`flogin.settings.Setting`
    - Remove ``flogin.errors.SettingNotFound``
- Rewrite the CLI commands
- Remove ``flogin.conditions.MultiCondition`` in favor of :class:`flogin.conditions.AnyCondition` and :class:`flogin.conditions.AllCondition`
- Remove `Query.from_json`
- For :func:`flogin.testing.plugin_tester.PluginTester.test_query`, switch from receiving a query object to taking kwargs that will be used to make a query object
- Rename the ``flogin.flow_api`` directory to ``flogin.flow``
    - Rename ``flogin.flow_api.client.py`` to ``flogin.flow.api.py``

New Features
~~~~~~~~~~~~

- Add ``Query.__repr__``
- Let :func:`flogin.search_handler.SearchHandler.callback` and :func:`flogin.jsonrpc.results.Result.context_menu` return ``None``
- Add :class:`~typing.Generic` to :class:`flogin.search_handler.SearchHandler` for :attr:`flogin.search_handler.SearchHandler.plugin`
- Add :class:`~typing.Generic` to :class:`flogin.jsonrpc.results.Result` for :attr:`flogin.jsonrpc.results.Result.plugin`
- Update ``Query.__init__`` to allow for an easier time manually creating query objects.
- Add the ability to supply a default into ``flogin.settings.Settings.__getitem__``
- Add a generic to :class:`flogin.plugin.Plugin` for a custom :class:`flogin.settings.Settings` class.
- Document the generic in :class:`flogin.jsonrpc.results.Result` for a custom plugin class.
- Document the generic in :class:`flogin.search_handler.SearchHandler.plugin` for a custom plugin class.
- Document the generic in :class:`flogin.query.Query` for :attr:`flogin.query.Query.condition_data`
- Make :attr:`flogin.jsonrpc.results.Result.title` optional
- Add :class:`flogin.conditions.AnyCondition`
- Add :class:`flogin.conditions.AllCondition`
- Add :func:`flogin.query.Query.update_results`
- Add :func:`flogin.query.Query.update`
- Add ``flogin.flow.settings.py``
    - Add :class:`flogin.flow.settings.CustomFileManager`
    - Add :class:`flogin.flow.settings.CustomBrowser`
    - Add :class:`flogin.flow.settings.CustomPluginHotkey`
    - Add :class:`flogin.flow.settings.CustomQueryShortcut`
    - Add :class:`flogin.flow.settings.HttpProxy`
    - Add :class:`flogin.flow.settings.PartialPlugin`
    - Add :class:`flogin.flow.settings.PluginsSettings`
    - Add :class:`flogin.flow.settings.FlowSettings`
- Add ``flogin.flow.enums.py``
    - Add :class:`flogin.flow.enums.LastQueryMode`
    - Add :class:`flogin.flow.enums.ColorSchemes`
    - Add :class:`flogin.flow.enums.SearchWindowScreens`
    - Add :class:`flogin.flow.enums.SearchWindowAligns`
    - Add :class:`flogin.flow.enums.AnimationSpeeds`
    - Add :class:`flogin.flow.enums.SearchPrecisionScore`
- Add :func:`flogin.plugin.Plugin.fetch_flow_settings`

Bug Fixes
~~~~~~~~~

- Fix bug where :func:`flogin.flow.api.FlowLauncherAPI.update_results` does not register the results, so callbacks do not get triggered.
- Fix typing bug with :func:`flogin.plugin.Plugin.register_search_handlers` and :func:`flogin.plugin.Plugin.register_search_handler` due to :class:`flogin.search_handler.SearchHandler` being a generic.
- Fix bug where ``Glyph`` was not included in ``ResultConstructorArgs``
- Fix bug with the ``PluginT`` TypeVar not being marked as covariant
- Fix bug with the default settings reader looking for the wrong path.

Removals
~~~~~~~~~
- Remove the ``CLI`` docs section
- Remove `click <https://pypi.org/project/click>`__ as a dependency.

v0.0.5
-------

New Features
~~~~~~~~~~~~~

- Add :func:`flogin.plugin.Plugin.register_search_handlers`
- Add the :doc:`whats_new` section in the docs
- Add :func:`flogin.plugin.Plugin.register_event`
- Add ``flogin gh gitignore`` CLI command
- Add :class:`flogin.jsonrpc.results.ResultPreview`
    - Add :attr:`~flogin.jsonrpc.results.Result.preview`
- Add :class:`flogin.jsonrpc.results.ProgressBar`
    - Add :attr:`flogin.jsonrpc.results.Result.progress_bar`
- Add :attr:`flogin.jsonrpc.results.Result.auto_complete_text`
- Add :class:`flogin.jsonrpc.results.Glyph`
    - Allow :class:`~flogin.jsonrpc.results.Glyph` objects in :attr:`flogin.jsonrpc.results.Result.icon`
- Add :attr:`flogin.jsonrpc.results.Result.rounded_icon`
- Add ``flogin create settings`` CLI command
- Add :func:`flogin.utils.cached_gen`

Bug Fixes
~~~~~~~~~

- Fixed bug with the `create plugin.json <cli-create-plugin-json>`_ CLI command dumping the wrong data.
- Add the missing dependency `click <https://pypi.org/project/click/>`__
- Fix bug where :attr:`flogin.search_handler.SearchHandler.plugin` is ``None`` when :obj:`flogin.search_handler.SearchHandler.condition` is ran.
- Fix an ``AttributeError`` that gets raised in a couple of :class:`~flogin.flow.api.FlowLauncherAPI` methods
- Log fatal errors that cause startup crashes to prevent them from being hidden.
- Fix bug where ``rounded_icon`` was not present in ``ResultConstructorArgs``
- Fix a ``NameError`` that gets raised in the default :func:`flogin.jsonrpc.results.Result.callback`
- Fix bug where :attr:`flogin.plugin.Plugin.settings` will be replaced with a new :class:`~flogin.settings.Settings` instance every time a new query request is received, preventing making setting changes.
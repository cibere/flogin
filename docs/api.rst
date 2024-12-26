.. module:: flogin

API Reference
=============

Plugin
------

.. autoclass:: flogin.plugin.Plugin
    :members:

.. autodecorator:: Plugin.event()

.. autodecorator:: Plugin.search()

Classes
~~~~~~~

.. autoclass:: flogin.settings.Settings
    :members:

.. autoclass:: flogin.query.Query
    :members:

JSON RPC
--------

Results
~~~~~~~

.. autoclass:: flogin.jsonrpc.results.Result
    :members:
    
.. autoclass:: flogin.jsonrpc.results.ResultPreview
    :members:

.. autoclass:: flogin.jsonrpc.results.ProgressBar
    :members:
    
.. autoclass:: flogin.jsonrpc.results.Glyph
    :members:

Responses
~~~~~~~~~

.. autoclass:: flogin.jsonrpc.responses.BaseResponse
    :members:

.. autoclass:: flogin.jsonrpc.responses.ErrorResponse
    :members:

.. autoclass:: flogin.jsonrpc.responses.QueryResponse
    :members:

.. autoclass:: flogin.jsonrpc.responses.ExecuteResponse
    :members:

.. _search_handlers_api_reference:

Search Handlers
---------------

.. autoclass:: flogin.search_handler.SearchHandler
    :members:

.. _builtin_search_conditions:

Builtin Search Conditions
~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: flogin.conditions.PlainTextCondition
    :members:

.. autoclass:: flogin.conditions.RegexCondition
    :members:

.. autoclass:: flogin.conditions.KeywordCondition
    :members:

.. autoclass:: flogin.conditions.AllCondition
    :members:

.. autoclass:: flogin.conditions.AnyCondition
    :members:

Flow
-----

API
~~~~

.. autoclass:: flogin.flow.api.FlowLauncherAPI
    :members:

.. autoclass:: flogin.flow.fuzzy_search.FuzzySearchResult
    :members:

.. autoclass:: flogin.flow.plugin_metadata.PluginMetadata
    :members:

Settings
~~~~~~~~~

.. autoclass:: flogin.flow.settings.FlowSettings
    :members:
    :private-members:

.. autoclass:: flogin.flow.settings.CustomQueryShortcut
    :members:

.. autoclass:: flogin.flow.settings.CustomFileManager
    :members:
    :private-members:

.. autoclass:: flogin.flow.settings.CustomBrowser
    :members:
    :private-members:

.. autoclass:: flogin.flow.settings.CustomPluginHotkey
    :members:
    :private-members:

.. autoclass:: flogin.flow.settings.HttpProxy
    :members:
    :private-members:

.. autoclass:: flogin.flow.settings.PartialPlugin
    :members:
    :private-members:

.. autoclass:: flogin.flow.settings.PluginsSettings
    :members:
    :private-members:

.. autoclass:: flogin.flow.settings.LastQueryMode
    :members:
    :private-members:

.. autoclass:: flogin.flow.settings.SearchWindowScreens
    :members:
    :private-members:

.. autoclass:: flogin.flow.settings.SearchWindowAligns
    :members:
    :private-members:

.. autoclass:: flogin.flow.settings.AnimationSpeeds
    :members:
    :private-members:

.. autoclass:: flogin.flow.settings.SearchPrecisionScore
    :members:
    :private-members:

Errors
-----------

Plugin Errors
~~~~~~~~~~~~~

.. autoclass:: flogin.errors.PluginException
    :members:

.. autoclass:: flogin.errors.PluginNotInitialized
    :members:

JSON-RPC Errors
~~~~~~~~~~~~~~~

.. autoclass:: flogin.jsonrpc.errors.JsonRPCException
    :members:

.. autoclass:: flogin.jsonrpc.errors.JsonRPCVersionMismatch
    :members:

.. _testing_module_api_reference:

Testing
-------

.. autoclass:: flogin.testing.plugin_tester.PluginTester
    :members:

Utils
-----

.. autofunction:: flogin.utils.setup_logging

.. autofunction:: flogin.utils.coro_or_gen

.. attribute:: flogin.utils.MISSING

    A type safe sentinel used in the library to represent something as missing. Used to distinguish from ``None`` values.

.. decorator:: flogin.utils.cached_property()

    A version of :func:`functools.cached_property` that is safe for async programs.

    Example
    --------
    .. code-block:: python3

        class Foo:
            @utils.cached_property
            def bar(self):
                ...

.. autodecorator:: flogin.utils.cached_coro()

.. autodecorator:: flogin.utils.cached_gen()
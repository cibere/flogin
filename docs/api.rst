.. module:: flogin

API Reference
=============

The following section outlines the API of flogin.

Version Related Info
---------------------

There are two main ways to query version information about the library. For guarantees, check :ref:`version_guarantees`.

.. data:: version_info

    A named tuple that is similar to :obj:`sys.version_info`.

    Just like :obj:`sys.version_info` the valid values for ``releaselevel`` are
    'alpha', 'beta', 'candidate' and 'final'.

.. data:: __version__

    A string representation of the version. e.g. ``'1.0.0rc1'``. This is based
    off of :pep:`440`.

Plugins
-------

.. attributetable:: flogin.plugin.Plugin

.. autoclass:: flogin.plugin.Plugin
    :members:

Models
-------

Settings
~~~~~~~~

.. attributetable:: flogin.settings.Settings

.. autoclass:: flogin.settings.Settings
    :members:

Query
~~~~~

.. attributetable:: flogin.query.Query

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

.. autoclass:: flogin.errors.EnvNotSet
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

.. _caching_reference:

Caching
-------

.. autodecorator:: flogin.caching.cached_property()

.. autodecorator:: flogin.caching.cached_coro()

.. autodecorator:: flogin.caching.cached_gen()

.. autodecorator:: flogin.caching.cached_callable()

.. autofunction:: flogin.caching.clear_cache
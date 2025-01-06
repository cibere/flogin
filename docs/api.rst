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

.. attributetable:: flogin.jsonrpc.results.Result

.. autoclass:: flogin.jsonrpc.results.Result
    :members:

.. attributetable:: flogin.jsonrpc.results.ResultPreview
    
.. autoclass:: flogin.jsonrpc.results.ResultPreview
    :members:

.. attributetable:: flogin.jsonrpc.results.ProgressBar

.. autoclass:: flogin.jsonrpc.results.ProgressBar
    :members:

.. attributetable:: flogin.jsonrpc.results.Glyph
    
.. autoclass:: flogin.jsonrpc.results.Glyph
    :members:

Responses
~~~~~~~~~

.. attributetable:: flogin.jsonrpc.responses.ErrorResponse

.. autoclass:: flogin.jsonrpc.responses.ErrorResponse
    :members:

.. attributetable:: flogin.jsonrpc.responses.QueryResponse

.. autoclass:: flogin.jsonrpc.responses.QueryResponse
    :members:

.. attributetable:: flogin.jsonrpc.responses.ExecuteResponse

.. autoclass:: flogin.jsonrpc.responses.ExecuteResponse
    :members:

.. _search_handlers_api_reference:

Search Handlers
---------------

.. attributetable:: flogin.search_handler.SearchHandler

.. autoclass:: flogin.search_handler.SearchHandler
    :members:

.. _builtin_search_conditions:

Builtin Search Conditions
~~~~~~~~~~~~~~~~~~~~~~~~~

.. attributetable:: flogin.conditions.PlainTextCondition

.. autoclass:: flogin.conditions.PlainTextCondition
    :members:

.. attributetable:: flogin.conditions.RegexCondition

.. autoclass:: flogin.conditions.RegexCondition
    :members:

.. attributetable:: flogin.conditions.KeywordCondition

.. autoclass:: flogin.conditions.KeywordCondition
    :members:

.. attributetable:: flogin.conditions.AllCondition

.. autoclass:: flogin.conditions.AllCondition
    :members:

.. attributetable:: flogin.conditions.AnyCondition

.. autoclass:: flogin.conditions.AnyCondition
    :members:

Flow
-----

API
~~~~

.. attributetable:: flogin.flow.api.FlowLauncherAPI

.. autoclass:: flogin.flow.api.FlowLauncherAPI
    :members:

.. attributetable:: flogin.flow.fuzzy_search.FuzzySearchResult

.. autoclass:: flogin.flow.fuzzy_search.FuzzySearchResult
    :members:

.. attributetable:: flogin.flow.plugin_metadata.PluginMetadata

.. autoclass:: flogin.flow.plugin_metadata.PluginMetadata
    :members:

Settings
~~~~~~~~~
.. attributetable:: flogin.flow.settings.FlowSettings

.. autoclass:: flogin.flow.settings.FlowSettings
    :members:
    :private-members:


.. attributetable:: flogin.flow.settings.CustomQueryShortcut

.. autoclass:: flogin.flow.settings.CustomQueryShortcut
    :members:


.. attributetable:: flogin.flow.settings.CustomFileManager

.. autoclass:: flogin.flow.settings.CustomFileManager
    :members:
    :private-members:


.. attributetable:: flogin.flow.settings.CustomBrowser

.. autoclass:: flogin.flow.settings.CustomBrowser
    :members:
    :private-members:


.. attributetable:: flogin.flow.settings.CustomPluginHotkey

.. autoclass:: flogin.flow.settings.CustomPluginHotkey
    :members:
    :private-members:


.. attributetable:: flogin.flow.settings.HttpProxy

.. autoclass:: flogin.flow.settings.HttpProxy
    :members:
    :private-members:


.. attributetable:: flogin.flow.settings.PartialPlugin

.. autoclass:: flogin.flow.settings.PartialPlugin
    :members:
    :private-members:


.. attributetable:: flogin.flow.settings.PluginsSettings

.. autoclass:: flogin.flow.settings.PluginsSettings
    :members:
    :private-members:


.. attributetable:: flogin.flow.settings.LastQueryMode

.. autoclass:: flogin.flow.settings.LastQueryMode
    :members:
    :private-members:


.. attributetable:: flogin.flow.settings.SearchWindowScreens

.. autoclass:: flogin.flow.settings.SearchWindowScreens
    :members:
    :private-members:


.. attributetable:: flogin.flow.settings.SearchWindowAligns

.. autoclass:: flogin.flow.settings.SearchWindowAligns
    :members:
    :private-members:


.. attributetable:: flogin.flow.settings.AnimationSpeeds

.. autoclass:: flogin.flow.settings.AnimationSpeeds
    :members:
    :private-members:


.. attributetable:: flogin.flow.settings.SearchPrecisionScore

.. autoclass:: flogin.flow.settings.SearchPrecisionScore
    :members:
    :private-members:

Errors
-----------

Plugin Errors
~~~~~~~~~~~~~


.. attributetable:: flogin.errors.PluginException

.. autoclass:: flogin.errors.PluginException
    :members:


.. attributetable:: flogin.errors.PluginNotInitialized

.. autoclass:: flogin.errors.PluginNotInitialized
    :members:


.. attributetable:: flogin.errors.EnvNotSet

.. autoclass:: flogin.errors.EnvNotSet
    :members:

JSON-RPC Errors
~~~~~~~~~~~~~~~


.. attributetable:: flogin.jsonrpc.errors.JsonRPCException

.. autoclass:: flogin.jsonrpc.errors.JsonRPCException
    :members:


.. attributetable:: flogin.jsonrpc.errors.JsonRPCVersionMismatch

.. autoclass:: flogin.jsonrpc.errors.JsonRPCVersionMismatch
    :members:

.. _testing_module_api_reference:

Testing
-------


.. attributetable:: flogin.testing.plugin_tester.PluginTester

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
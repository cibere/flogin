:orphan:

.. _intro:

Introduction
==============

This is an introduction to the flogin library, which aims to make it easy for python developers to create advanced plugins for Flow Launcher using it's V2 jsonrpc api.

Prerequisites
-------------

flogin requires Python 3.11 or higher. Python 3.11 is recommended as it matches flow's default embedded Python version.

.. _installing:

Installing
----------

.. note::

    A `Virtual Environment <https://docs.python.org/3/library/venv.html>`__ is recommended to install
    the library.

To install flogin, do the following:

.. code:: sh

    pip install -U flogin

To install the development version, ensure `git <https://git-scm.com/>`_ is installed, then do the following:

.. code:: sh

    pip install git+https://github.com/cibere/flogin

Basic Concepts
---------------

Callbacks
~~~~~~~~~

With flogin's architecture, you'll primarily work with callbacks. A callback is a specific function tied to an object that gets triggered when a corresponding event occurs for that object.

Search handlers
~~~~~~~~~~~~~~~

For handling search/query requests with flogin, you will use :ref:`search handlers <search_handlers>`. See the :ref:`search handlers section <search_handlers>` for an in-depth look at them, but for now, here is a quick version:

You can use the :func:`~flogin.plugin.Plugin.search` decorator to register a search handler, with an async callback. The callback takes a single argument (:class:`~flogin.query.Query`), and returns an :class:`~flogin.jsonrpc.results.Result` object, a list of :class:`~flogin.jsonrpc.results.Result` objects, or anything that will get casted to a string and converted into an :class:`~flogin.jsonrpc.results.Result` object.

.. NOTE::
    Unlike :func:`~flogin.plugin.Plugin.event`, with :func:`~flogin.plugin.Plugin.search` you must call the decorator, as there are optional arguments that could be passed.

.. code:: py
    
    plugin = Plugin()
    
    @plugin.search()
    async def my_search_handler(query):
        return "Hello!"

Results
~~~~~~~

You can use the :class:`~flogin.jsonrpc.results.Result` object constructor to pass most options.

.. NOTE::
    For handling what happens when the result gets clicked or customizing the context menu, subclass the object and override the methods. See :class:`~flogin.jsonrpc.results.Result` for more info. Alternatively, you can use :func:`~flogin.jsonrpc.results.Result.create_with_partial` to create a result with a callback, without subclassing.

.. code:: py
    
    plugin = Plugin()
    
    @plugin.search()
    async def my_search_handler(query):
        return Result(
            title=f"Your text: {query.text}",
            sub="boo",
            copy_text=query.text
        )

Events
~~~~~~

At a low level, flogin revolves around a concept called :ref:`events <events>`. An event is something that you listen for, then respond to. For example, when flow starts and runs your plugin, it will send a :ref:`on_initialization <on_initialization>` event that we can listen for.

A quick example code to showcase this:

.. code:: py

    from flogin import Plugin, Query

    plugin = Plugin()

    @plugin.event
    async def on_initialization():
        # Plugin has started
    
    plugin.run()

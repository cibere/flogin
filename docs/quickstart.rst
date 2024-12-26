:orphan:

.. _quickstart:

Quickstart
============

This page gives a brief introduction to the library. It assumes you have the library installed,
if you don't check the :ref:`installing` portion.

.. NOTE::
    To get yourself familiar with flow, check out their `guide <https://www.flowlauncher.com/docs/#/py-develop-plugins?id=about-flow39s-python-plugins>`_ for creating a plugin with the V1 API

A Minimal Plugin
---------------

Let's make a plugin which compares how similar the user's query is with the word ``Flow``.

.. code-block:: python3
    :linenos:

    from flogin import Plugin, Query

    plugin = Plugin()

    @plugin.search()
    async def compare_results(data: Query):
        result = await plugin.api.fuzzy_search(data.text, "Flow")
        return f"Flow: {result.score}",

    plugin.run()


There's a lot going on here, so let's walk you through it line by line.

1. The first line just imports the library, if this raises a :exc:`ModuleNotFoundError` or :exc:`ImportError`
   then head on over to :ref:`installing` section to properly install.
2. Empty Line to increase readability
3. Now we create an instance of :class:`~flogin.plugin.Plugin`, which will let us work with Flow.
4. Empty Line to increase readability
5. Now, in line 5, we use the :func:`~flogin.plugin.Plugin.search` decorator to create and register a :class:`~flogin.search_handler.SearchHandler` object using the function defined in line 6.
6. Now in line 6, we define our handler's callback, which takes a single argument: ``data`` of the type :class:`~flogin.query.Query`
7. In line 7, we access the :class:`~flogin.flow.api.FlowLauncherAPI` client, and use its :func:`~flogin.flow.api.FlowLauncherAPI.fuzzy_search` method to tell flow to use fuzzy search to compare the two strings inputted. In this case, we are telling Flow to compare whatever the user gave as their query. See :class:`~flogin.query.Query` for more info on working with the query object.
8. We are returning a string that contains our ``Flow`` string and the results score. See the :class:`~flogin.flow.fuzzy_search.FuzzySearchResult` class for more information on using the result object.
9. Empty Line to increase readability
10. Now we call plugin's :class:`~flogin.plugin.Plugin.run` method to start the plugin.

Now although we've just made a plugin, we can't use it yet, because it isn't as simple as running the program.

What's Next?
------------
Here are a couple of good places to go next:

- :doc:`search_handlers`
- :doc:`api`
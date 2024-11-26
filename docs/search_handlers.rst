.. _search_handlers:

Search Handlers
===============
The easy and intuative way of handling query/search requests.

Search Handler Callback
------------------------

.. function:: async def search_handler_callback(query)

    This is an scheme of a basic search handler callback that returns items.

    See the :ref:`registering search handlers section <register_search_handler>` for information on how to register your search handler.

    Flow.py will attemp to convert whatever the callback returns into a list of results. If a dictionary is given, flow.py will try and convert it into an :class:`~flowpy.jsonrpc.results.Result` via :func:`~flowpy.jsonrpc.results.Result.from_dict`
    
    The callback can also be an async iterator, and yield the results.

    :param query: The query data
    :type query: :class:`~flowpy.query.Query`
    :rtype: :class:`~flowpy.jsonrpc.results.Result` | list[:class:`~flowpy.jsonrpc.results.Result`] | dict | str | int | Any
    :yields: :class:`~flowpy.jsonrpc.results.Result` | dict | str | int | Any
    :returns: Flow.py will take the output in whatever form it is in, and try its best to convert it into a list of results. Worst case, it casts the item to a string and handles it accordingly.

.. code:: py

    # Return a string, which gets turned into a result
    async def search_handler_callback_example(query):
        return "This is a string"
    # Flow.py will return a single result to flow launcher, which will look something like this:
    # Result(title="This is a string")

.. code:: py

    # Return a list of strings, which gets turned into a list of strings
    async def search_handler_callback_example(query):
        return ["Foo", "Bar", "Apple", "Pear"]
    # Flow.py will return a list of results to flow launcher, which will look something like this:
    # [
    #   Result(title="Foo"),
    #   Result(title="Bar"),
    #   Result(title="Apple"),
    #   Result(title="Pear"),
    # ]

.. code:: py

    # Return an int, which gets casted to a string and turned into a result.
    async def search_handler_callback_example(query):
        return 25
    # Flow.py will return a single result to flow launcher, which will look something like this:
    # Result(title=str(25))

.. code:: py

    # yield a couple of numbers
    async def search_handler_callback_example(query):
        yield 2
        yield 3
        yield 25
        yield 30
    # Flow.py will return a list of results to flow launcher, which will look something like this:
    # [
    #   Result(title=str(2)),
    #   Result(title=str(3)),
    #   Result(title=str(25)),
    #   Result(title=str(30)),
    # ]

Conditions
-----------

Flow.py uses condition functions to determine which handler should be used on a certain query. A condition function should take a single parameter (:class:`~flowpy.query.Query`), and return a bool. ``True`` means the search handler that this condition is associated with should be used on this query, and ``False`` means that the search handler shouldn't be used on this query. See the :ref:`builtin conditions section <builtin_search_conditions>` of this page's api reference for a list of builtin conditions.

.. _condition_example:

Condition Example
~~~~~~~~~~~~~~~~~

.. function:: def condition(query)

    This is called when flow.py is determining if a certain query handler should be used for a certain query or not.

    :param query: The query that will be give to the search handler
    :type query: :class:`~flowpy.query.Query`
    :rtype: :class:`bool`
    :returns: A bool. ``True`` means the search handler that this condition is associated with should be used on this query, and ``False`` means that the search handler shouldn't be used on this query.

.. _register_search_handler:

Registering Handlers
--------------------

There are 2 main ways to register handlers:

1. :ref:`Using the plugin.search decorator <register_search_handler_by_plugin.search_deco>`

2. :ref:`Subclassing and registering your search handler <subclass_and_register_search_handler>`

.. _register_search_handler_by_plugin.search_deco:

Plugin.search decorator
~~~~~~~~~~~~~~~~~~~~~~~
If you want to create a handler outside of your :class:`~flowpy.plugin.Plugin` class using a decorator, you can use the :func:`~flowpy.plugin.Plugin.search` decorator. ::

    @plugin.search()
    async def my_handler(query: Query):
        return f"Your query was: {query.text}"

.. _subclass_and_register_search_handler:

Subclassing and registering a search handler
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Using the decorator isn't the only weay to create search handlers, you can also subclass the :class:`~flowpy.search_handler.SearchHandler` object and register the handler. ::

    class MyHandler(SearchHandler):
        def __init__(self) -> None:
            super().__init__(condition=PlainTextCondition("egg"))
        
        async def callback(self, query: Query):
            return "You found the easter egg!"
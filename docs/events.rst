.. _events:

Event Reference
================

You can register an event using the :func:`~flogin.plugin.Plugin.event` decorator using your :class:`~flogin.plugin.Plugin` instance. For example: ::

    @plugin.event
    async def on_initialization():
        ...

Alternatively, you can use the :func:`~flogin.plugin.Plugin.register_event` method to manually register events. For example: ::

    async def my_event():
        ...
    
    plugin.register_event(my_event, name="on_initialization")

.. warning::

    All the events must be a |coroutine_link|_. If they aren't, then you might get unexpected
    errors. In order to turn a function into a coroutine they must be ``async def``
    functions.

API Events
----------
These events are serialized versions of the raw api events

.. _on_initialization:

on_initialization
~~~~~~~~~~~~~~~~~~

.. function:: async def on_initialization()

    |coro|
    
    This is called when flow sends the ``initialize`` request, which happens when the plugin gets started for the first time.

.. _on_close:

on_close
~~~~~~~~~

.. function:: async def on_close()

    |coro|

    This is called when flow attempts to gracefully shut down.

    .. WARNING::
        Not sending a response in this event WILL cause flow to deadlock. Any response will do, even and error response.

Error Handling Events
---------------------
These events are triggered by flogin to handle errors

on_error
~~~~~~~~

.. function:: async def on_error(event, error, *args, **kwargs)

    |coro|
    
    This is called when an error occurs inside of another event.

    :param event: The name of the event
    :type event: :class:`str`
    :param error: The error that occured
    :type error: :class:`Exception`
    :param \*args: The positional arguments that were passed to the event
    :param \*\*kwargs: The keyword arguments that were passed to the event
    :returns: Any valid response object for the given event
    :rtype: :class:`~flogin.jsonrpc.responses.ErrorResponse` | :class:`~flogin.jsonrpc.responses.QueryResponse` | :class:`~flogin.jsonrpc.responses.ExecuteResponse`
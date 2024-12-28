.. _faq:

Frequently Asked Questions
===========================

This is a list of Frequently Asked Questions regarding using ``flogin`` and its extension modules. Feel free to suggest a
new question or submit one via pull requests.

Coroutines
------------

Questions regarding coroutines and asyncio belong here.

.. NOTE::
    Credits for the ``Coroutines`` section goes to `discord.py <https://discordpy.readthedocs.io/en/latest/faq.html?highlight=on_error#coroutines>`_

What is a coroutine?
~~~~~~~~~~~~~~~~~~~~~~

A |coroutine_link|_ is a function that must be invoked with ``await`` or ``yield from``. When Python encounters an ``await`` it stops
the function's execution at that point and works on other things until it comes back to that point and finishes off its work.
This allows for your program to be doing multiple things at the same time without using threads or complicated
multiprocessing.

**If you forget to await a coroutine then the coroutine will not run. Never forget to await a coroutine.**

Where can I use ``await``\?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can only use ``await`` inside ``async def`` functions and nowhere else.

What does "blocking" mean?
~~~~~~~~~~~~~~~~~~~~~~~~~~~

In asynchronous programming a blocking call is essentially all the parts of the function that are not ``await``. Do not
despair however, because not all forms of blocking are bad! Using blocking calls is inevitable, but you must work to make
sure that you don't excessively block functions. Remember, if you block for too long then your bot will freeze since it has
not stopped the function's execution at that point to do other things.

A common source of blocking for too long is something like :func:`time.sleep`. Don't do that. Use :func:`asyncio.sleep`
instead. Similar to this example: ::

    # bad
    time.sleep(10)

    # good
    await asyncio.sleep(10)

Another common source of blocking for too long is using HTTP requests with the famous module :doc:`req:index`.
While :doc:`req:index` is an amazing module for non-asynchronous programming, it is not a good choice for
:mod:`asyncio` because certain requests can block the event loop too long. Instead, use the :doc:`aiohttp <aio:index>` library which
is installed on the side with this library.

Consider the following example: ::

    # bad
    r = requests.get('https://httpbin.org/get')
    if r.status_code == 200:
        js = r.json()
        yield Result(f"User Agent: {js['headers']['User-Agent']}")

    # good
    async with aiohttp.ClientSession() as session:
        async with session.get('https://httpbin.org/get') as r:
            if r.status == 200:
                js = await r.json()
                yield Result(f"User Agent: {js['headers']['User-Agent']}")

General
---------

General questions regarding library usage belong here.

Where can I find usage examples?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Example code can be found in the `examples folder <https://github.com/cibere/flogin/tree/master/examples>`_ in the repository.

For live projects that you can use as references for "advanced" plugins, see the following plugins:

- `FirefoxKeywordBookmarks by cibere <https://github.com/cibere/FirefoxKeywordBookmarks>`_

- `WordnikDictionary by cibere <https://github.com/cibere/Flow.Launcher.Plugin.WordNikDictionary>`_ *(The development version uses flogin)*

- `Wordle by cibere <http://github.com/cibere/flow.launcher.plugin.wordle>`_

Where can I get help with using the library?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can ask questions in `flow's official discord server <https://discord.gg/QDbDfUJaGH>`_

.. _highlights: 

How do highlights work?
~~~~~~~~~~~~~~~~~~~~~~~

Highlight data works by marking which characters should be highlighted, by including their index in a list. Take the following string as an example: ``Hello World``. If I wanted to just highlight ``Hello``, the highlight data would be ``(0, 1, 2, 3, 4)``. If I wanted to just highlight ``World``, the highlight data would be ``(6, 7, 8, 9, 10)``. If I just wanted to highlight the vowels, I would do: ``(1, 4, 7)``.

Why are the only supported python versions 3.11 and 3.12?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When a user installs a python plugin, flow prompts them to either locate a python installation or install an embedded version of python. The embedded version of python is 3.11. However, as the user can also install other versions of python, 3.12 is also supported.

Flow Launcher
-------------

Questions related to flogin and flow launcher belong here.

What is the difference between the V1 API and the V2 API?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The V1 API is partially documented, and creates a new instance of the plugin for each query/request. However the V2 API is completely undocumented (which is why I am trying to document flogin as much as possible), and has a single instance for the lifespan of flow itself. This allows for more efficient memory usage and faster response times.
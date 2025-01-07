:orphan:

.. currentmodule:: flogin

.. _quickstart:

Quickstart
============

This page gives a brief introduction to the library and how to use it with flow. It assumes you have the library installed,
if you don't check the :ref:`installing` portion of the intro page.

.. NOTE::
    To get yourself familiar with flow, check out their `guide <https://www.flowlauncher.com/docs/#/py-develop-plugins?id=about-flow39s-python-plugins>`_ for creating a plugin with the V1 API

Setting up your environment
---------------------------

See the :ref:`manual installation instructions <manual_install_instructions>` for instructions on how to find where to create your plugin folder.

Once you have your plugin folder in the right directory, you will need to setup your environment. This guide will go over a simple but manual way of setting up your environment. For a more automated method aimed at more complex plugins, see the :doc:`complex_plugins` page.

.. _pluginjson:

plugin.json
~~~~~~~~~~~
In order for flow to actually register your plugin and know how to run it, you will need a ``plugin.json`` file. `Json Scheme <https://www.flowlauncher.com/schemas/plugin.schema.json>`_ 

Keys
^^^^

.. container::

    .. describe:: ID

        Your plugin's ID, a 32 bit UUID. Can be generated with :func:`uuid.uuid4`
    
    .. describe:: ActionKeyword

        Your plugin's default action keyword (``*`` means no specific action keyword). This is only optional if ``ActionKeywords`` is given.
    
    .. describe:: ActionKeywords

        A list of keywords your plugin uses. This is optional.
    
    .. describe:: Name

        The name of your plugin

    .. describe:: Description
        
        A short description of your plugin
    
    .. describe:: Author
        
        Your github username
    
    .. describe:: Version
        
        The current version of your plugin (e.g. ``1.0.0``). It is important for automatic plugin updates.
    
    .. describe:: Language
        
        The language your plugin is written in. In this case, it should be set to 'python_v2'
    
    .. describe:: Website
        
        The plugin's website. If you don't have a website for it, use your plugin's github repository.
    
    .. describe:: IcoPath
        
        The relative path to your plugin's icon
    
    .. describe:: ExecuteFileName
        
        The python file that flow should execute to start your plugin. Ex: ``main.py``

Example
^^^^^^^

.. code-block:: json

    {
        "ID":"ed0770f8-5a99-493f-833a-93b34657a03a",
        "ActionKeyword":"*",
        "Name":"Example Plugin",
        "Description":"This is an example plugin to show how to use the plugin.json file",
        "Author":"cibere",
        "Version":"1.0.0",
        "Language":"python_v2",
        "Website":"https://github.com/cibere/Flow.Launcher.Plugin.ExamplePlugin",
        "IcoPath": "icon.png",
        "ExecuteFileName":"main.py",
    }

A Minimal Plugin
~~~~~~~~~~~~~~~~

Let's make a plugin which compares how similar the user's query is with the word ``Flow``. Since this is the file that we call :func:`flogin.plugin.Plugin.run` in, this is the file that we should put as the ``ExecuteFileName`` key in our :ref:`plugin.json file <pluginjson>`.

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

Path Additions
~~~~~~~~~~~~~~
When flow runs your plugin, it won't detect your venv and run your plugin through it. Because of this, you will have to add some code to the top of the file you set as the execution file in order to add your packages to path.

.. NOTE::
    Make sure to add these to path before you do anything else.

There are 3 main paths that you will want to add:

1. The parent directory.

| This is so that you can import other files in the same directory.

2. A ``lib`` directory in the same folder as your file.

| This is for when you end up publishing your plugin. Your published plugin will have a copy of its dependencies in the ``lib`` dir.

3. Your venv's site packages directory.

| This is for development, so you can install packages as normal into your venv, and have them run just fine,

.. code-block:: python3

    import os
    import sys

    parent_folder_path = os.path.abspath(os.path.dirname(__file__)) # get the folder that your file is in
    sys.path.append(parent_folder_path) # add the folder to path
    sys.path.append(os.path.join(parent_folder_path, "lib")) # add a 'lib' folder that is in the same dir as your file to path
    sys.path.append(os.path.join(parent_folder_path, "venv", "lib", "site-packages")) # add your venv to path

Final Review
~~~~~~~~~~~~~

To review, you should have a folder for your plugin in your flow plugins folder, with the following files:


**plugin.json**

.. NOTE::
    Ensure the ``ExecuteFileName`` key is set to ``main.py``

.. code-block:: json
    :linenos:

    {
        "ID":"ed0770f8-5a99-493f-833a-93b34657a03a",
        "ActionKeyword":"*",
        "Name":"Example Plugin",
        "Description":"This is an example plugin to show how to use the plugin.json file",
        "Author":"cibere",
        "Version":"1.0.0",
        "Language":"python_v2",
        "Website":"https://github.com/cibere/Flow.Launcher.Plugin.ExamplePlugin",
        "IcoPath": "icon.png",
        "ExecuteFileName":"main.py",
    }

**main.py**

.. code-block:: python3
    :linenos:

    import os
    import sys

    parent_folder_path = os.path.abspath(os.path.dirname(__file__)) # get the folder that your file is in
    sys.path.append(parent_folder_path) # add the folder to path
    sys.path.append(os.path.join(parent_folder_path, "lib")) # add a 'lib' folder that is in the same dir as your file to path
    sys.path.append(os.path.join(parent_folder_path, "venv", "lib", "site-packages")) # add your venv to path

    from flogin import Plugin, Query

    plugin = Plugin()

    @plugin.search()
    async def compare_results(data: Query):
        result = await plugin.api.fuzzy_search(data.text, "Flow")
        return f"Flow: {result.score}",

    plugin.run()

Running your plugin
-------------------
Now that our environment is setup, we can run and test our plugin. If already put your plugin in the correct directory, great. If not, see the :ref:`manual installation instructions <manual_install_instructions>` and make sure that your plugin is in the right place.

After you have your plugin in the right place, which includes a properly configured :ref:`plugin.json <pluginjson>` file and your plugin file, all you have to do is restart flow.
Installing your plugin
======================

Installing
----------

Now that you have your plugin setup and ready to be installed, here are the different ways you can install it:

.. _manual_install_instructions:

Manually
~~~~~~~~

To test your plugin with flow itself, you will have to clone your plugin into your userdata folder. To do this, use the ``UserData`` command with the ``System Commands`` plugin to find your userdata folder, head into the ``Plugins`` folder, create a new folder for your plugin, and clone the contents into it. Then, restart flow for the plugin to be activated and run.

From zip
~~~~~~~~

.. NOTE::
    This is useful when installing a specific version of a plugin from a github release

To install a plugin from a zip file, start by getting a direct url or to it. For example: ``https://github.com/cibere/Flow.Launcher.Plugin.rtfm/releases/download/v0.2.1/Flow.Launcher.Plugin.rtfm.zip`` or ``C:\Users\default.MyPC\Downloads\Flow.Launcher.Plugin.rtfm.zip``. Next run the following command with flow: ::

    pm install <url or path>

so in my case, I would run: ::

    pm install https://github.com/cibere/Flow.Launcher.Plugin.rtfm/releases/download/v0.2.1/Flow.Launcher.Plugin.rtfm.zip

or ::

    pm install C:\Users\default.MyPC\Downloads\Flow.Launcher.Plugin.rtfm.zip
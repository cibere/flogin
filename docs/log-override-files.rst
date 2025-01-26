.. currentmodule:: flogin

Log Override Files
==================
Flogin provides the ability to forcibly disable/enable logs for your plugin based on if certain files are present in the plugin's directory. This check is done during the :ref:`initialization event <on_initialization>`.

.. NOTE::
    The ``disable_log_override_files`` option can be passed to :class:`~flogin.plugin.Plugin` to disable this behavior.

.flogin.debug
-------------

If the ``.flogin.debug`` file is present, then logs will forcibly be enabled using :func:`utils.setup_logging`.

.flogin.prod
-------------

If the ``.flogin.prod`` file is present, then logs will forcibly be disabled, but only if they were setup using :func:`utils.setup_logging`.

Matching
---------

Flogin uses a star pattern at the start of the filename when looking for the files, so you can add whatever prefix you want. For example: ``REMOVE-TO-ENABLE-LOGS.flogin.prod``.
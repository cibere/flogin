flogin
=======

.. image:: https://img.shields.io/github/actions/workflow/status/cibere/flogin/tests.yml?label=tests
    :target: https://github.com/cibere/flogin/actions/workflows/tests.yml
    :alt: Tests Workflow Status
.. image:: https://flogin-coverage.cibere.dev/badges/3.13.svg
    :target: https://flogin-coverage.cibere.dev
    :alt: Coverage Report
.. image:: https://img.shields.io/github/actions/workflow/status/cibere/flogin/build.yml?label=build
    :target: https://github.com/cibere/flogin/actions/workflows/build.yml
    :alt: Build Workflow Status
.. image:: https://img.shields.io/github/actions/workflow/status/cibere/flogin/lint.yml?label=lint
    :target: https://github.com/cibere/flogin/actions/workflows/lint.yml
    :alt: Lint Workflow Status

.. raw:: html

    <br>

.. image:: https://img.shields.io/pypi/v/flogin.svg
    :target: https://pypi.python.org/pypi/flogin
    :alt: PyPI version info
.. image:: https://img.shields.io/pypi/pyversions/flogin.svg
    :target: https://pypi.python.org/pypi/flogin
    :alt: PyPI supported Python versions
.. image:: https://img.shields.io/badge/Documentation-Stable-blue
    :target: https://flogin.cibere.dev/en/stable
    :alt: Stable Documentation
.. image:: https://img.shields.io/badge/Documentation-Dev/Latest-blue
    :target: https://flogin.cibere.dev/en/latest
    :alt: Dev/Latest Documentation

A wrapper for Flow Lancher's V2 jsonrpc api using python, to easily and quickly make **Flo**\ w launcher plu\ **gin**\ s.

.. WARNING::
    This library is still in alpha development, so expect breaking changes

Key Features
-------------

- Modern Pythonic API using ``async`` and ``await``.
- Fully Typed
- Easy to use with an object oriented design

Installing
----------

**Python 3.11 or higher is required**

To install flogin, do the following:

.. code:: sh

    pip install flogin

To install the development version, ensure `git <https://git-scm.com/>`_ is installed, then do the following:

.. code:: sh

    pip install git+https://github.com/cibere/flogin

Basic Example
-------------
.. code:: py

    from flogin import Plugin, Query

    plugin = Plugin()

    @plugin.search()
    async def on_query(data: Query):
        return f"You wrote {data.text}"
    
    plugin.run()

You can find more examples in the examples directory.

Links
------

- `Documentation <https://flogin.readthedocs.io/en/latest/index.html>`_
- `Flow Launcher's Official Discord Server <https://discord.gg/QDbDfUJaGH>`_
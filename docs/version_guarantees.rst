.. _version_guarantees:

Version Guarantees
=====================

The library follows `semantic versioning principles <https://semver.org/>`_. The major version is incremented for incompatible API changes. While we strive to clearly identify breaking changes, the determination can sometimes be complex due to the interconnected nature of API components.

The first thing to keep in mind is that breaking changes only apply to things that are **publicly documented**. If it's not listed in the documentation here then it is not part of the public API and is thus bound to change. This includes attributes that start with an underscore or functions without an underscore that are not documented.

.. note::

    The examples below are non-exhaustive.

Examples of Breaking Changes
------------------------------

- Changing the default parameter value to something else.
- Renaming a function without an alias to an old function.
- Adding or removing parameters to an event.

Examples of Non-Breaking Changes
----------------------------------

- Adding or removing private underscored attributes.
- Adding an element into the ``__slots__`` of a data class.
- Changing the behaviour of a function to fix a bug.
- Changes in the typing behaviour of the library
- Changes in the calling convention of functions that are primarily meant as callbacks
- Changes in the documentation.
- Modifying the internal HTTP handling.
- Upgrading the dependencies to a new version, major or otherwise.


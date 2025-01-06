# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import re
import sys
from datetime import date

project = "flogin"

# source:
# https://github.com/Rapptz/discord.py/blob/61eddfcb189f11a293011d43b09fe4ec52641dd2/docs/conf.py#L95C1-L100C18
version = "0.0.0"
author = "Unknown Author"
try:
    with open("../flogin/__init__.py") as f:
        read = f.read()
        version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', read, re.MULTILINE).group(1)  # type: ignore
        author = re.search(r'^__author__\s*=\s*[\'"]([^\'"]*)[\'"]', read, re.MULTILINE).group(1)  # type: ignore
except Exception:
    pass

release = version
author = author

current_year = date.today().year
copyright = f"{current_year}, {author}"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

import os
import sys

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
sys.path.insert(0, os.path.abspath(os.path.join("..", "..")))
sys.path.append(os.path.abspath("extensions"))

extensions = [
    "sphinx.ext.viewcode",  # https://www.sphinx-doc.org/en/master/usage/extensions/viewcode.html
    "sphinx.ext.autodoc",  # https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html
    "sphinx.ext.napoleon",  # https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html
    "sphinx_autodoc_typehints",  # https://github.com/tox-dev/sphinx-autodoc-typehints
    "sphinx.ext.intersphinx",  # https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html
    "sphinx_toolbox.more_autodoc.typevars",  # https://sphinx-toolbox.readthedocs.io/en/latest/extensions/more_autodoc/typevars.html
    "sphinxcontrib_trio",  # https://sphinxcontrib-trio.readthedocs.io/en/latest/
    "nitpick_file_ignorer",
    "attributetable",
]

rst_prolog = """
.. |coro| replace:: This function is a |coroutine_link|_.
.. |maybecoro| replace:: This function *could be a* |coroutine_link|_.
.. |coroutine_link| replace:: *coroutine*
.. _coroutine_link: https://docs.python.org/3/library/asyncio-task.html#coroutine
"""


templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"
html_static_path = ["_static"]
html_css_files = [
    "style.css",
]
html_js_files = [
    "custom.js",
]


# autodoc
# https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#
autodoc_typehints_format = "short"
autodoc_typehints = "none"
autodoc_typehints_description_target = "all"
autodoc_mock_imports = ["typing"]
autodoc_default_options = {"exclude-members": "__init__", "special-members": ""}

# sphinx.ext.napoleon
napoleon_google_docstring = False
napoleon_use_rtype = False

# sphinx_autodoc_typehints
typehints_document_rtype = False
typehints_defaults = "braces"
simplify_optional_unions = False

# sphinx_toolbox.more_autodoc.typevars
all_typevars = False

# intersphinx
# https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "req": ("https://requests.readthedocs.io/en/latest/", None),
    "aio": ("https://docs.aiohttp.org/en/stable/", None),
}

# https://pradyunsg.me/furo/customisation/announcement/
html_theme_options = {
    "announcement": (
        "<b>In Developement</b> Please note that this extension is still in developement. "
        "If you find any bugs, please report them om the <a href='https://github.com/cibere/flogin/issues'>GitHub repository</a>."
    ),
}

# Nitpicky mode options
nitpick_ignore_files = [
    "whats_new",
]

# Typehints are wonky for some reason, and errors/warnings get raised. This workaround just ignores the errors
# https://github.com/sphinx-doc/sphinx/issues/10785
nitpick_ignore = [
    ("py:class", "flogin.query.T"),
    ("py:class", "SearchHandlerCallbackReturns"),
    (
        "py:class",
        "pathlib._local.Path",
    ),  # this gets resolved just fine, but an error still gets thrown for some reason
]

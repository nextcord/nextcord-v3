# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys

sys.path.insert(0, os.path.abspath(".."))
sys.path.append(os.path.abspath("./extensions"))
sys.path.append(os.path.abspath("./_pygments"))


# theme
import furo

from nextcord import __version__


# -- Project information -----------------------------------------------------

project = "nextcord"
copyright = "2021, vcokltfre & tag-epic"
author = "vcokltfre & tag-epic"

# The full version, including alpha/beta/rc tags
release = __version__

branch = "master" if "a" in __version__ else "v" + __version__


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named "sphinx.ext.*") or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "attributetable",
    "exception_hierarchy",
    "resourcelinks",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

autodoc_default_options = {"members": True, "show-inheritance": True}

# TODO: uncomment on requirements.txt
# with open("../requirements.txt") as f:
#     autodoc_mock_imports = f.readlines()


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "furo"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]


html_logo = "_static/padded_logo.png"
html_favicon = "_static/logo.ico"
pygments_style = "light.CustomLightStyle"
pygments_dark_style = "dark.CustomDarkStyle"
default_dark_mode = True


rst_prolog = """
.. |coro| replace:: This function is a |coroutine_link|_.\n\n
.. |maybecoro| replace:: This function *could be a* |coroutine_link|_.
.. |coroutine_link| replace:: *coroutine*
.. _coroutine_link: https://docs.python.org/3/library/asyncio-task.html#coroutine
.. |default| raw:: html

    <div class="default-value-section"> <span class="default-value-label">Default:</span>
"""


# The suffix of source filenames.
source_suffix = ".rst"


add_module_names = False

autodoc_typehints = "none"

autodoc_member_order = "alphabetical"


resource_links = {
    "discord": "https://discord.gg/nextcord",
    "issues": "https://github.com/nextcord-v3/issues",
    "discussions": "https://github.com/nextcord-v3/discussions",
    "examples": f"https://github.com/nextcord-v3/tree/{branch}/examples",
}

intersphinx_mapping = {
    "py": ("https://docs.python.org/3", None),
    "aiohttp": ("https://docs.aiohttp.org/en/stable/", None),
}

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
sys.path.insert(0, os.path.abspath('../.'))

# -- Project information -----------------------------------------------------

project = 'GreedyBoy'
html_title= 'GreedyBoy'
copyright = '2021, Kevin Pruvost'
author = 'Kevin Pruvost'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.githubpages',
    'sphinx.ext.autodoc',
    'sphinx.ext.mathjax',
#    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinxemoji.sphinxemoji',
    'rinoh.frontend.sphinx'
]

autosummary_generate = True
autoclass_content = "class"

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
# source_suffix = ['.rst', '.md']
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
import insegel
html_theme = 'sphinx_material'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']
html_logo = "_static/eye.png"
html_favicon = "_static/eye.ico"

html_copy_source = True
html_show_sourcelink = True
html_sidebars = {
    "**": ["logo-text.html", "globaltoc.html", "localtoc.html", "searchbox.html"]
}
html_theme_options = {
    "base_url": "http://bashtage.github.io/sphinx-material/",
    "repo_url": "https://github.com/kevinpruvost/GreedyBoy/",
    "repo_name": "GreedyBoy",
    "html_minify": False,
    "html_prettify": True,
    "css_minify": True,
    "repo_type": "github",
    "globaltoc_depth": 2,
    "color_primary": "yellow",
    "color_accent": "amber",
    "touch_icon": "eye.png",
    "theme_color": "#219600",
    "master_doc": False,
    "nav_links": [
        {
            "href": "index",
            "internal": True,
            "title": "Main Page"
        },
        {
            "href": "https://github.com/kevinpruvost/GreedyBoy/",
            "internal": False,
            "title": "Github",
        },
    ],
    "heroes": {
        "index": "A Trading Bot to get rid of all the stress of manual trading.",
        "customization": "Configuration options to personalize your site.",
    },
    "version_dropdown": False,
    "version_json": "_static/versions.json",
    "version_info": {
        "Release": "https://bashtage.github.io/sphinx-material/",
        "Development": "https://bashtage.github.io/sphinx-material/devel/",
        "Release (rel)": "/sphinx-material/",
        "Development (rel)": "/sphinx-material/devel/",
    },
    "table_classes": ["plain"],
}

latex_elements = {
    'papersize': 'letterpaper',
    'pointsize': '10pt',
    'preamble': '',
    'figure_align': 'htbp'
}

def setup(app):
    app.add_object_type(
        'confval',  # directivename
        'confval',  # rolename
        'pair: %s; configuration value',  # indextemplate
    )
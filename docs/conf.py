# -*- coding: utf-8 -*-
# pylint: disable=invalid-name

"""Sphinx documentation build configuration file"""

import sphinx_rtd_theme
import fontlib

project   = 'fontlib'
copyright = fontlib.__copyright__
version   = fontlib.__version__
release   = fontlib.__version__

#highlight_language = 'guess'

intersphinx_mapping = {}
# usage:    :ref:`comparison manual <python:comparisons>`
intersphinx_mapping['python']  = ('https://docs.python.org/', None)
intersphinx_mapping['fspath']  = ('https://return42.github.io/fspath/', None)
intersphinx_mapping['sqlalchemy']  = ('https://docs.sqlalchemy.org/', None)

# disable tls_verify for intersphinx url's with self signed certifacates
# tls_verify = False

extlinks = {}
extlinks['origin']    = ('https://github.com/return42/fontlib/blob/master/%s', 'git')
extlinks['commit']    = ('https://github.com/return42/fontlib/commit/%s', '#')

show_authors = True
master_doc = 'index'
templates_path = ['_templates']
exclude_patterns = ['_build', 'slides']

extensions = [
    'sphinx.ext.autodoc'
    , 'sphinx.ext.extlinks'
    #, 'sphinx.ext.autosummary'
    #, 'sphinx.ext.doctest'
    , 'sphinx.ext.todo'
    , 'sphinx.ext.coverage'
    #, 'sphinx.ext.pngmath'
    #, 'sphinx.ext.mathjax'
    , 'sphinx.ext.viewcode'
    , 'sphinx.ext.intersphinx'
    , 'sphinxcontrib.programoutput'
]

html_theme = "sphinx_rtd_theme"
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
html_static_path = ["../utils/sphinx-static"]
html_context = {
    'css_files': [
        '_static/theme_overrides.css',
    ],
}
html_logo = 'darmarIT_logo_128.png'

# http://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html
autoclass_content = 'both'
autodoc_member_order = 'groupwise'

todo_include_todos = True

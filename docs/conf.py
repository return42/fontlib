# -*- coding: utf-8 -*-
# pylint: disable=invalid-name

"""Sphinx documentation build configuration file"""

import os, sys
import fontlib.__pkginfo__ as PKG

from pallets_sphinx_themes import ProjectLink

project    = 'fontlib'
copyright  = PKG.copyright
version    = PKG.version
release    = PKG.version

DOC_URL    = PKG.docs
GIT_URL    = PKG.url
GIT_BRANCH = 'master'

intersphinx_mapping = {}
# usage:    :ref:`comparison manual <python:comparisons>`
intersphinx_mapping['python']  = ('https://docs.python.org/', None)
intersphinx_mapping['fspath']  = ('https://return42.github.io/fspath/', None)
intersphinx_mapping['sqlalchemy']  = ('https://docs.sqlalchemy.org/', None)

# disable tls_verify for intersphinx url's with self signed certifacates
# tls_verify = False

extlinks = {}
extlinks['origin'] = (GIT_URL + '/blob/' + GIT_BRANCH + '/%s', 'git://%s')
extlinks['commit'] = (GIT_URL + '/commit/%s', '#%s')
extlinks['docs'] = (DOC_URL + '/%s', 'docs: %s')
extlinks['pypi'] = ('https://pypi.org/project/%s', 'PyPi: %s')
extlinks['man'] = ('https://manpages.debian.org/jump?q=%s', '%s')

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
    , 'pallets_sphinx_themes'
]

# http://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html
autoclass_content = 'both'
autodoc_member_order = 'groupwise'

todo_include_todos = True

# Sphinx theme

sys.path.append(os.path.abspath('_themes'))
html_theme           = 'custom'
html_logo            = 'darmarIT_logo_128.png'
html_theme_path      = ['_themes']

html_context = {"project_links": [] }
html_context['project_links'].append(ProjectLink('Source', GIT_URL + '/tree/' + GIT_BRANCH))
html_context['project_links'].append(ProjectLink('Issue Tracker', GIT_URL + '/issues'))
html_context['project_links'].append(ProjectLink('Releases', 'https://pypi.org/project/fontlib/'))

html_sidebars = {
    "**": [
        "globaltoc.html",
        "project.html",
        "relations.html",
        "searchbox.html",
        # "sourcelink.html"
    ],
}

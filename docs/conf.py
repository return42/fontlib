# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
"""Sphinx documentation build configuration file"""

import os
import sys
from pallets_sphinx_themes import ProjectLink

from fontlib import __pkginfo__ as PKG
from fontlib import app
from fontlib import googlefont

# build application's context
APP = app.Application()
APP.init()


project    = 'fontlib'
copyright  = PKG.copyright  # pylint: disable=redefined-builtin
version    = PKG.version
release    = PKG.version

DOC_URL    = PKG.docs
GIT_URL    = PKG.url
GIT_BRANCH = 'master'

intersphinx_mapping = {}
# usage:    :ref:`comparison manual <python:comparisons>`
intersphinx_mapping['python']        = ('https://docs.python.org/', None)
intersphinx_mapping['fspath']        = ('https://return42.github.io/fspath/', None)
intersphinx_mapping['sqlalchemy']    = ('https://docs.sqlalchemy.org/', None)

# disable tls_verify for intersphinx url's with self signed certifacates
# tls_verify = False

extlinks = {}
extlinks['origin']   = (GIT_URL + '/blob/' + GIT_BRANCH + '/%s', 'git://%s')
extlinks['commit']   = (GIT_URL + '/commit/%s', '#%s')
extlinks['docs']     = (DOC_URL + '/%s', 'docs: %s')
extlinks['pypi']     = ('https://pypi.org/project/%s', 'PyPi: %s')
extlinks['man']      = ('https://manpages.debian.org/jump?q=%s', '%s')

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
    , 'sphinx_jinja'                    # https://github.com/tardyp/sphinx-jinja
    , 'notfound.extension'              # https://github.com/readthedocs/sphinx-notfound-page
    , 'sphinx_tabs.tabs'                # https://github.com/djungelorm/sphinx-tabs
    , 'linuxdoc.kernel_include'         # https://return42.github.io/linuxdoc/linuxdoc-howto/kernel-include-directive.html
    , 'linuxdoc.rstFlatTable'           # https://return42.github.io/linuxdoc/linuxdoc-howto/table-markup.html#rest-flat-table
    , 'linuxdoc.kfigure'                # https://return42.github.io/linuxdoc/linuxdoc-howto/kfigure.html#kfigure

]

# http://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html
autoclass_content = 'both'
autodoc_member_order = 'groupwise'

todo_include_todos = True
notfound_urls_prefix = '/'

# jinja templating

jinja_contexts = {
    'fontlib': {
        'googlefont' : {
            'font_map' : googlefont.font_map(APP.cfg),
            'GOOGLE_METADATA_FONTS' : googlefont.GOOGLE_METADATA_FONTS,
        }
    },
}

# Sphinx theme

sys.path.append(os.path.abspath('_themes'))

html_theme           = 'custom'
html_logo            = 'darmarIT_logo_128.png'
html_theme_path      = ['_themes']

html_context = {
    'project_links': []
}
html_context['project_links'].append(ProjectLink('Source', GIT_URL + '/tree/' + GIT_BRANCH))
html_context['project_links'].append(ProjectLink('Issue Tracker', GIT_URL + '/issues'))
html_context['project_links'].append(ProjectLink('Releases', 'https://pypi.org/project/fontlib/'))

html_sidebars = {
    '**': [
        'globaltoc.html'
        , 'project.html'
        , 'relations.html'
        , 'searchbox.html'
        # , 'sourcelink.html'
    ],
}

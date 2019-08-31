#!/usr/bin/env python
# -*- coding: utf-8; mode: python -*-
"""
fontlib
"""
import os
from os.path import join as ospj
import io
import imp
from setuptools import setup, find_packages

ROOT   = os.path.abspath(os.path.dirname(__file__))
SRC    = ospj(ROOT, 'fontlib')
DOCS   = ospj(ROOT, 'docs')
TESTS  = ospj(ROOT, 'tests')

PKG = imp.load_source('__pkginfo__', ospj(SRC, '__pkginfo__.py'))

def readFile(fname, mode='rt', encoding='utf-8', newline=None):
    """helper function to read a file"""
    with io.open(fname, mode=mode, encoding=encoding, newline=newline) as f:
        return f.read()

setup(
    name               = PKG.package
    , version          = PKG.version
    , description      = PKG.description
    , long_description = PKG.docstring

    , url              = PKG.url
    , project_urls     = PKG.project_urls

    , author           = PKG.author
    , author_email     = PKG.author_email
    , maintainer       = PKG.maintainer
    , maintainer_email = PKG.maintainer_email

    , license          = PKG.license
    , keywords         = PKG.keywords

    , packages         = find_packages(exclude=['docs', 'tests'])
    , install_requires = PKG.install_requires
    , extras_require   = {
        'dev' : PKG.develop_requires
        , 'test' : PKG.test_requires
    }
    , entry_points     = PKG.get_entry_points()
    , classifiers      = PKG.classifiers
    , package_data     = PKG.package_data
)

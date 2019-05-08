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
README = ospj(ROOT, 'README.rst')
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
    , long_description = readFile(README)
    , url              = PKG.url
    , author           = PKG.authors[0]
    , author_email     = PKG.emails[0]
    , license          = PKG.license
    , keywords         = PKG.keywords
    , packages         = find_packages(exclude=['docs', 'tests'])
    , install_requires = PKG.install_requires
    , entry_points     = PKG.get_entry_points()
    , classifiers      = PKG.classifiers
    , package_data     = PKG.package_data
    )

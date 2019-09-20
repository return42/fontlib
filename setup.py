#!/usr/bin/env python
# -*- coding: utf-8; mode: python -*-
"""
fontlib ``setup.py``

Metadata see ``fontlib/__pkginfo__.py``
"""

import os
from os.path import join as ospj
import imp
from setuptools import setup

ROOT = os.path.abspath(os.path.dirname(__file__))
SRC = ospj(ROOT, 'fontlib')
PKG = imp.load_source('__pkginfo__', ospj(SRC, '__pkginfo__.py'))

# https://packaging.python.org/guides/distributing-packages-using-setuptools/#configuring-your-project
setup(
    name               = PKG.package
    , version          = PKG.version
    , description      = PKG.description
    , long_description = PKG.docstring
    , url              = PKG.url

    , author           = PKG.author
    , author_email     = PKG.author_email
    , maintainer       = PKG.maintainer
    , maintainer_email = PKG.maintainer_email

    , license          = PKG.license
    , classifiers      = PKG.classifiers
    , keywords         = PKG.keywords
    , project_urls     = PKG.project_urls

    , packages         = PKG.packages
    , py_modules       = PKG.py_modules

    , install_requires = PKG.install_requires
    , python_requires  = PKG.python_requires

    , package_data     = PKG.package_data
    , data_files       = PKG.data_files
    , entry_points     = PKG.get_entry_points()

    , extras_require   = {
        # usage: pip install .\[develop,test\]
        # see: https://pip.pypa.io/en/stable/reference/pip_install/#examples
        'develop' : PKG.develop_requires
        , 'test'  : PKG.test_requires
    }

)

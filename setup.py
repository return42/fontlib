#!/usr/bin/env python
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
fontlib ``setup.py``

Metadata see ``fontlib/__pkginfo__.py``
"""

import os
from os.path import join as ospj
import importlib.util
from setuptools import setup

ROOT = os.path.abspath(os.path.dirname(__file__))
SRC = ospj(ROOT, 'fontlib')

_spec = importlib.util.spec_from_file_location('__pkginfo__', ospj(SRC, '__pkginfo__.py'))
PKG = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(PKG)

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
        # - https://pip.pypa.io/en/stable/reference/pip_install/#examples
        # - https://setuptools.readthedocs.io/en/latest/setuptools.html#declaring-extras-optional-features-with-their-own-dependencies
        'develop' : PKG.develop_requires
        , 'test'  : PKG.test_requires
    }

)

# -*- coding: utf-8; mode: python -*-
# pylint: disable=invalid-name,redefined-builtin
"""
python package meta informations used by setup.py

- https://packaging.python.org/guides/distributing-packages-using-setuptools/

"""

package      = 'fontlib'
version      = '20190505'
authors      = ['Markus Heiser', ]
emails       = ['markus.heiser@darmarIT.de', ]
copyright    = '2019 Markus Heiser'
url          = 'https://github.com/return42/fontlib'
description  = 'Pluginable font library'
license      = 'GPLv2'
keywords     = 'fonts TTF OTF WOFF WOFF2 SFNT'
docs         = 'http://return42.github.io/fontlib'
repository   = 'https://github.com/return42/fontlib'
package_data = {'fontlib' : ['cantarell','dejavu']}

python_requires  ='>=3'
install_requires = [
    'fspath'
    , 'tinycss'
]
tests_require = [
    'pylint'
    # , 'tox'
    # , 'pytest'
    # , 'pytest-cov'
    ]

def get_entry_points():
    """get entry points of the python package"""
    return {}

# See https://pypi.python.org/pypi?%3Aaction=list_classifiers
classifiers = [
    "Development Status :: 5 - Production/Stable"
    , "Intended Audience :: Developers"
    , "License :: OSI Approved :: GNU General Public License v2 (GPLv2)"
    , "Operating System :: OS Independent"
    , "Programming Language :: Python"
    , "Programming Language :: Python :: 3"
]

docstring = """
The python fontlib API helps to manage fonts from different resources .

- uses ``entry_points`` where clients plug in fonts
- register MIME types (:py:mod:`mimetypes`) for font types

===========  ===============================================
docs:        %s
repository:  %s
copyright:   %s
e-mail:      %s
license:     %s
===========  ===============================================

""" % (docs, repository, copyright, emails[0], license )


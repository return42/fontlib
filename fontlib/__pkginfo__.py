# -*- coding: utf-8; mode: python; mode: flycheck -*-
# pylint: disable=invalid-name,redefined-builtin
"""
python package meta informations used by setup.py

- https://packaging.python.org/guides/distributing-packages-using-setuptools/

"""

package = 'fontlib'
version = '20190831.1'

copyright = '2019 Markus Heiser'
description = 'Pluginable font library'
license = 'GPLv2'
keywords = 'fonts TTF OTF WOFF WOFF2'

author = 'Markus Heiser'
author_email = 'markus.heiser@darmarIT.de'
authors = [author, ]

maintainer = 'Markus Heiser'
maintainer_email = 'markus.heiser@darmarIT.de'
maintainers = [maintainer, ]

url = 'https://github.com/return42/fontlib'
docs = 'http://return42.github.io/fontlib'
issues = 'https://github.com/return42/fontlib/issues'

project_urls = {
    'Documentation'      : docs
    , 'Code'             : url
    , 'Issue tracker'    : issues
}

package_data = {'fontlib' : ['cantarell','dejavu']}

python_requires  ='>=3.5'

install_requires = [
    'fspath'
    , 'tinycss2'
    , 'requests'
]
install_requires_txt = "\n".join(install_requires)

test_requires = [
    'pylint'
    ]

test_requires_txt = "\n".join(test_requires)

develop_requires = [
    'jedi'
    ,'Sphinx'
    ,'sphinx_rtd_theme'
    ,'sphinx-autobuild'
    ,'sphinxcontrib-programoutput'
    ,'pip'
    , 'twine'
]

develop_requires_txt = "\n".join(develop_requires)

requirements_txt = """# -*- coding: utf-8; mode: conf -*-
# ----------------
# install requires
# ----------------

%(install_requires_txt)s

# -------------
# test requires
# -------------

%(test_requires_txt)s

#tox
#pytest
#pytest-cov

# ----------------
# develop requires
# ----------------

%(develop_requires_txt)s

#wheel
#mock

# sphinxjp.themes.revealjs: slide-shows with revaljs
#
#   comment out next lines, if you don't build slide-shows
#
#git+https://github.com/return42/sphinxjp.themes.revealjs
# -e file:../sphinxjp.themes.revealjs#egg=sphinxjp.themes.revealjs

# -------------------------------
# Packages with font entry points
# -------------------------------
#
# font-amatic-sc
# font-caladea
# font-font-awesome
# font-fredoka-one
# font-hanken-grotesk
# font-intuitive
# font-source-sans-pro
# font-source-serif-pro
""" % globals()

def get_entry_points():
    """get entry points of the python package"""
    return {
        'console_scripts': [
            'fontlib = fontlib.cli:main' # Main fontlib_ console script
        ]}

# See https://pypi.python.org/pypi?%3Aaction=list_classifiers
classifiers = [
    "Development Status :: 5 - Production/Stable"
    , "Intended Audience :: Developers"
    , "License :: OSI Approved :: GNU General Public License v2 (GPLv2)"
    , "Operating System :: OS Independent"
    , "Programming Language :: Python"
    , "Programming Language :: Python :: 3"
    , "Programming Language :: Python :: Implementation :: CPython"
    , "Programming Language :: Python :: Implementation :: PyPy"
    , "Topic :: Software Development :: Libraries :: Application Frameworks"
    , "Topic :: Software Development :: Libraries :: Python Modules"
]

docstring = """
The python `fontlib <%(docs)s>`__ package helps to manage fonts from different
resources.  It comes with an API and the fontlib command line (see `use
<%(docs)s/use.html>`__).  To name just a few fontlib features:

- fontlib ships some `builtin fonts <%(docs)s/builtin.html>`__
- fontlib make use of fonts from `google fonts <%(docs)s/googlefont.html>`__
- fontlib use fonts from `entry points <%(docs)s/ep_points.html>`__
- Python `mimetypes <https://docs.python.org/3/library/mimetypes.html>`__ for font types


Install
=======

Install and update using `pip <https://pip.pypa.io/en/stable/quickstart/>`__:

.. code-block:: text

   pip install -U fontlib


Links
=====

- Documentation:   %(docs)s
- Releases:        https://pypi.org/project/fontlib/
- Code:            %(url)s
- Issue tracker:   %(url)s/issues

============ ===============================================
package:     %(package)s (%(version)s)
copyright:   %(copyright)s
e-mail:      %(maintainer_email)s
license:     %(license)s
============ ===============================================

""" % globals()

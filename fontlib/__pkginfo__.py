# -*- coding: utf-8; mode: python; mode: flycheck -*-
# pylint: disable=invalid-name,redefined-builtin
# pylint: disable=line-too-long
"""Python package meta informations used by setup.py and other project files.

Single point of source for all fontlib package metadata.  After modifying this
file it is needed to recreate some projet files::

  ./local/py3/bin/python -c "from fontlib.__pkginfo__ import *; print(README)" > README.rst
  ./local/py3/bin/python -c "from fontlib.__pkginfo__ import *; print(requirements_txt)" > requirements.txt

About python packaging see `Python Packaging Authority`_.  Most of the names
here are mapped to ``setup(<name1>=..., <name2>=...)`` arguments in
``setup.py``.  See `Packaging and distributing projects`_ about ``setup(...)``
arguments. If this is all new for you, start with `PyPI Quick and Dirty`_.

Further read:

- pythonwheels_
- setuptools_
- packaging_
- sdist_
- installing_

.. _`Python Packaging Authority`: https://www.pypa.io
.. _`Packaging and distributing projects`: https://packaging.python.org/guides/distributing-packages-using-setuptools/
.. _`PyPI Quick and Dirty`: https://hynek.me/articles/sharing-your-labor-of-love-pypi-quick-and-dirty/
.. _pythonwheels: https://pythonwheels.com/
.. _setuptools: https://setuptools.readthedocs.io/en/latest/setuptools.html
.. _packaging: https://packaging.python.org/guides/distributing-packages-using-setuptools/#packaging-and-distributing-projects
.. _sdist: https://packaging.python.org/guides/distributing-packages-using-setuptools/#source-distributions
.. _bdist_wheel: https://packaging.python.org/guides/distributing-packages-using-setuptools/#pure-python-wheels
.. _installing: https://packaging.python.org/tutorials/installing-packages/

"""
# pylint: enable=line-too-long

from setuptools import find_packages

package = 'fontlib'
version = '20230220'

copyright = '2023 Markus Heiser'
description = 'Pluginable font library'
license = 'GPLv3'
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
    # pylint: disable=bad-continuation
    'Documentation'      : docs
    , 'Code'             : url
    , 'Issue tracker'    : issues
}

packages = find_packages(exclude=['docs', 'tests'])

# https://setuptools.readthedocs.io/en/latest/setuptools.html#including-data-files
package_data = {
    'fontlib' : [
        'config.ini'
        , 'log.ini'
        , 'mime.types'

        , 'files/cantarell/COPYING'
        , 'files/cantarell/cantarell.css'
        , 'files/cantarell/*.woff2'

        , 'files/dejavu/LICENSE.html'
        , 'files/dejavu/dejavu.css'
        , 'files/dejavu/DejaVu*.woff2'
    ]
}

# https://docs.python.org/distutils/setupscript.html#installing-additional-files
# https://setuptools.readthedocs.io/en/latest/setuptools.html?highlight=options.data_files#configuring-setup-using-setup-cfg-files
# https://www.scivision.dev/newer-setuptools-needed/
# https://setuptools.readthedocs.io/en/latest/history.html#v40-5-0
data_files = [
    ('/etc/fontlib', [
        'fontlib/config.ini'
        ,  'fontlib/log.ini'
    ])
    , ('/usr/share/doc/fontlib', [
        'README.rst'
        , 'LICENSE.txt'
        , 'fontlib/files/cantarell/COPYING'
        , 'fontlib/files/dejavu/LICENSE.html'
    ])
    , ]

# https://packaging.python.org/guides/distributing-packages-using-setuptools/#python-requires
python_requires  ='>=3.5'

# https://packaging.python.org/guides/distributing-packages-using-setuptools/#py-modules
py_modules = []

# Since pip v18.1 [PEP508-URL] is supported!
#
# Don't use depricated [dependency_links] any more.  See [git+] for using repos
# as packages.  E.g. 'fontlib's master from github with *all extras* is added to
# the requirements by::
#
#        fontlib @ git+https://github.com/return42/fontlib[devel,test]
#
#  The setup.py 'extra_requires' addressed with [PEP-508 extras], here in the
#  example 'devel' and 'test' requirements also installed.
#
# [PEP-508 URL]      https://www.python.org/dev/peps/pep-0508/
# [PEP-508 extras]   https://www.python.org/dev/peps/pep-0508/#extras
# [git+] https://pip.pypa.io/en/stable/reference/pip_install/#vcs-support
# [requirements.txt] https://pip.pypa.io/en/stable/user_guide/#requirements-files
# [dependency_links] https://python-packaging.readthedocs.io/en/latest/dependencies.html

install_requires = [
    'fspath'
    , 'tinycss2'
    , 'requests'
    , 'sqlalchemy'
]
install_requires.sort()
install_requires_txt = "\n".join(install_requires)

test_requires = [
    'pylint'
    ]
test_requires.sort()
test_requires_txt = "\n".join(test_requires)

develop_requires = [
    'jedi' # https://jedi.readthedocs.io/
    , 'Sphinx'
    , 'pallets-sphinx-themes'
    , 'sphinx-autobuild'
    , 'sphinxcontrib-programoutput'
    , 'pip'
    , 'sqlalchemy_schemadisplay @ git+https://github.com/fschulze/sqlalchemy_schemadisplay'
    , 'psycopg2-binary'
    , 'twine'
    , 'argcomplete'
]
develop_requires.sort()
develop_requires_txt = "\n".join(develop_requires)

requirements_txt = """\
%(install_requires_txt)s

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

requirements_dev_txt = """\
%(test_requires_txt)s
%(develop_requires_txt)s
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
    , "License :: OSI Approved :: GNU General Public License v3 (GPLv3)"
    , "Operating System :: OS Independent"
    , "Programming Language :: Python"
    , "Programming Language :: Python :: 3"
    , "Programming Language :: Python :: Implementation :: CPython"
    , "Programming Language :: Python :: Implementation :: PyPy"
    , "Topic :: Software Development :: Libraries :: Application Frameworks"
    , "Topic :: Software Development :: Libraries :: Python Modules"
]

docstring = """\
The python `fontlib <%(docs)s>`__ package helps to manage fonts from different
resources.  It comes with an API and the fontlib command line (see `usage
<%(docs)s/usage/index.html>`__).

To name just a few fontlib features:

- fontlib ships some `builtin fonts <%(docs)s/resources/builtin.html>`__
- fontlib make use of fonts from `google fonts <%(docs)s/resources/googlefont.html>`__
- fontlib use fonts from `entry points <%(docs)s/resources/ep_points.html>`__
- Python `mimetypes <https://docs.python.org/3/library/mimetypes.html>`__ for font types
""" % globals()

README = """\
=======
fontlib
=======

%(docstring)s

Install
=======

Install and update using `pip <https://pip.pypa.io/en/stable/quickstart/>`__
(see :ref:`install`):

.. code-block:: text

   pip install --user -U fontlib

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

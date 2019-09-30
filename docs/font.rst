.. -*- coding: utf-8; mode: rst -*-
.. include:: refs.txt

.. _font:
.. _fontstack:

==================
Font and FontStack
==================

In fontlib's managment a font is identified by its origin URL.  For the
implemtation take a look at class :py:class:`fontlib.font.Font`.  Instances of
class Font are managed in a :py:class:`fontlib.api.FontStack`.  The factory
:py:method:`fontlib.api.FontStack.get_fontstack` can be used to build an
FontStack instance inited from a :py:class:`fontlib.config.Config` object.  See
:ref:`config`, there is a section named ``[fontstack]``.

Source Code Remarks
===================

.. automodule:: fontlib.font
   :noindex:

.. automodule:: fontlib.fontstack
   :noindex:

Further Reading
===============

WOFF2:
  - `WOFF2 W3C Recommendation <https://www.w3.org/TR/WOFF2>`_

OFL fonts:
  - SIL-OFL_
  - `OFL at fontlibrary.org`_

Variable Fonts (VF):
  - `Variable Fonts (css-tricks.com)`_
  - `v-fonts.com <https://v-fonts.com>`_

fonttools:
  Tool for manipulating TrueType and OpenType fonts (`fonttools
  <https://github.com/fonttools/fonttools>`_).

  Install method which uses python3 & installs 'fonttools' and 'brotli'
  compression::

    $ sudo apt-get install python3-dev
    $ pip3 install --user fonttools
    $ git clone https://github.com/google/brotli
    cd brotli
    $ python3 setup.py install --user


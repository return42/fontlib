.. -*- coding: utf-8; mode: rst -*-
.. include:: refs.txt

.. _`builtin_fonts`:

=============
builtin fonts
=============

Some WOFF2 fonts are shipped with :py:mod:`fontlib`.

WOFF2:
  - `W3C Recommendation <https://www.w3.org/TR/WOFF2>`_

OFL fonts:
  - SIL-OFL_
  - `OFL at fontlibrary.org`_

Variable Fonts (VF):
  - `Variable Fonts (css-tricks.com)`_
  - `v-fonts.com <https://v-fonts.com>`_

fonttools:
  Tool for manipulating TrueType and OpenType fonts (`fonttools
  <https://github.com/fonttools/fonttools>`_).  Install method using python3 &
  install fonttools and brotli compression::

    $ sudo apt-get install python3-dev
    $ pip3 install --user fonttools
    $ git clone https://github.com/google/brotli
    cd brotli
    $ python3 setup.py install --user


.. _builtin_cantarell:

Cantarell
=========

WOFF2 format of Cantarell Variable Font TTF (origin)

font
  Cantarell-VT (Variable Font) v0.111 (commit 8cf8f934)

CSS
  `cantarell.css <cantarell/cantarell.css>`_

  - Cantarell

origin
  `GNOME cantarell-fonts`_

license
  `COPYING <cantarell/COPYING>`_

build
  WOFF2 format was generated from the ttf files using ``pyftsubset`` command
  from the fonttools_ lib::

    $ pyftsubset Cantarell-VF.ttf --output-file="Cantarell-VF.woff2"

.. _builtiin_dejavu:

DejaVu
======

.. _dejavu-fonts-ttf-2.37.tar.bz2: https://github.com/dejavu-fonts/dejavu-fonts/releases/download/version_2_37/dejavu-fonts-ttf-2.37.tar.bz2

WOFF2 format of DejaVu TTF (origin)

font
  DejaVu v2.37

CSS
  `dejavu.css <dejavu/dejavu.css>`_

  - DejaVu Sans
  - DejaVu Sans Bold
  - DejaVu Sans Bold Oblique
  - DejaVu Sans Condensed
  - DejaVu Sans Condensed Bold
  - DejaVu Sans Condensed Bold Oblique
  - DejaVu Sans Condensed Oblique
  - DejaVu Sans ExtraLight
  - DejaVu Sans Mono
  - DejaVu Sans Mono Bold
  - DejaVu Sans Mono Bold Oblique
  - DejaVu Sans Mono Oblique
  - DejaVu Sans Oblique
  - DejaVu Serif
  - DejaVu Serif Bold
  - DejaVu Serif Bold Italic
  - DejaVu Serif Condensed
  - DejaVu Serif Condensed Bold
  - DejaVu Serif Condensed Bold Italic
  - DejaVu Serif Condensed Italic
  - DejaVu Serif Italic
  - DejaVu Math TeX Gyre

origin
  `dejavu-fonts-ttf-2.37.tar.bz2`_

license
  `LICENSE.html <./dejavu/LICENSE.html>`_

build
  WOFF2 format was generated from the ttf files using ``pyftsubset`` command
  from the fonttools_ lib::

    # switch into fonts folder and convert ttf to WOFF2
    $ cd dejavu-fonts-ttf-2.37/ttf/
    $ mkdir ../woff2
    $ for ttf in *.ttf; do \
        pyftsubset $ttf --output-file="../woff2/${ttf%.*}.woff2" \
        --unicodes=U+0-10FFFF --layout-features='*' --flavor=woff2; \
      done
    WARNING: FFTM NOT subset; don't know how to subset; dropped
    # ignore warnings about the FontForge time stamp table (FFTM)

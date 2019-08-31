.. -*- coding: utf-8; mode: rst -*-
.. include:: refs.txt

.. _ep_points:

=======================
Fonts from entry points
=======================

Fontlib uses ``entry_points`` to expose fonts that are packaged and distributed
by PyPi_.  Fontlib can use entry points named:

- ``fonts_ttf``
- ``fonts_otf``
- ``fonts_woff``
- ``fonts_woff2``

To install fonts from the fonts-python_ project use pip::

    $ pip install --user \\
          font-amatic-sc font-caladea font-font-awesome \\
          font-fredoka-one font-hanken-grotesk font-intuitive \\
          font-source-sans-pro font-source-serif-pro


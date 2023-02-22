.. -*- coding: utf-8; mode: rst -*-
.. include:: ../refs.txt

.. _googlefont:

============
Google Fonts
============

.. sidebar:: info

   This module does not need a google API key!

.. contents:: Contents
   :depth: 2
   :local:
   :backlinks: entry

.. automodule:: fontlib.googlefont
   :noindex:

``fontlib google``
==================

.. admonition:: fontlib google --help
   :class: rst-example

    .. program-output:: ../local/py3/bin/fontlib google --help


Font Table
==========

.. jinja:: fontlib

   .. flat-table:: Fonts available from {{ googlefont['GOOGLE_METADATA_FONTS'] }}
      :header-rows: 1
      :stub-columns: 1
      :widths: 1 1 9 6 1

      * - No.
	- 🔗
	- Font Family `@font-face`_
        - Category
        - `Noto <https://en.wikipedia.org/wiki/Noto_fonts>`__

      {% for name, item in googlefont['font_map'].items() %}

      * - {{ loop.index }}
	- `🔗 <https://fonts.google.com/specimen/{{ name.replace(' ', '+') }}>`__
	- `{{ name }} <{{ item['css_url'] }}>`__
	- {{ item['category'] }}
        - {{ '✔' if item['noto'] else '' }}

      {% endfor %}


.. hint::

   The table above is a *snapshot* of the moment when this documentation has
   been build.

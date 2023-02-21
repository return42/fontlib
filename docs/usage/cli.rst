.. -*- coding: utf-8; mode: rst -*-
.. include:: ../refs.txt

.. _fontlib_cli:

=======================
The ``fontlib`` command
=======================

.. contents:: Contents
   :depth: 2
   :local:
   :backlinks: entry

.. automodule:: fontlib.cli
   :noindex:

.. admonition:: fontlib --help
   :class: rst-example

   .. program-output:: ../local/py3/bin/fontlib --help

.. _fontlib list:

``fontlib list``
================

.. admonition:: fontlib list --help
   :class: rst-example

   .. program-output:: ../local/py3/bin/fontlib list --help

.. _fontlib css-parse:

``fontlib css-parse``
=====================

With this command fonts can be parsed from `@font-face`_ rules in a CSS file.
With the option ``--register`` the parsed fonts will be registered in the
workspace.

.. admonition:: fontlib css-parse --help
   :class: rst-example

   .. program-output:: ../local/py3/bin/fontlib css-parse --help

.. _fontlib download:

``fontlib download``
====================

.. admonition:: fontlib download --help
   :class: rst-example

   .. program-output:: ../local/py3/bin/fontlib download --help

.. _fontlib config:

``fontlib config``
==================

For more details see :ref:`Config`.

Source Code Remarks
-------------------

.. automodule:: fontlib.config
   :noindex:

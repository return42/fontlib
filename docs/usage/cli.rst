.. -*- coding: utf-8; mode: rst -*-
.. include:: ../refs.txt

.. _fontlib_cli:

=======================
The ``fontlib`` command
=======================

.. automodule:: fontlib.cli
   :noindex:

The fontlib_ library comes with a command line.  Use ``fontlib --help`` for a
basic help.

.. admonition:: fontlib --help
   :class: rst-example

   .. program-output:: ../local/py3/bin/fontlib --help

For a more detailed help to one of the sub commands type::

  $ fontlib <command> --help

.. _fontlib_cli_options:

Fontlib Options
---------------

- ``--verbose``: more verbose output

- ``-c / --config``: :origin:`fontlib/config.ini` (see :ref:`config`)

- ``--workspace``: place where application persists its data

Fontstack options
-----------------

- ``--builtins``: select :ref:`builtin_fonts`

- ``--ep-fonts``: :ref:`ep_points`

- ``--google``: :ref:`googlefont`

fontlib list
============

.. admonition:: fontlib list --help
   :class: rst-example

   .. program-output:: ../local/py3/bin/fontlib list --help


fontlib css-parse
=================

.. admonition:: fontlib css-parse --help
   :class: rst-example

   .. program-output:: ../local/py3/bin/fontlib css-parse --help


fontlib download
================

.. admonition:: fontlib download --help
   :class: rst-example

   .. program-output:: ../local/py3/bin/fontlib download --help


fontlib config
==============

For more details see :ref:`Config`.

Source Code Remarks
-------------------

.. automodule:: fontlib.config
   :noindex:

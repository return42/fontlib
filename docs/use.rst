.. -*- coding: utf-8; mode: rst -*-
.. include:: refs.txt

.. _use:

===
Use
===

The fontlib command
====================

.. automodule:: fontlib.cli
   :noindex:

The fontlib_ library comes with a command line, use ``fontlib --help`` for a
basic help.  For a detailed help to one of the subcommands type ``fontlib``
<command> --help``.

.. program-output:: ../local/py3/bin/fontlib --help

.. _fontlib_cli_options:

Fontlib Options
---------------

- ``--verbose``: more verbose output

- ``-c / --config``: :origin:`fontlib/config.ini` (see :ref:`config`)

- ``--workspace``: place where application persists its data

Fontstack options
-----------------

- ``--builtins``: select :ref:`builtin_fonts`

- ``--ep-fonts``: use fonts from entry points

- ``--google``: select fons from google

fontlib list
------------

.. program-output:: ../local/py3/bin/fontlib list --help


fontlib css-parse
-----------------

.. program-output:: ../local/py3/bin/fontlib css-parse --help


fontlib download
----------------

.. program-output:: ../local/py3/bin/fontlib download --help


fontlib config
--------------

For more details see :ref:`Config`.

Source Code Remarks
===================

.. automodule:: fontlib.config
   :noindex:

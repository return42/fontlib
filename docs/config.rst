.. -*- coding: utf-8; mode: rst -*-
.. include:: refs.txt

.. _config:

======
Config
======

Fontlib can be configured with a configuration file (see `basic config and
logging setup`_) and/or with command line arguments (see :ref:`fontlib options
<fontlib_cli_options>`).  If nothing is given, the `application defaults`_ and
`logging defaults`_ come to the effect.

basic config and logging setup
==============================

To install templates for indiviual configuration use the ``config install``
command::

   $ fontlib config install ~/.fontlib
   using workspace: ~/.fontlib
   set log level of logger: fontlib (WARNING)
   log goes to:
    - <StreamHandler <stderr> (DEBUG)>
   install:  ~/.fontlib/config.ini
   install:  ~/.fontlib/log.ini

This will setup a workspace folder ``.fontlib`` in your home folder where
templates for `application defaults`_ and `logging defaults`_ are copied in.  To
activate the configuration in ``.fontlib/log.ini`` just un-comment the `config`
line:

.. code-block:: ini

   [logging]
   ...
   config = %(workspace)s/log.ini


inspect configuration
=====================

With command ``fontlib config show`` you can inspect current configuration
options.  To show your current configuration use ``fontlib config show``.  With
switch ``--verbose`` you will get some more information.::

  $ fontlib --verbose config show
  using workspace: ~/.fontlib
  set log level of logger: fontlib (WARNING)
  log goes to:
  - <StreamHandler <stderr> (DEBUG)>

  config.ini
  ==========

  [DEFAULT]
  workspace = ~/.fontlib

  [fontstack]
  builtin fonts = cantarell, dejavu
  entry points = fonts_ttf, fonts_otf, fonts_woff, fonts_woff2
  cache = fontlib.urlcache.SimpleURLCache
  ...

  log.ini
  =======

  [loggers]
  keys = root, fontlib
  ...

.. _application defaults:

application defaults
====================

The default application configuration is taken from the
:origin:`fontlib/config.ini` file:

.. literalinclude:: ../fontlib/config.ini
   :language: ini
   :linenos:


logging defaults
================

Fontlib uses the standard py-logging_ facility.  The default logging
configuration is taken from the :origin:`fontlib/log.ini` file (shown
below).  For details options see `py-logging INI format`_.

.. literalinclude:: ../fontlib/log.ini
   :language: ini
   :linenos:


Source Code Remarks
===================

.. automodule:: fontlib.config
   :noindex:

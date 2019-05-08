.. -*- coding: utf-8; mode: rst -*-

==============
Python fontlib
==============

The python fontlib API helps to manage fonts from different resources .

- uses ``entry_points`` where clients plug in fonts
- register MIME types (:py:mod:`mimetypes`) for font types

=============  =======================================
docs:          http://return42.github.io/fontlib
repository:    https://github.com/return42/fontlib
copyright:     2019 Markus Heiser
e-mail:        markus.heiser@darmarIT.de
license:       GPLv2
=============  =======================================

=======
Install
=======

.. code-block:: sh

   pip install [--user] fontlib

For a bleeding edge installation:

.. code-block:: sh

  pip install --user git+http://github.com/return42/fontlib.git

If you are a developer fork/clone from github and run make:

.. code-block:: sh

  git clone https://github.com/return42/fontlib
  cd fontlib
  make install

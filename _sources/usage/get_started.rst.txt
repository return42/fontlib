.. -*- coding: utf-8; mode: rst -*-
.. include:: ../refs.txt

.. _get_started:

===========
get started
===========

The first thing you need to work with fontlib is a *workspace*.  Let's start
with the initialization of a workspace::

  $ fontlib workspace init
  initing workspace at: ~/.fontlib
  load entry point fonts_ttf
  ...
  add ttf // AmaticSCBold // unicode range: -- ...
  load entry point fonts_otf ...
  load entry point fonts_woff ...
  load entry point fonts_woff2 ...
  load CSS file:/path/to/fontlib/fontlib/files/cantarell/cantarell.css ...
  load CSS file:/path/to/fontlib/fontlib/files/dejavu/dejavu.css ...
  load CSS https://fonts.googleapis.com/css?family=Roboto Slab ...
  load CSS https://fonts.googleapis.com/css?family=Staatliches ...
  load CSS https://fonts.googleapis.com/css?family=Libre Barcode 39 Extended Text ...

By default the workspace is created in ``~/.fontlib`` and the configuration from
:ref:`application defaults` are applied.  To see what a default FontStack
consist of use::

  $ fontlib list

What you will see is a list of font families and their file locations (URL):

========== ================= ========== ====================== ===================================================================================
cache sate name              format     font ID                location
========== ================= ========== ====================== ===================================================================================
local      DejaVu Sans Mono  woff2      xfficWNFACPr2phNsNtP1Q file:/path/to/fontlib/fontlib/files/dejavu/DejaVuSansMono.woff2
...        ...               ...        ...                    ...
local      DejaVu Serif      woff2      R3R9kwD3jhPe7B7gEsuQlw file:/path/to/fontlib/fontlib/files/dejavu/DejaVuSerif.woff2
...        ...               ...        ...                    ...
remote     Leckerli One      woff2      yvoLBmviuMkm9D2qqCeF4A https://fonts.gstatic.com/s/leckerlione/v10/V8mCoQH8VCsNttEnxnGQ-1idKpZd.woff2
remote     Leckerli One      truetype   bEENZuBR4lRJicez5ZzF7A https://fonts.gstatic.com/s/leckerlione/v10/V8mCoQH8VCsNttEnxnGQ-1idKpZYJNE9Fg.ttf
...        ...               ...        ...                    ...
remote     Roboto Slab       woff2      Sg1D8MFYhKLwgOr69iIoXQ https://fonts.gstatic.com/s/robotoslab/v9/BngMUXZYTXPIvIBgJJSb6ufA5qW54A.woff2
remote     Roboto Slab       woff2      7rDHs6Nuesbjlzo41NloFQ https://fonts.gstatic.com/s/robotoslab/v9/BngMUXZYTXPIvIBgJJSb6ufJ5qW54A.woff2
remote     Roboto Slab       woff2      gsDhbHcgFsjRqJIs23E7tQ https://fonts.gstatic.com/s/robotoslab/v9/BngMUXZYTXPIvIBgJJSb6ufB5qW54A.woff2
...        ...               ...        ...                    ...
remote     Roboto Slab       truetype   qSYiiwuckE32fKvnEIQaMQ https://fonts.gstatic.com/s/robotoslab/v9/BngMUXZYTXPIvIBgJJSb6ufN5qCr4xCC.ttf
...        ...               ...        ...                    ...
========== ================= ========== ====================== ===================================================================================

In the output, the **name** of the font-family (`CSS @font-face:font-family`_)
is shown and we can see entries with same **name** but different **format**
(`CSS @font-face:src`_).  If both are identical, the different URLs are pointing
to files with different unicode-range (`CSS @font-face:unicode-range`_).  In
column **location** the URL of the origin is shown.  The **font ID** is a
*url-save*, base64 encoding of URL's MD5 digest.  The font ID is nothing you
really need to know, just remember, that there is one which is used fore
internal purpose.

Now lets download font family *Leckerli One*::

  $ fontlib download ~/Downloads "Leckerli One"
  [Leckerli One]: download ~/Downloads/V8mCoQH8VCsNttEnxnGQ-1idKpZd.woff2     from https://fonts.gstatic.com/s/leckerlione/v10/V8mCoQH8VCsNttEnxnGQ-1idKpZd.woff2
  [Leckerli One]: download ~/Downloads/V8mCoQH8VCsNttEnxnGQ-1idKpZYJNE9Fg.ttf from https://fonts.gstatic.com/s/leckerlione/v10/V8mCoQH8VCsNttEnxnGQ-1idKpZYJNE9Fg.ttf
  [Leckerli One]: download ~/Downloads/8qrv1tIC_i-mOkfb29wAlg.svg             from https://fonts.gstatic.com/l/font?kit=V8mCoQH8VCsNttEnxnGQ-1idKpZa&skey=6384c587add2bb80&v=v10#LeckerliOne
  download 3 files into ~/Downloads

If you repeat the ``fontlib list`` after a *download* command you will see that
the downloaded font-family is cached from now on (compare column **cache
state**).  The **location** now points to the **BLOB** located in the cache.

========== ======================================== ==================== ====================== ==========================================================================================
cache sate name                                     format               font ID                location
========== ======================================== ==================== ====================== ==========================================================================================
...        ...                                      ...                  ...                    ...
cached     Leckerli One                             woff2                yvoLBmviuMkm9D2qqCeF4A ~/.fontlib/urlcache/yvoLBmviuMkm9D2qqCeF4A
cached     Leckerli One                             truetype             bEENZuBR4lRJicez5ZzF7A ~/.fontlib/urlcache/bEENZuBR4lRJicez5ZzF7A
...        ...                                      ...                  ...                    ...
========== ======================================== ==================== ====================== ==========================================================================================

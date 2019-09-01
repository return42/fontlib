.. -*- coding: utf-8; mode: rst -*-
.. include:: refs.txt

.. _use:

===
Use
===

The python fontlib_ package helps to manage fonts from different resources.  A
:ref:`Font <font>` itself is identified by its origin URL.  Fonts from various
resources (URLs) are organized in a :ref:`FontStack <fontstack>`.  You can setup
a FontStack individual, but for the first the ``fontlib`` command has some handy
defaults for you.  To see what such a default FontStack consist of use::

  $ fontlib list

========== ======================================== ==================== ====================== ==========================================================================================
cache sate name                                     format               font ID                location
========== ======================================== ==================== ====================== ==========================================================================================
local      DejaVu Sans Mono                         woff2                xfficWNFACPr2phNsNtP1Q file:/x/share/fontlib/fontlib/files/dejavu/DejaVuSansMono.woff2
..
local      DejaVu Serif                             woff2                R3R9kwD3jhPe7B7gEsuQlw file:/x/share/fontlib/fontlib/files/dejavu/DejaVuSerif.woff2
..
remote     Leckerli One                             woff2                yvoLBmviuMkm9D2qqCeF4A https://fonts.gstatic.com/s/leckerlione/v10/V8mCoQH8VCsNttEnxnGQ-1idKpZd.woff2
remote     Leckerli One                             truetype             bEENZuBR4lRJicez5ZzF7A https://fonts.gstatic.com/s/leckerlione/v10/V8mCoQH8VCsNttEnxnGQ-1idKpZYJNE9Fg.ttf
..
remote     Roboto Slab                              woff2                Sg1D8MFYhKLwgOr69iIoXQ https://fonts.gstatic.com/s/robotoslab/v9/BngMUXZYTXPIvIBgJJSb6ufA5qW54A.woff2
remote     Roboto Slab                              woff2                7rDHs6Nuesbjlzo41NloFQ https://fonts.gstatic.com/s/robotoslab/v9/BngMUXZYTXPIvIBgJJSb6ufJ5qW54A.woff2
remote     Roboto Slab                              woff2                gsDhbHcgFsjRqJIs23E7tQ https://fonts.gstatic.com/s/robotoslab/v9/BngMUXZYTXPIvIBgJJSb6ufB5qW54A.woff2
..
remote     Roboto Slab                              truetype             qSYiiwuckE32fKvnEIQaMQ https://fonts.gstatic.com/s/robotoslab/v9/BngMUXZYTXPIvIBgJJSb6ufN5qCr4xCC.ttf
..
========== ======================================== ==================== ====================== ==========================================================================================

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
  [Leckerli One]: download ~/Downloads/V8mCoQH8VCsNttEnxnGQ-1idKpZd.woff2 from https://fonts.gstatic.com/s/leckerlione/v10/V8mCoQH8VCsNttEnxnGQ-1idKpZd.woff2
  [Leckerli One]: download ~/Downloads/V8mCoQH8VCsNttEnxnGQ-1idKpZYJNE9Fg.ttf from https://fonts.gstatic.com/s/leckerlione/v10/V8mCoQH8VCsNttEnxnGQ-1idKpZYJNE9Fg.ttf
  [Leckerli One]: download ~/Downloads/8qrv1tIC_i-mOkfb29wAlg.svg from https://fonts.gstatic.com/l/font?kit=V8mCoQH8VCsNttEnxnGQ-1idKpZa&skey=6384c587add2bb80&v=v10#LeckerliOne
  download 3 files into ~/Downloads


.. todo::

   WIP


.. admonition:: fontlib download
   :class: rst-example

   .. program-output:: ../local/py3/bin/fontlib list


.. toctree::

   font
   cli

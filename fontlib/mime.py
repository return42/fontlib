# -*- coding: utf-8; mode: python -*-
"""
MIME type implementations
"""

__all___ = ['add_types', ]

import mimetypes
import fspath

def add_types():
    """Add ``fontlib/mime.types`` to :py:mod:`mimetypes` """
    mtypes = mimetypes.read_mime_types(fspath.FSPath(__file__).DIRNAME / 'mime.types')
    for ext, mtype in mtypes.items():
        mimetypes.add_type(mtype, ext)

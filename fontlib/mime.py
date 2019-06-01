# -*- coding: utf-8; mode: python; mode: flycheck -*-
"""
MIME type implementations
"""

__all___ = ['add_types', ]

import logging
import mimetypes
import fspath

log = logging.getLogger(__name__)

MIMETYPES_FNAME = fspath.FSPath(__file__).DIRNAME / 'mime.types'

def add_types():
    """Add ``fontlib/mime.types`` to :py:mod:`mimetypes` """
    log.debug("load mime.types from: %s", MIMETYPES_FNAME)
    mtypes = mimetypes.read_mime_types(MIMETYPES_FNAME)
    for ext, mtype in mtypes.items():
        mimetypes.add_type(mtype, ext)

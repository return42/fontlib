# -*- coding: utf-8; mode: python; mode: flycheck -*-
"""
MIME type implementations
"""

__all___ = ['add_types', 'FontlibMimeTypes']

import logging
import mimetypes
import fspath

log = logging.getLogger(__name__)

MIMETYPES_FNAME = fspath.FSPath(__file__).DIRNAME / 'mime.types'

class FontlibMimeTypes(mimetypes.MimeTypes):
    """
    A class (:py:class:`mimetypes.MimeTypes` ) with (only) mime types from ``fontlib/mime.types``
    """
    def __init__(self):  #pylint: disable=super-init-not-called
        self.encodings_map = {}
        self.suffix_map = {}
        self.types_map = ({}, {})
        self.types_map_inv = ({}, {})
        log.debug("FontlibMimeTypes: load mime.types from: %s", MIMETYPES_FNAME)
        with open(MIMETYPES_FNAME) as f:
            self.readfp(f, True)

    def map_types(self):
        """Return tuples with suffix and mime type.

        :return:
            ``[('.ttf', 'font/ttf'), ('.woff2', 'font/woff2'), ...]``
        """
        return self.types_map[True].items()

def add_types():
    """Add mime types from ``fontlib/mime.types`` to :py:mod:`mimetypes`

    .. literalinclude:: ../fontlib/mime.types

    """
    for ext, mtype in FontlibMimeTypes().map_types():
        log.debug("mime: add %s (%s)", mtype, ext)
        mimetypes.add_type(mtype, ext)

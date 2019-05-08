# -*- coding: utf-8; mode: python -*-
# pylint: disable=missing-docstring

from . import __pkginfo__

__version__   = __pkginfo__.version
__author__    = __pkginfo__.authors[0]
__license__   = __pkginfo__.license
__copyright__ = __pkginfo__.copyright
__doc__       = __pkginfo__.docstring

# register mime types

from .mime import add_types
add_types()

# SPDX-License-Identifier: AGPL-3.0-or-later
# pylint: disable=missing-module-docstring
import logging
from . import __pkginfo__
from .mime import add_types

logging.getLogger(__name__).addHandler(logging.NullHandler())

__version__   = __pkginfo__.version
__author__    = __pkginfo__.authors[0]
__license__   = __pkginfo__.license
__copyright__ = __pkginfo__.copyright
__doc__       = __pkginfo__.docstring

# register mime types
add_types()

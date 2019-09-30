# -*- coding: utf-8; mode: python; mode: flycheck -*-
"""
Font library API
"""

__all__ = ['FontStack', 'URLBlob', 'BUILTINS', 'get_event']

from .fontstack import FontStack
from .fontstack import BUILTINS
from .urlcache import URLBlob
from .event import get_event

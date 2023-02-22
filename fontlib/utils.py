# SPDX-License-Identifier: AGPL-3.0-or-later
"""utils

"""
# pylint: disable=too-few-public-methods
__all__ = [
    'lazy_property'
    , ]

class lazy_property:  # pylint: disable=invalid-name
    """A @property that is only evaluated once."""

    def __init__(self, deferred):
        self._deferred = deferred
        self.__doc__ = deferred.__doc__

    def __get__(self, obj, cls):
        if obj is None:
            return self
        value = self._deferred(obj)
        setattr(obj, self._deferred.__name__, value)
        return value

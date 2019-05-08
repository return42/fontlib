# -*- coding: utf-8; mode: python -*-
"""
Implemtation of :py:class:`Font`
"""

__all__ = ["Font", ]

class Font:
    """A font file (url)"""
    # pylint: disable=too-few-public-methods

    def __init__(self, url, font_name):
        self.url = url
        self.name = font_name
        self.aliases = []

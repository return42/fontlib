# -*- coding: utf-8; mode: python; mode: flycheck -*-
"""
Implemtation of :py:class:`Font`
"""

__all__ = ["Font", ]

import logging

log = logging.getLogger(__name__)

class Font:
    """A font resource identified by URL"""
    # pylint: disable=too-few-public-methods

    def __init__(self, url, font_name):
        """Create instace

        :param url:
            URL of the font
        :param font_name:
            Name of the font
        """

        self.url = url
        self.name = font_name
        self.aliases = []

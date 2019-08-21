# -*- coding: utf-8; mode: python; mode: flycheck -*-
"""Module that implements the application :py:class:`Config` class."""

__all__ = ['Config']

import configparser
from fspath import FSPath

class Config(configparser.ConfigParser): # pylint: disable=too-many-ancestors
    """Configuration object of :py:obj:`fontlib`"""

    DEFAULT_INI = FSPath(__file__).DIRNAME / "config.ini"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.read(Config.DEFAULT_INI)

    def getlist(self, section, option, *, raw=False, _vars=None,
                fallback=configparser._UNSET, **kwargs): # pylint: disable=protected-access
        """Get a list from a comma separated config string."""
        return self._get_conv(
            section, option, self._convert_to_list,
            raw=raw, vars=_vars, fallback=fallback, **kwargs)

    def _convert_to_list(self, value): # pylint: disable=no-self-use
        return [i.strip() for i in value.split(',')]

    # direct access to config sections

    @property
    def FONTSTACK(self):
        """Dictionary from config section 'fontstack'"""
        return self['fontstack']

    @property
    def GOOGLE_FONTS(self):
        """Dictionary from config section 'google fonts'"""
        return self['google fonts']

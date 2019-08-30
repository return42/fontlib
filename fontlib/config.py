# -*- coding: utf-8; mode: python; mode: flycheck -*-
"""The implementation of application's configuration is given in class
:py:class:`Config`.

"""

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
        if not value:
            return []
        return [i.strip() for i in value.split(',')]

    def getpath(self, section, option, *, raw=False, _vars=None,
                fallback=configparser._UNSET, **kwargs): # pylint: disable=protected-access
        """Get a :py:class:`fspath.FSPath` object from a config string."""
        return self._get_conv(
            section, option, self._convert_to_fspath,
            raw=raw, vars=_vars, fallback=fallback, **kwargs)

    def _convert_to_fspath(self, value): # pylint: disable=no-self-use
        return FSPath(value).EXPANDUSER.EXPANDVARS

    def config_env(self, app, workspace):
        """Additional variables that can be used in the INI files"""
        return {'app' : app, 'workspace' : workspace}

    # direct access to config sections

    @property
    def FONTSTACK(self):
        """Dictionary from config section ``[fontstack]``"""
        return self['fontstack']

    @property
    def GOOGLE_FONTS(self):
        """Dictionary from config section ``[google fonts]``"""
        return self['google fonts']

    @property
    def LOGGING(self):
        """Dictionary from config section ``[logging]``"""
        return self['logging']

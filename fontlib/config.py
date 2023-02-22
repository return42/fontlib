# SPDX-License-Identifier: AGPL-3.0-or-later
"""Implementation of application's configuration class :py:class:`Config`."""

__all__ = ['Config', 'init_cfg', 'get_cfg', 'DEFAULT_INI', 'GLOBAL_CONFIG']

import logging
import configparser
from fspath import FSPath

log = logging.getLogger(__name__)

DEFAULT_INI = FSPath(__file__).DIRNAME / "config.ini"
"""Default ``config.ini``"""

GLOBAL_CONFIG = None
"""Active :py:class:`Config` object of the application

The surrounding process (or thread) sets the *active* ``GLOBAL_CONFIG``, for
details see :py:func:`init_cfg` and :py:func:`get_cfg`.

.. note::

   The GLOBAL_CONFIG has no special treatment for threading, its just a simple
   name auf a python modul.  Never import ``GLOBAL_CONFIG`` in your module,
   always use :py:func:`get_cfg` to get active ``GLOBAL_CONFIG``!

"""

def init_cfg(filenames=None, encoding='utf-8'):
    """Init :py:obj:`GLOBAL_CONFIG`.

    Read and parse a filename or an iterable of filenames.  Files that cannot be
    opened are silently ignored `[ref] <configparser.ConfigParser.read>`__.

    Return list of successfully read files.

    :param filenames: Filename or an iterable of filenames (default:
        :py:obj:`DEFAULT_INI`).

    :param encoding: The encoding parameter(default: ``utf-8``).

    .. note::

       Re-initing means; replace the old value of GLOBAL_CONFIG with a new
       instance of class :py:class:`Config`.

       To *extend* the :py:data:`GLOBAL_CONFIG` use
       :py:meth:`configparser.ConfigParser.read`::

           get_cfg().read(filenames)

    """
    global GLOBAL_CONFIG # pylint: disable=global-statement
    GLOBAL_CONFIG = Config()
    log.debug('init_cfg: defaults from %s', DEFAULT_INI)
    ret_val = GLOBAL_CONFIG.read(DEFAULT_INI, encoding='utf-8')
    if filenames:
        log.debug('init_cfg: read from %s', filenames)
        ret_val = GLOBAL_CONFIG.read(filenames, encoding)
    return ret_val

def get_cfg():
    """Returns *active* :py:obj:`GLOBAL_CONFIG`

    """
    return GLOBAL_CONFIG


class Config(configparser.ConfigParser):
    """Configuration object of :py:obj:`fontlib`"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def getfqnobj(self, section, option, *, raw=False, _vars=None,
                  fallback=configparser._UNSET, **kwargs): # pylint: disable=protected-access
        """Get python object refered by full qualiffied name (FQN) in the config string.
        """
        return self._get_conv(
            section, option, self._convert_fqn_to_pyobj,
            raw=raw, vars=_vars, fallback=fallback, **kwargs)

    def _convert_fqn_to_pyobj(self, value):
        (modulename, name) = value.rsplit('.', 1)
        m = __import__(modulename, {}, {}, [name], 0)
        return getattr(m, name)

    def getlist(self, section, option, *, raw=False, _vars=None,
                fallback=configparser._UNSET, **kwargs): # pylint: disable=protected-access
        """Get a list from a comma separated config string."""
        return self._get_conv(
            section, option, self._convert_to_list,
            raw=raw, vars=_vars, fallback=fallback, **kwargs)

    def _convert_to_list(self, value):
        if not value:
            return []
        return [i.strip() for i in value.split(',')]

    def getpath(self, section, option, *, raw=False, _vars=None,
                fallback=configparser._UNSET, **kwargs): # pylint: disable=protected-access
        """Get a :py:class:`fspath.fspath.FSPath` object from a config string."""
        return self._get_conv(
            section, option, self._convert_to_fspath,
            raw=raw, vars=_vars, fallback=fallback, **kwargs)

    def _convert_to_fspath(self, value):
        return FSPath(value).EXPANDUSER.EXPANDVARS

    def config_env(self, app, workspace):
        """Additional variables that can be used in the INI files"""
        return {'app' : app, 'workspace' : workspace}

    # pylint: disable=invalid-name

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

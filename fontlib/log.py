# -*- coding: utf-8; mode: python; mode: flycheck -*-
"""
common logging & setup implementations
"""

__all__ = ['DEFAULT_LOG_INI', 'FONTLIB_LOGGER', 'init_log']

import configparser
import logging
from fspath import FSPath

log = logging.getLogger(__name__)

DEFAULT_LOG_INI = FSPath(__file__).DIRNAME / "log.ini"

FONTLIB_LOGGER = 'fontlib'
"""Name of :py:obj:`fontlib` 's (topmost) logger"""

def init_log(log_config_ini, defaults=None):
    log.debug('init log from: %s env: %s', log_config_ini, defaults)
    log_cfg = configparser.ConfigParser(defaults=defaults)
    log_cfg.read(log_config_ini)
    logging.config.fileConfig(log_cfg)

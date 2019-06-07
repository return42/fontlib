# -*- coding: utf-8; mode: python; mode: flycheck -*-
"""
common logging & setup implementations
"""

import logging

from fspath import OS_ENV

log = logging.getLogger(__name__)

DEFAULT_LOGGER = 'fontlib'
CONSOLE_LEVEL = 'ERROR'

DEBUG_LOG = OS_ENV.get("DEBUG", None)

if DEBUG_LOG is not None:
    CONSOLE_LEVEL = 'DEBUG'
    if DEBUG_LOG and DEBUG_LOG.startswith(DEFAULT_LOGGER):
        DEFAULT_LOGGER = DEBUG_LOG


cfg = {
    'version': 1,
    'formatters': {
        'console': {
            'format': '%(levelname)-8s|%(name)-12s| %(message)s',
        },
        'logfile': {
            'format': '%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
        }
    },
    'handlers': {
        'console': {
            'class':        'logging.StreamHandler',
            'formatter':    'console',
            'level':        CONSOLE_LEVEL,
        },
        'logfile': {
            'class':        'logging.handlers.RotatingFileHandler',
            'formatter':    'console',
            'level':        'DEBUG',
            'filename':     './fontlib.log',
            'maxBytes':     1024 * 1024,
            'backupCount':  3,
        },
    },
    'loggers':  {
        DEFAULT_LOGGER: {
            'handlers':     ['console', 'logfile'],
            'level':        'DEBUG'
        },
    },
}

# -*- coding: utf-8; mode: python; mode: flycheck -*-
"""
common logging & setup implementations
"""

import logging

from fspath import OS_ENV

log = logging.getLogger('fontlib')

CONSOLE_LEVEL = 'ERROR'
if OS_ENV.get("DEBUG", None) is not None:
    CONSOLE_LEVEL =  'DEBUG'

cfg = {
    'version': 1,
    'formatters': {
        'console': {
            'format': '%(levelname)s: %(message)s',
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
        'fontlib': {
            'handlers':     ['console', 'logfile'],
            'level':        'DEBUG'
        },
    },
}

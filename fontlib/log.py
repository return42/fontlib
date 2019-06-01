# -*- coding: utf-8; mode: python; mode: flycheck -*-
"""
common logging & setup implementations
"""

import logging

log = logging.getLogger('fontlib')

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
            'level':        'INFO',
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

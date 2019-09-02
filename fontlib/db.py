# -*- coding: utf-8; mode: python; mode: flycheck -*-
"""Implementation of application's database """

# __all__ = [, ]

import logging

from sqlalchemy import Column, String
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

log = logging.getLogger(__name__)
Base = declarative_base()

# https://docs.sqlalchemy.org/en/13/orm/tutorial.html#create-a-schema

def open_db(config):
    """Open & Returns a DB instance ..."""

    connector = config.getfqnobj('fontstack', 'database', fallback='sqlite:///:memory:')
    engine = create_engine(connector)
    return engine

class DB_Font(Base):
    __tablename__ = 'fonts'

    origin = Column(String(1024), primary_key=True)
    """The URL from `CSS @font-face:src`_ of the font resource."""

    ID = Column(String(22), index=True, unique=True)
    """A url-safe hash of font's resource URL, used as unique resource ID"""

    font_name = Column(String(80), index=True, unique=False)
    """The font-name (value of `CSS @font-face:font-family`_)"""

    # FIXME ..
    aliases = Column(String(80*12))
    """A list of alias font-names (values of `CSS @font-face:font-family`_)"""

    # FIXME ..
    format = Column(String(22*6))
    """Comma-separated list of format strings (`CSS @font-face:src`_)"""

    unicode_range = Column(String(4098))
    """A string with the value of `CSS @font-face:unicode-range`_"""

    def __repr__(self):
        return "<DB:: font_name='%s', format='%s', ID='%s', origin='%s'>" % (
            self.font_name, self.format, self.ID, self.origin
        )

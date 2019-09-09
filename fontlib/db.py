# -*- coding: utf-8; mode: python; mode: flycheck -*-
"""Implementation of application's database """

# __all__ = [, ]

import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

log = logging.getLogger(__name__)

# pylint: disable=invalid-name
FontLibSchema = declarative_base()
FontLibEngine = None
FontLibSession = None
# pylint: enable=invalid-name

def init_fontlib_db(config):
    """Init DB engine configured in config.ini [DEFAULT]:fontlib_db"""
    global FontLibSession # pylint: disable=global-statement, invalid-name

    # https://docs.sqlalchemy.org/engines.html#database-urls
    connector = config.get('DEFAULT', 'fontlib_db', fallback='sqlite:///:memory:')

    log.info("create engine connected to DB: %s", connector)
    # https://docs.sqlalchemy.org/orm/tutorial.html#connecting
    # https://docs.sqlalchemy.org/core/engines.html
    engine = create_engine(connector)

    log.info("create sessionmaker binded to engine: %s", engine)
    # https://docs.sqlalchemy.org/en/13/orm/session_transaction.html
    FontLibSession = sessionmaker(bind=engine, autocommit=True)

    log.info("init schema (create_all) of %s", FontLibSchema)
    # https://docs.sqlalchemy.org/en/13/core/metadata.html#creating-and-dropping-database-tables
    FontLibSchema.metadata.create_all(engine)
    log.info("init fontlib_db: OK")

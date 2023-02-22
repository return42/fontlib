# SPDX-License-Identifier: AGPL-3.0-or-later
"""Implementation of application's database.

Fontlib's SQL Toolkit and Object Relational Mapper is based on the
SQLAlchemy_ (SQLAlchemy-ORM_)

"""

__all__ = [
    'FontLibSchema'
    , 'fontlib_init'
    , 'fontlib_scope'
    , 'fontlib_session'
    , 'FONTLIB_ENGINE'
    , 'TableUtilsMixIn'
    , 'FONTLIB_SESSION'
    , 'FONTLIB_ACTIVE_SESSION'
    , 'FONTLIB_SESSIONMAKER'
]

import logging
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from sqlalchemy.ext.declarative import declarative_base

log = logging.getLogger(__name__)

FontLibSchema = declarative_base()
FONTLIB_SESSION = None
"""Session class

The global session class is inited by :py:func:`fontlib_init`

"""

FONTLIB_ENGINE = None
"""Engine of DB ``fontlib``.

"""

FONTLIB_SESSIONMAKER = None
"""Sessionmaker of DB ``fontlib``

The global session maker is inited by :py:func:`fontlib_init`

"""

FONTLIB_ACTIVE_SESSION = None
"""active session of DB ``fontlib``

The surrounding process (or thread) sets the active session, for details see
:py:func:`fontlib_scope` and :py:func:`fontlib_session`

"""

def fontlib_init(config):
    """Init DB engine configured in config.ini ``[DEFAULT]:fontlib_db``

    1. Create a DB connector to database ``[DEFAULT]:fontlib_db``

    2. Create a engine with this connector in :py:obj:`FONTLIB_ENGINE`

    3. Create a session maker in :py:obj:`FONTLIB_SESSIONMAKER`

    4. Create DB schema by calling :py:class:`sqlalchemy.schema.MetaData.create_all`

    5. Create a session class in :py:obj:`FONTLIB_SESSION`.

    .. hint::

       The :py:obj:`FONTLIB_SESSION` is a scoped_session_, about session
       management (transactions) in application's code see :py:func:`fontlib_scope`.

    """
    global FONTLIB_ENGINE, FONTLIB_SESSIONMAKER, FONTLIB_SESSION  # pylint: disable=global-statement

    log.debug("init_fontlib: START ...")
    # https://docs.sqlalchemy.org/engines.html#database-urls
    fontlib_connector = config.get('DEFAULT', 'fontlib_db', fallback='sqlite:///:memory:')

    log.debug("init_fontlib: create engine connected to DB: %s", fontlib_connector)
    # https://docs.sqlalchemy.org/orm/tutorial.html#connecting
    # https://docs.sqlalchemy.org/core/engines.html
    FONTLIB_ENGINE = create_engine(fontlib_connector)

    log.debug("fontlib_db: init schema (create_all) of %s",  FontLibSchema)
    # https://docs.sqlalchemy.org/en/13/core/metadata.html#creating-and-dropping-database-tables
    FontLibSchema.metadata.create_all(FONTLIB_ENGINE)

    # https://docs.sqlalchemy.org/en/13/orm/contextual.html#unitofwork-contextual
    log.debug("fontlib_db: create sessionmaker binded to engine: %s", FONTLIB_ENGINE)
    FONTLIB_SESSIONMAKER = sessionmaker(bind=FONTLIB_ENGINE, autocommit=False)

    # https://docs.sqlalchemy.org/en/13/orm/session_transaction.html
    log.debug("init_fontlib: init contextual (scoped) sessions")
    FONTLIB_SESSION = scoped_session(FONTLIB_SESSIONMAKER)

    log.debug("init_fontlib: OK")

@contextmanager
def fontlib_scope():
    """Provide a (new) transactional scope for on 'fontlib' DB.

    Creates a instance of :py:obj:`FONTLIB_SESSION`, stores it under the global
    name :py:obj:`FONTLIB_ACTIVE_SESSION` and yield it.

    .. hint::

       For the *client site* use :py:func:`fontlib_session` to get current
       active session.

    A typical usage is to start (and end) the transaction in your *top function
    / main loop* while all other modules get the active session by calling
    :py:func:`fontlib_session`.

    By example; suppose you have a *main* script where you start the transaction
    scope named ``session`` and a module which likes to add a new ``Font`` into
    the database (into the acrive session).::

        # ----  file: main.py ----

        from fontlib import db
        from fontlib.config import Config
        import foo

        cfg = Config()
        db.init_fontlib(cfg)
        ...
        with db.fontlib_scope() as session:
            ...
            foo.add_myfont()
            ...
            all_fonts = session.query(Font)
            ...

    Modules like the *foo* below are using the :py:func:`fontlib_scope` to get
    the session which was set by the surrounding application code (*main*).  The
    *foo* module itself does not need to now about transaction start and
    transaction end, this is managed by the outer scope in *main*, while both
    are using sthe same session instance::

        # ----  module: foo.py ----

        from fontlib.db import fontlib_session
        from fontlib.font import Font

        def add_myfont():
            my_font = Font("file:///fontlib/files/dejavu/dejavu.css")
            fontlib_session().add(font)

    """
    global FONTLIB_ACTIVE_SESSION # pylint: disable=global-statement

    # https://docs.sqlalchemy.org/en/13/orm/contextual.html#unitofwork-contextual
    log.debug("fontlib_scope: START transactional scope")
    FONTLIB_ACTIVE_SESSION = FONTLIB_SESSION()
    try:
        yield FONTLIB_ACTIVE_SESSION
        log.debug("fontlib_scope: COMMIT transactional scope")
        FONTLIB_ACTIVE_SESSION.commit()

    except:
        log.debug("fontlib_scope: ROLLBACK transactional scope")
        FONTLIB_ACTIVE_SESSION.rollback()
        raise

    finally:
        log.debug("fontlib_scope: CLOSE transactional scope")
        FONTLIB_ACTIVE_SESSION.close()

    log.debug("fontlib_scope: END transactional scope")

def fontlib_session():
    """Returns current active fontlib session (see :py:func:`fontlib_scope`)

    """
    return FONTLIB_ACTIVE_SESSION


class TableUtilsMixIn:
    """MixIn class for SQLAlchemy ORM classes.

    usage::

        class MyClass(MySchema, TableUtilsMixIn):
            __tablename__ = 'my_class'

    """

    def pkey_exists(self, session):
        """Check if object with same primary keys exists in the database.

        .. note::

           ``inspect(myobject).identity`` will not work:

           An object which is transient or pending does not have a mapped
           identity until it is flushed, even if its attributes include primary
           key values, [`ref
           <https://docs.sqlalchemy.org/en/13/orm/internals.html#sqlalchemy.orm.state.InstanceState.identity>`__].

           Thats why :py:meth:`pkey_exists` is based on a real DB query.

        """
        return bool(self.get_persistent_object(session))

    def get_persistent_object(self, session):
        """Return persistent object from DB or None if ot exists in DB

        Does a *session query* of the self object by it's primary keys in the DB
        and returns object if one exists. If primary key does not exists in the
        database None is returned.

        """
        # https://docs.sqlalchemy.org/en/13/orm/mapping_api.html#sqlalchemy.orm.util.identity_key
        cls, pkey = session.identity_key(instance=self)[:2]
        return session.query(cls).get(pkey)

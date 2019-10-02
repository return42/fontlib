# -*- coding: utf-8; mode: python; mode: flycheck -*-
"""Implementation of application's database.

Fontlib's SQL Toolkit and Object Relational Mapper is based on the
SQLAlchemy_ (SQLAlchemy-ORM_)

"""

__all__ = [
    'FontLibSchema'
    , 'fontlib_init'
    , 'fontlib_scope'
    , 'fontlib_session'
    , 'fontlib_engine'
    , 'TableUtilsMixIn'
    , 'FontLibSession'
    , 'fontlib_active_session'
    , 'fontlib_sessionmaker'
]

import logging
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from sqlalchemy.ext.declarative import declarative_base

log = logging.getLogger(__name__)

FontLibSchema = declarative_base()
FontLibSession = None
"""Session class

The global session class is inited by :py:func:`fontlib_init`

"""

fontlib_engine = None
"""Engine of DB ``fontlib``.

"""

fontlib_sessionmaker = None
"""Sessionmaker of DB ``fontlib``

The global session maker is inited by :py:func:`fontlib_init`

"""

fontlib_active_session = None
"""active session of DB ``fontlib``

The surrounding process (or thread) sets the active session, for details see
:py:func:`fontlib_scope` and :py:func:`fontlib_session`

"""

def fontlib_init(config):
    """Init DB engine configured in config.ini ``[DEFAULT]:fontlib_db``

    1. Create a DB connector to database ``[DEFAULT]:fontlib_db``

    2. Create a engine with this connector in :py:obj:`fontlib_engine`

    3. Create a session maker in :py:obj:`fontlib_sessionmaker`

    4. Create DB schema by calling :py:class:`sqlalchemy.schema.MetaData.create_all`

    5. Create a session class in :py:obj:`FontLibSession`.

    .. hint::

       The :py:obj:`FontLibSession` is a scoped_session_, about session
       management (transactions) in application's code see :py:func:`fontlib_scope`.

    """
    global fontlib_engine, fontlib_sessionmaker, FontLibSession  # pylint: disable=global-statement

    log.debug("init_fontlib: START ...")
    # https://docs.sqlalchemy.org/engines.html#database-urls
    fontlib_connector = config.get('DEFAULT', 'fontlib_db', fallback='sqlite:///:memory:')

    log.debug("init_fontlib: create engine connected to DB: %s", fontlib_connector)
    # https://docs.sqlalchemy.org/orm/tutorial.html#connecting
    # https://docs.sqlalchemy.org/core/engines.html
    fontlib_engine = create_engine(fontlib_connector)

    log.debug("fontlib_db: init schema (create_all) of %s",  FontLibSchema)
    # https://docs.sqlalchemy.org/en/13/core/metadata.html#creating-and-dropping-database-tables
    FontLibSchema.metadata.create_all(fontlib_engine)

    # https://docs.sqlalchemy.org/en/13/orm/contextual.html#unitofwork-contextual
    log.debug("fontlib_db: create sessionmaker binded to engine: %s", fontlib_engine)
    fontlib_sessionmaker = sessionmaker(bind=fontlib_engine, autocommit=False)

    # https://docs.sqlalchemy.org/en/13/orm/session_transaction.html
    log.debug("init_fontlib: init contextual (scoped) sessions")
    FontLibSession = scoped_session(fontlib_sessionmaker)

    log.debug("init_fontlib: OK")

@contextmanager
def fontlib_scope():
    """Provide a (new) transactional scope for on 'fontlib' DB.

    Creates a instance of :py:obj:`FontLibSession`, stores it under the global
    name :py:obj:`fontlib_active_session` and yield it.

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
    global fontlib_active_session # pylint: disable=global-statement

    # https://docs.sqlalchemy.org/en/13/orm/contextual.html#unitofwork-contextual
    log.debug("fontlib_scope: START transactional scope")
    fontlib_active_session = FontLibSession()
    try:
        yield fontlib_active_session
        log.debug("fontlib_scope: COMMIT transactional scope")
        fontlib_active_session.commit()

    except:
        log.debug("fontlib_scope: ROLLBACK transactional scope")
        fontlib_active_session.rollback()
        raise

    finally:
        log.debug("fontlib_scope: CLOSE transactional scope")
        fontlib_active_session.close()

    log.debug("fontlib_scope: END transactional scope")

def fontlib_session():
    """Returns current active fontlib session (see :py:func:`fontlib_scope`)

    """
    global fontlib_active_session # pylint: disable=global-statement
    return fontlib_active_session


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

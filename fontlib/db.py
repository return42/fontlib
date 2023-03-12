# SPDX-License-Identifier: AGPL-3.0-or-later
"""Implementation of application's database.

Fontlib's SQL Toolkit and Object Relational Mapper is based on the `SQLAlchemy 2`_.

.. _SQLAlchemy 2:
   https://docs.sqlalchemy.org/en/20/intro.html

"""
# pylint: disable=too-few-public-methods

__all__ = [ 'FontlibBase' , 'FontlibDB' ]

import logging

from sqlalchemy import create_engine
from sqlalchemy import orm
from sqlalchemy import engine

log = logging.getLogger(__name__)

class FontlibBase(orm.DeclarativeBase):
    """Declarative base class of fontlib's DB schema"""

    def identity(self, session: orm.Session):
        """Return the mapped identity of the mapped object.  This is the primary
        key identity as persisted by the ORM.

        Does a *session query* of the self object by it's primary keys in the DB
        and returns object if one exists.  If primary key does not exists in the
        database :py:obj:`None` is returned.

        .. note::

           This method does not use `InstanceState.identity`_: An object which
           is transient or pending does not have a mapped identity until it is
           flushed, even if its attributes include primary key values.

        .. _InstanceState.identity:
           https://docs.sqlalchemy.org/en/20/orm/internals.html#sqlalchemy.orm.InstanceState.identity

        """
        cls, pkey = session.identity_key(instance=self)[:2]
        ret_val = session.get(cls, pkey)
        return ret_val

    def has_identity(self, session: orm.Session):
        """Return :py:obj:`True` if mapped identity of the ORM object exist,
        otherwise :py:obj:False`.

        .. note::

           This method does not use `InstanceState.has_identity`_ / see
           :py:meth:`identity`.

        """
        return bool(self.get_persistent_object(session))


class FontlibDB:
    """Session and DB engine of the fontlib application."""

    session: orm.Session
    """Contextual (scoped) session / see `Session API`_ and `Transactions and
    Connection Management`_

    .. code: python

       db = FontlibDB(cfg)
       with db.session.begin() as session:
          session.add(some_object)
          session.add(some_other_object)
       # commits transaction, closes session

    .. _Session API:
       https://docs.sqlalchemy.org/en/20/orm/session_api.html
    .. _Transactions and Connection Management:
       https://docs.sqlalchemy.org/en/20/orm/session_transaction.html
    """

    engine: engine.Engine
    """DB engine_

    .. _engine:
       https://docs.sqlalchemy.org/en/20/core/engines.html
    """

    def __init__(self, cfg):
        db_url = cfg.get('fontlib.db_url', 'sqlite://')
        self.engine = create_engine(db_url)
        self.session = orm.scoped_session(orm.sessionmaker(self.engine))
        # from sqlalchemy import inspect
        # self.inspect = inspect(self.engine)
        self.create()

    def create(self):
        """Create DB tables / see `Creating and Dropping Database Tables`_.

        .. _Creating and Dropping Database Tables:
           https://docs.sqlalchemy.org/en/20/core/metadata.html#creating-and-dropping-database-tables

        """
        log.debug("init schema (create_all) of %s",  FontlibBase)
        FontlibBase.metadata.create_all(self.engine)

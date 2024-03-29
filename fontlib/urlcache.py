# SPDX-License-Identifier: AGPL-3.0-or-later
"""Font library

"""

__all__ = [
    'URLBlob'
    , 'download_blob'
    , 'URLCache'
    , 'NoCache'
    , 'SimpleURLCache'
]

import logging
import base64
import hashlib
from urllib.parse import urlparse
from urllib.request import urlopen
from sqlalchemy import Column, String
from sqlalchemy.schema import ForeignKey
from sqlalchemy.orm import relationship

import fspath

from . import event

from .db import FontLibSchema
from .db import TableUtilsMixIn
from .db import fontlib_session

log = logging.getLogger(__name__)

class URLBlob(FontLibSchema, TableUtilsMixIn):  # pylint: disable=too-few-public-methods
    """A simple BLOB object"""

    __tablename__ = 'urlcache_blob'

    STATE_REMOTE = 'remote'
    STATE_LOCAL  = 'local'
    STATE_CACHED = 'cached'
    STATE_LIST   = [STATE_REMOTE, STATE_LOCAL, STATE_CACHED]

    origin = Column(String(1024), primary_key=True)
    """The origin URL"""

    id = Column(String(22), ForeignKey('font.id'), nullable=False, unique=True)
    """A url-safe hash of :py:class:`URLBlob` resource, used as unique resource ID"""

    state = Column(String(80))
    """State of the BLOB in the cache: ``[w]``

    - ``remote`` : BLOB needs replication
    - ``local``  : BLOB is not cached but available from common filesystem
    - ``cached`` : a copy of the BLOB is localy available

    """

    font = relationship("Font", back_populates="blob", uselist=False)

    def __init__(self, origin, **kwargs):

        kwargs['origin'] = origin

        if 'state' not in kwargs:
            kwargs['state'] = URLBlob.STATE_REMOTE
        if kwargs['state'] not in URLBlob.STATE_LIST:
            raise ValueError(f"URLBlob unknown state: {kwargs['state']}")

        if 'id' not in kwargs:
            _ = origin.encode('utf-8')
            _ = hashlib.md5(_).digest()
            _ = base64.urlsafe_b64encode(_)[:-2]
            kwargs['id'] = _.decode('utf-8')

        super().__init__(**kwargs)

    def __repr__(self):
        # pylint: disable=consider-using-f-string
        return "<URLBlob (%(id)s), origin='%(origin)s'>" % self.__dict__


def download_blob(blob, cache_file, chunksize=1048576):
    """Download blob.origin into cache_file.

    :param fspath.fspath.FSPath cache_file: local filename
    :param .urlcache.URLBlob blob: URL from blob.origin
    :param int chunkize: The default chunksize is 1048576 bytes.

    :py:func:`.event.emit`:

    - ``urlcache.download.tick`` (:py:obj:`url <str>`, :py:obj:`font name
      <str>`, :py:obj:`font format <str>`, :py:obj:`local file name
      <fspath.fspath.FSPath>`, :py:obj:`down_bytes <int>`, :py:obj:`max_bytes
      from 'headers:Content-Length' or 0 <int>`) is released, each time a chunk
      has been downloaded.  If no more to download, max_bytes is set to -1.

    """

    with urlopen(blob.origin) as d:
        with open(cache_file, "wb") as f:
            max_bytes  = int(d.headers.get("Content-Length", 0))
            down_bytes = 0
            if chunksize is None:
                chunksize = max_bytes // 100
            while 1:
                x = d.read(chunksize)
                if not bool(len(x)):
                    event.emit(
                        'urlcache.download.tick'
                        , blob.origin, blob.font.name, blob.font.format
                        , cache_file, down_bytes, -1)
                    break
                f.write(x)
                down_bytes += len(x)
                event.emit(
                    'urlcache.download.tick'
                    , blob.origin, blob.font.name, blob.font.format
                    , cache_file, down_bytes, max_bytes)


class URLCache:
    """Abstract key/value hash for cached BLOBs (response) from origin.

    The *key* is origin's URL and the value is the BLOB (response) from this
    URL.

    """

    CHUNKSIZE = 1048576

    def __init__(self):
        self.init_ok = False

    def get_blob_obj(self, origin):
        """Return :py:class:`URLBlob` for <origin> URL or ``None`` if URL is unknown.

        :param str origin: the URL of the origin

        """

        session = fontlib_session()
        blob = session.query(URLBlob).get(origin)

        if blob is None:
            log.debug("get_blob_obj: no entry for: %s", origin)
        else:
            log.debug("get_blob_obj: found entry for: %s", origin)

        return blob

    def add_url(self, origin):
        """Add URL <origin> to cache's database.

        :param str origin: the URL of the origin

        :returns:  BLOB object
        :rtype:    .urlcache.URLBlob
        """

        blob = self.get_blob_obj(origin)

        if blob is None:
            log.debug("URLCache: sql insert table urlcache_blob: %s", blob)
            blob = URLBlob(origin)
            self.update_db(blob)

        return blob

    def update_db(self, blob):
        """Update status of :py:class:`URLBlob` in the database.

        :param blob: instance of class :py:class:`.urlcache.URLBlob`
        """

        cache_file = self.fname_by_blob(blob)

        state = URLBlob.STATE_REMOTE
        if cache_file and cache_file.EXISTS:
            state = URLBlob.STATE_CACHED
        else:
            url = urlparse(blob.origin)
            if url.scheme == 'file':
                state = URLBlob.STATE_LOCAL

        blob.state = state
        fontlib_session().merge(blob)

    def cache_url(self, origin):
        """Assure a localy cached copy of the URL response.

        :param str origin: the URL of the origin

        :returns:  BLOB object from persistent
        :rtype:    .urlcache.URLBlob

        :py:func:`.event.emit`: see :py:func:`download_blob`

        """
        blob = self.get_blob_obj(origin)
        if blob is None:
            # add new BLOB to the persistence
            blob = self.add_url(origin)
        else:
            # force update of the persistence
            self.update_db(blob)

        cache_file = self.fname_by_blob(blob)

        if blob.state == URLBlob.STATE_CACHED:
            # sort out dead candidates / for whatever reason the BLOB might gone
            self.update_db(blob)

        if blob.state == URLBlob.STATE_CACHED:
            log.debug(
                "BLOB [%s] already cached from: %s" , blob.id, blob.origin)

        elif blob.state == URLBlob.STATE_LOCAL:
            log.debug(
                "BLOB [%s] caching from local filesystem: %s", blob.id, blob.origin)

            url = urlparse(blob.origin)
            fspath.FSPath(url.path).copyfile(cache_file)
            self.update_db(blob)

        elif blob.state == URLBlob.STATE_REMOTE:
            log.debug(
                "BLOB [%s] caching from remote: %s", blob.id, blob.origin)
            download_blob(blob, cache_file, chunksize=self.CHUNKSIZE)
            self.update_db(blob)

        return blob

    def save_url(self, origin, dest_file):
        """Save (possibly cached) BLOB from <origin> into file <dest_file>

        :param str origin: URL of the origin

        :param dest_file: Filename of the destination

        If <origin> is not already cached, it is downloaded and cached now.

        """

        blob = self.cache_url(origin)
        cache_file = self.fname_by_blob(blob)
        cache_file.copyfile(dest_file)

    def init(self, config):
        """Init cache from :py:class:`fontlib.config.Config` object"""
        raise NotImplementedError

    def fname_by_blob(self, blob):
        """Return file name of cached BLOB data or ``None`` if blob not already cached.

        :param .urlcache.URLBlob blob: BLOB instance

        :returns: absolute filename of the cached BLOB

        :rtype: fspath.fspath.FSPath

        """
        raise NotImplementedError


class NoCache(URLCache):
    """A dummy cache which never caches"""

    def get_blob_obj(self, origin):
        return URLBlob(origin)

    def add_url(self, origin):
        pass

    def update_db(self, blob):
        pass

    def cache_url(self, origin):
        pass

    def fname_by_blob(self, blob):
        return None

    def init(self, config):
        self.init_ok = True

    def save_url(self, origin, dest_file):
        """Download (un-cached) BLOB from <origin> into file <dest_file>

        :param str origin: URL of the origin
        :param fspath.fspath.FSPath dest_file: Filename of the destination
        """

        state = URLBlob.STATE_REMOTE
        url = urlparse(origin)
        if url.scheme == 'file':
            state = URLBlob.STATE_LOCAL

        if state == URLBlob.STATE_LOCAL:
            log.debug("BLOB copied from local filesystem: %s", origin)
            fspath.FSPath(url.path).copyfile(dest_file)

        elif state == URLBlob.STATE_REMOTE:
            log.debug("BLOB copied from remote: %s", origin)
            blob = self.get_blob_obj(origin)
            download_blob(blob, dest_file, chunksize=self.CHUNKSIZE)


class SimpleURLCache(URLCache):
    """Simple URL cache

    The BLOBs are stored in folder ``[DEFAULT]<workspace>/urlcache`` in your
    <workspace>.  The value for <workspace> is taken from the configuration::

        [DEFAULT]
        workspace = ~/.fontlib

    """

    def __init__(self):
        super().__init__()
        self.root = None

    def init(self, config):
        if self.init_ok:
            return
        self.root = config.getpath('DEFAULT', 'workspace') / 'urlcache'
        log.info("init SimpleURLCache at: %s", self.root)
        self.root.makedirs()

        self.init_ok = True

    def fname_by_blob(self, blob):
        if self.root is None:
            raise ValueError("cache not yet inited!")
        return self.root / blob.id

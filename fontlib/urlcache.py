# -*- coding: utf-8; mode: python; mode: flycheck -*-
"""
Font library
"""

import logging
import base64
import hashlib
from urllib.parse import urlparse

import fspath

log = logging.getLogger(__name__)

class URLBlob:  # pylint: disable=too-few-public-methods
    """A simple BLOB object"""
    def __init__(self, origin, state='remote'):
        self.origin = origin
        _ = self.origin.encode('utf-8')
        _ = hashlib.md5(_).digest()
        _ = base64.urlsafe_b64encode(_)[:-2]
        self.ID = _.decode('utf-8')
        """A url-safe hash of :py:class:`URLBlob` resource, used as unique resource ID"""
        self.state = state
        """State of the BLOB in the cache: ``[remote|local|cached]``

        ``remote``: BLOB needs replication
        ``local``: BLOB is not cached but available from common filesystem
        ``cached``: a copy of the BLOB is localy available
        """

class URLCache:
    """Abstract key/value hash for cached BLOBs (response) from origin.

    The *key* is origin's URL and the value is the BLOB (response) from this
    URL.

    """

    def __init__(self):
        self.init_ok = False
        self.blobs = dict()

    def download_url(self, origin, dest_file):
        """Download (cached) BLOB from <origin> into file <dest_file>"""
        self.cache_url(origin)
        blob = self.blobs[origin]
        cache_file = self.cache_blob_fname(blob)
        cache_file.copyfile(dest_file)

    def cache_url(self, origin):
        """Assure a local copy of the URL.

        :param url: the URL of the origin

        """
        self.init()
        blob = self.add_url(origin)
        cache_file = self.cache_blob_fname(blob)

        if blob.state == 'cached':
            log.debug("BLOB [%s] already cached from: %s" , blob.ID, blob.origin)

        elif blob.state == 'local':
            if not cache_file.EXISTS:
                log.debug("BLOB [%s] is cached (copied) from: %s" , blob.ID, blob.origin)
                url = urlparse(blob.origin)
                fspath.FSPath(url.path).copyfile(cache_file)
                blob.state = 'cached'

        elif blob.state == 'remote':
            if not cache_file.EXISTS:
                log.debug("BLOB [%s] is cached (downloaded) from: %s" , blob.ID, blob.origin)
                cache_file.download(blob.origin)
                blob.state = 'cached'

    def url_state(self, origin):
        """Returns BLOB state of <origin> or ``None`` if URL is unknown.

        :param origin: the URL of the origin

        """
        state = None
        blob = self.blobs.get(origin, None)
        if blob is not None:
            state = blob.state
        return state

    def init(self):
        """Init cache"""
        raise NotImplementedError


    def add_url(self, origin):
        """Add URL <origin> to cached blobs.

        :param origin: the URL of the origin

        """
        raise NotImplementedError

    def cache_blob_fname(self, blob):
        """Return local file name of cached blob.

        :param blob: a :py:class:`URLBlob` instance

        """
        raise NotImplementedError

class NoCache(URLCache):
    """A dummy cache which never caches"""

    def init(self):
        pass

    def add_url(self, origin):
        blob = self.blobs.get(origin, None)
        if blob is None:
            state = 'remote'
            url = urlparse(origin)
            if url.scheme == 'file':
                state = 'local'
            blob = URLBlob(origin, state)
            self.blobs[origin] = blob
        return blob

    def cache_url(self, origin):
        self.add_url(origin)

    def cache_blob_fname(self, blob):
        return None

    def download_url(self, origin, dest_file):
        """Download (un-cached) BLOB from <origin> into file <dest_file>"""
        self.cache_url(origin)
        blob = self.blobs[origin]

        if blob.state == 'local':
            log.debug("BLOB [%s] is copied from: %s" , blob.ID, blob.origin)
            url = urlparse(blob.origin)
            fspath.FSPath(url.path).copyfile(dest_file)

        elif blob.state == 'remote':
            log.debug("BLOB [%s] is downloaded from: %s" , blob.ID, blob.origin)
            dest_file.download(blob.origin)

class SimpleURLCache(URLCache):
    """Simple URL cache"""

    def __init__(self):
        super().__init__()
        self.root = fspath.FSPath("~").EXPANDUSER / '.fontlib' / 'urlcache'

    def init(self):
        if self.init_ok:
            return
        # init ...
        self.root.makedirs()
        self.init_ok = True

    def cache_blob_fname(self, blob):
        return self.root / blob.ID

    def add_url(self, origin):
        blob = self.blobs.get(origin, None)
        if blob is None:
            state = 'remote'
            url = urlparse(origin)
            if url.scheme == 'file':
                state = 'local'
            blob = URLBlob(origin, state)
            self.blobs[origin] = blob

        # does the BLOB already exists in the cache?
        cache_file = self.cache_blob_fname(blob)
        if cache_file.EXISTS:
            blob.state = 'cached'

        return blob

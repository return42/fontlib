# -*- coding: utf-8; mode: python; mode: flycheck -*-
# pylint: disable=missing-docstring, too-few-public-methods
"""The googlefont module serves stuff to manage fonts from `fonts.google.com
<https://www.google.com/fonts>`__

"""

__all__ = [
    'GOOGLE_FONTS_HOST'
    , 'GOOGLE_FONTS_NETWORK'
    , 'GOOGLE_FONT_FORMATS'
    , 'GOOGLE_FONT_METADATA_CSV'
    , 'is_google_font_url'
    , 'resolve_google_ip'
    , 'read_google_font_css'
]

import logging
import socket
import ipaddress
from urllib.parse import urlparse
from urllib.request import urlopen
import requests

import fspath

log = logging.getLogger(__name__)

GOOGLE_FONTS_HOST = 'fonts.googleapis.com'
"""Hostname of the google fonts api (url)"""

GOOGLE_FONTS_GSTATIC = 'fonts.gstatic.com'
"""Hostname of the google fonts resource (url)"""

GOOGLE_FONTS_NETWORK = ipaddress.ip_network('172.217.0.0/16')
"""Google font network '172.217.0.0/16'"""

# user agent concept was stolen from https://github.com/glasslion/fontdump.git
GOOGLE_USER_AGENTS = {
    # pylint: disable=bad-continuation
    'woff2':  'Mozilla/5.0 (X11; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0'
    , 'ttf':  'Mozilla/5.0 (Linux; U; Android 2.2; en-us; DROID2 GLOBAL '
              'Build/S273) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 '
              'Mobile Safari/533.1' # Android 2
    , 'svg':  'Mozilla/5.0 (iPad; U; CPU OS 3_2 like Mac OS X; en-us) '
              'AppleWebKit/531.21.10 (KHTML, like Gecko) Version/4.0.4 '
              'Mobile/7B334b Safari/531.21.10'  # iOS<4.2
}

GOOGLE_FONT_FORMATS = list(GOOGLE_USER_AGENTS)
"""list of font formats used from google's font api"""

GOOGLE_FONT_METADATA_CSV = "https://raw.githubusercontent.com/googlefonts/FontClassificationTool/master/font-metadata.csv"

def is_google_font_url(url):
    """Test if ``url`` is from google font host ``fonts.googleapis.com``

    :param url:
        URL that match hostname ``fonts.googleapis.com`` and scheme
        ``http://`` or ``https://``

    """
    url = urlparse(url)
    hostname = url.netloc.split(':')[0]

    if ( hostname in (GOOGLE_FONTS_HOST, GOOGLE_FONTS_GSTATIC)
         and  url.scheme in ('http', 'https')):
        return True
    return False

def resolve_google_ip(url):
    """Resolve domain from google URL into IP.

    :type url: str
    :param url: URL of the google service

    :raises ConnectionError: Raised when the URL is not a google font URL (see
         :py:func:`is_google_font_url`) or the IP is not in the
         :py:obj:`GOOGLE_FONTS_NETWORK`

    """

    log.debug("try to solve %s", url)
    _url = urlparse(url)
    hostname = _url.netloc.split(':')[0]
    gf_ip = socket.gethostbyname(hostname)
    if ipaddress.ip_address(gf_ip) not in ipaddress.ip_network(GOOGLE_FONTS_NETWORK):
        log.error("got IP: %s for %s", gf_ip, url)
        raise ConnectionError(
            'got wrong IP %s [%s] not matching %s (may a local DNS blocks CDN?)' % (
                gf_ip, hostname, GOOGLE_FONTS_NETWORK))
    log.debug("got IP: %s for %s", gf_ip, url)
    return gf_ip

def read_google_font_css(url, format_list=None):
    """Read stylesheet's (CSS) content from ``url``

    :type url: str
    :param url:
        URL of the google CSS that defines the @font-face rules, e.g.:
        https://fonts.googleapis.com/css?family=Cute+Font|Roboto+Slab

    :type format_list: list
    :param format_list:
        A list with the formats to fetch (default: ``['woff2', 'ttf', 'svg']``)

    :rtype: bytes
    :return: CSS loaded from URL (request.content)

    :raises ConnectionError:
         Raised when the URL is not a google font URL (see
         :py:func:`resolve_google_ip`)
    """

    if not is_google_font_url(url):
        raise ConnectionError('%s is not a google font url matching %s' % (
            url, GOOGLE_FONTS_HOST))

    resolve_google_ip(url)
    if format_list is None:
        format_list = GOOGLE_FONT_FORMATS

    content = b''
    headers = {}

    for font_format in format_list:
        headers['User-Agent'] = GOOGLE_USER_AGENTS[font_format]
        log.debug("request: %s | User-Agent: %s" , url, headers['User-Agent'])
        resp = requests.get(url, headers=headers)
        content += resp.content
    return content


def list_fontnames():
    """Yield a list of *known* foontnames from ``fonts.googleapis.com``.

    .. hint::

      This funtion needs some more elaboration, the generated list is faulty in
      a very different way ...

      ATM I do not know a *singel point of definition* with a complete list of
      font names hosted on ``fonts.googleapis.com``.

    ATM ``fonts.googleapis.com`` lists 959 fonts.  When I grep the HTML from
    https://fonts.google.com/ I found 950 font names (see
    ``google-font-names.txt``).  The only list I have found is the list of font
    names from :data:`GOOGLE_FONT_METADATA_CSV`.  In this list there are only
    873 unique font names.

      The interim solution is to mix font names from ``google-font-names.txt``
      and :data:`GOOGLE_FONT_METADATA_CSV` into one list (containing 954 font
      names).

    """
    names = set()

    gfn_txt_file = fspath.FSPath(__file__).DIRNAME / 'google-font-names.txt'
    with gfn_txt_file.openTextFile() as gfn_txt:
        for line in gfn_txt:
            name = line.strip()
            if name and name[0] != '#':
                if name in names:
                    log.error("%s: duplicate %s", GOOGLE_FONT_METADATA_CSV, name)
                else:
                    names.add(name)

    with urlopen(GOOGLE_FONT_METADATA_CSV) as csv:
        _max_bytes  = int(csv.headers.get("Content-Length", 0))
        _csv_header = csv.readline()
        for line in csv:
            name, _ = line.decode('utf-8').split(':', 1)
            if name not in names:
                log.debug("adding %s from CSV table", name)
                names.add(name)

    for name in sorted(names):
        yield name

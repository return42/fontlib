# SPDX-License-Identifier: AGPL-3.0-or-later
"""The :py:obj:`fontlib.googlefont` module serves stuff to manage fonts from
`fonts.google.com <https://www.google.com/fonts>`__

"""

__all__ = [
    'GOOGLE_FONTS_HOST'
    , 'GOOGLE_FONT_FORMATS'
    , 'is_google_font_url'
    , 'read_google_font_css'
]

import logging
import urllib.parse
import requests

log = logging.getLogger(__name__)

GOOGLE_FONTS_HOST = 'fonts.googleapis.com'
"""Hostname of the google fonts api (url)"""

GOOGLE_FONTS_GSTATIC = 'fonts.gstatic.com'
"""Hostname of the google fonts resource (url)"""

# user agent concept was stolen from https://github.com/glasslion/fontdump.git
GOOGLE_USER_AGENTS = {
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

GOOGLE_METADATA_FONTS = 'https://fonts.google.com/metadata/fonts'
"""URL of the fonts database in JSON format.  The fonts are grouped in the list
``familyMetadataList``."""

def is_google_font_url(url):
    """Test if ``url`` is from google font host ``fonts.googleapis.com``

    :param url:
        URL that match hostname ``fonts.googleapis.com`` and scheme
        ``http://`` or ``https://``

    """
    url = urllib.parse.urlparse(url)
    hostname = url.netloc.split(':')[0]

    if ( hostname in (GOOGLE_FONTS_HOST, GOOGLE_FONTS_GSTATIC)
         and  url.scheme in ('http', 'https')):
        return True
    return False

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
    """

    if not is_google_font_url(url):
        raise ConnectionError(f'{url} is not a google font url matching {GOOGLE_FONTS_HOST}')

    if format_list is None:
        format_list = GOOGLE_FONT_FORMATS

    content = b''
    headers = {}

    for font_format in format_list:
        headers['User-Agent'] = GOOGLE_USER_AGENTS[font_format]
        log.debug("request: %s | User-Agent: %s" , url, headers['User-Agent'])
        resp = requests.get(url, headers=headers, timeout=30)
        content += resp.content
    return content


def font_map(cfg):
    """Return a dictionary of font families from ``fonts.googleapis.com``.

    A item in the returned dict contains of::

        <str: family-name> : {
            'category':    <str: category name>,
            'noto':        <bool: is noto font>,
            'css_url':     <str: URL>,
    }

    ``<str: category name>``:
      - Handwriting
      - Sans
      - ...

    ``<bool: is noto font>``:
      The font is (``True``) or is not (``False``) a `noto font`_

    ``<str: URL>``:
      URL to google's CSS with @font-face rules for this font family.

    .. _noto font: https://en.wikipedia.org/wiki/Noto_fonts

    """
    family_map = {}
    base_url = cfg.get('fontlib.googlefont.family_base_url')
    with requests.get(GOOGLE_METADATA_FONTS, timeout=30) as resp:
        if not resp.ok:
            raise ConnectionError(f'HTTP {resp.status_code} : {GOOGLE_METADATA_FONTS}')
        family_list = resp.json()['familyMetadataList']
        for item in family_list:
            family = item['family']
            if family in family_map:
                log.error('google: duplicate font-family-name: %s', family)

            family_map[family] = {
                'category':   item['category'],
                'noto':       item['isNoto'],
                'css_url':    base_url + urllib.parse.quote(family)
            }
    return family_map

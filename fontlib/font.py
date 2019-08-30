# -*- coding: utf-8; mode: python; mode: flycheck -*-
"""
Implemtation of :py:class:`Font`
"""

__all__ = ["Font", ]

from urllib.parse import urlparse

import logging
import base64
import hashlib
import pkg_resources
import mimetypes
import collections

from .css import get_css_at_rules
from .css import FontFaceRule

log = logging.getLogger(__name__)


# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# please pay attention whe adding new formats to FONTFACE_SRC_FORMAT; it is an
# ordered dict and the first '.startswith' will match!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

FONTFACE_SRC_FORMAT = _ = collections.OrderedDict()

# https://css-tricks.com/one-file-many-options-using-variable-fonts-web/
_['woff2-variations']  = ('.woff2', )

# https://www.w3.org/TR/2018/REC-css-fonts-3-20180920/#src-desc
_['woff2']  = ('.woff2', )           # WOFF 2.0 https://www.w3.org/TR/WOFF2/
_['woff'] = ('.woff', )              # WOFF 1.0 https://www.w3.org/TR/WOFF/
_['truetype'] = ('.ttf')             # TrueType --> https://docs.microsoft.com/en-us/typography/opentype/spec/
_['opentype'] = ('.otf', 'ttf' )    # OpenType --> https://docs.microsoft.com/en-us/typography/opentype/spec/
_['embedded-opentype'] = ('.eot', )  # Embedded OpenType --> https://www.w3.org/Submission/2008/SUBM-EOT-20080305/
_['svg'] = ('.svg', '.svgz')         # SVG Font --> https://www.w3.org/TR/SVG11/fonts.html

def _guess_format(src_format_string):
    if src_format_string is None:
        return None

    src_format_string = src_format_string.lower()
    if src_format_string in FONTFACE_SRC_FORMAT.keys():
        return src_format_string

    found_format = None

    for _format, extensions in FONTFACE_SRC_FORMAT.items():
        for ext in extensions:
            if ( src_format_string.startswith(ext)           # match '.<suffix>'
                 or src_format_string.startswith(ext[1:])):  # match '<suffix>'
                found_format = _format
                break

        if found_format is not None:
            break

    if found_format is not None:
        src_format_string = found_format
    return src_format_string


class Font:
    """A font resource identified by URL.

    :param url:
        URL of the font resource file
    :param font_name:
        Name of the font

    """
    # pylint: disable=too-few-public-methods

    def __init__(self, origin, font_name, unicode_range=None, src_format=None):

        self.origin = origin
        """The URL from `CSS @font-face:src`_ of the font resource."""

        _ = self.origin.encode('utf-8')
        _ = hashlib.md5(_).digest()
        _ = base64.urlsafe_b64encode(_)[:-2]
        self.ID = _.decode('utf-8')
        """A url-safe hash of font's resource URL, used as unique resource ID"""

        self.font_name = font_name
        """The font-name (value of `CSS @font-face:font-family`_)"""

        self.aliases = []
        """A list of alias font-names (values of `CSS @font-face:font-family`_)"""

        self.format = _guess_format(src_format)
        """Comma-separated list of format strings (`CSS @font-face:src`_)"""

        self.unicode_range = unicode_range
        """A string with the value of `CSS @font-face:unicode-range`_"""

    def __repr__(self):
        return "<font_name='%s', format='%s', ID='%s', origin='%s'>" % (
            self.font_name, self.format, self.ID, self.origin
        )

    def match_name(self, font_name):
        """Returns ``True`` if ``font_name`` match one of the names"""
        return self.font_name == font_name or font_name in self.aliases

    @classmethod
    def from_entry_point(cls, ep_name):
        """Build Font instances from python entry point

        :param ep_name:
            Name of the python entry point (e.g. ``fonts_ttf`` or ``fonts_woff2``)

        :rtype: [api.Font]
        :return:
            A generator of :py:class:`Font` instances.
        """

        ep_list = list(pkg_resources.iter_entry_points(ep_name))
        for entry_point in ep_list:
            log.debug("loading from entry point: %s (%s)", ep_name, entry_point)
            for name, file_name in entry_point.load().items():
                src_format = mimetypes.guess_type(file_name)[0]
                if src_format is not None:
                    src_format = src_format.split('/')[1]
                else:
                    src_format = file_name.split('.')[-1]
                # add font ...
                font = Font('file:' + file_name, name, src_format=src_format)
                yield font

    @classmethod
    def from_css(cls, css_url):
        """Get :py:class:`Font` objects from CSS Stylesheet

        :type css_url:   str
        :param css_url:  URL of the CSS (stylesheet) file

        :rtype: [api.Font]
        :return:
            A generator of :py:class:`Font` instances.
        """
        at_rules = get_css_at_rules(css_url, FontFaceRule)
        for rule in at_rules:
            yield  cls.from_at_rule(rule, css_url)

    @classmethod
    def from_at_rule(cls, at_rule, css_url):
        """Build Font instances from :py:class:`.css.AtRule` object.

        :param at_rule:
            ``@font-face`` rule, object of type :py:class:`.css.AtRule`

        :param css_url:
            URL of the CSS this ``@font-face`` rule comes from.  We need this
            base URL to calculate relative path names for the ``src``
            declarations.

        :rtype: [api.Font]
        :return:
            A generator of :py:class:`Font` instances.
        """

        base_url = "/".join(css_url.split('/')[:-1])
        src = at_rule.src()
        font_family = at_rule.font_family()
        origin = src['url']

        url = urlparse(origin)
        if url.scheme == '' and url.netloc == '' and url.path[0] != '/':
            # is relative path name
            origin = base_url + "/" + origin

        return Font(
            origin
            , font_family
            , at_rule.unicode_range()
            , src_format = src['format']
            )

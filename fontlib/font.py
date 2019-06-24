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

from .css import get_css_at_rules
from .css import FontFaceRule

log = logging.getLogger(__name__)

class Font:
    """A font resource identified by URL.

    :param url:
        URL of the font resource file
    :param font_name:
        Name of the font

    """
    # pylint: disable=too-few-public-methods

    def __init__(self, url, font_name, unicode_range=None, src_format=None):

        self.url = url
        """The URL from `CSS @font-face:src`_ of the font resource."""

        _ = self.url.encode('utf-8')
        _ = hashlib.md5(_).digest()
        _ = base64.urlsafe_b64encode(_)[:-2]
        self.ID = _.decode('utf-8')
        """A url-safe hash of font's resource URL, used as unique resource ID"""

        self.font_name = font_name
        """The font-name (value of `CSS @font-face:font-family`_)"""

        self.aliases = []
        """A list of alias font-names (values of `CSS font-family`_)"""

        if src_format.lower().startswith('woff2'):
            src_format = 'woff2'
        elif src_format.lower().startswith('woff'):
            src_format = 'woff'
        elif src_format.lower().startswith('svg'):
            src_format = 'svg'
        elif src_format.lower().startswith('ttf'):
            src_format = 'ttf'

        self.format = src_format
        """Comma-separated list of format strings (`CSS @font-face:src`_)"""

        self.unicode_range = unicode_range
        """A string with the value of `CSS @font-face:unicode-range`_"""


    def __repr__(self):
        return "<font_name='%s', format='%s', ID='%s', url='%s'>" % (
            self.font_name, self.format, self.ID, self.url
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
                # add font ...
                font = Font('file:' + file_name, name)
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
        url_str = src['url']

        url = urlparse(url_str)
        if url.scheme == '' and url.netloc == '' and url.path[0] != '/':
            # is relative path name
            url_str = base_url + "/" + url_str

        return Font(
            url_str
            , font_family
            , at_rule.unicode_range()
            , src_format = src['format']
            )

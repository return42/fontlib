# -*- coding: utf-8; mode: python; mode: flycheck -*-
"""
Implemtation of :py:class:`Font`
"""

__all__ = ["Font", ]

import logging
from urllib.parse import urlparse
import pkg_resources
from .css import get_css_at_rules
from .css import FontFaceRule

log = logging.getLogger(__name__)

class Font:
    """A font resource identified by URL"""
    # pylint: disable=too-few-public-methods

    def __init__(self, url, font_name):
        """Create :py:class:`.font.Font` instance

        :param url:
            URL of the font
        :param font_name:
            Name of the font
        """

        self.url = url
        self.name = font_name
        self.aliases = []

    def match_name(self, font_name):
        """Returns ``True`` if ``font_name`` match one of the names"""
        return self.name == font_name or font_name in self.aliases

    @classmethod
    def from_entry_point(cls, ep_name):
        """Build Font instances from python entry point

        :param ep_name:
            Name of the python entry point (e.g. ``fonts_ttf`` or ``fonts_woff2``)

        :return:
            A list of :py:class:`Font` instances.
        """

        ep_list = list(pkg_resources.iter_entry_points(ep_name))
        ret_val = []
        for entry_point in ep_list:
            log.debug("loading from entry point: %s (%s)" % (ep_name, entry_point))
            for name, file_name in entry_point.load().items():
                # add font ...
                font = Font('file:' + file_name, name)
                ret_val.append(font)
        return ret_val

    @classmethod
    def from_css(cls, css_url):
        at_rules = get_css_at_rules(css_url, FontFaceRule)
        for rule in at_rules:
            for font in cls.from_at_rule(rule, css_url):
                yield font

    @classmethod
    def from_at_rule(cls, at_rule, css_url):
        """Build Font instances from :py:class:`.css.AtRule` object.

        :param at_rule:
            ``@font-face`` rule, object of type :py:class:`.css.AtRule`

        :param css_url:
            URL of the CSS this ``@font-face`` rule comes from.  We need this
            base URL to calculate relative path names for the ``src``
            declarations.

        :return:
            A list of :py:class:`Font` instances.
        """
        base_url = "/".join(css_url.split('/')[:-1])
        name_list = at_rule.declaration_token_values('font-family', 'string')
        url_list =  at_rule.declaration_token_values('src', 'url')

        ret_val = []
        for font_name in name_list:
            for url_str in url_list:
                # log.debug("font-family: '%s' / src: url('%s')", font_name, url_str)
                url = urlparse(url_str)
                if url.scheme == '' and url.netloc == '' and url.path[0] != '/':
                    # is relative path name
                    url_str = base_url + "/" + url_str
                # add font ...
                font = Font(url_str, font_name)
                ret_val.append(font)
        return ret_val

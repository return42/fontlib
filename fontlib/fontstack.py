# -*- coding: utf-8; mode: python -*-
"""
Font library
"""

import logging
from urllib.parse import urlparse
import pkg_resources
import fspath

from .font import Font
from .css import get_css_at_rules
from .css import FontFaceRule

log = logging.getLogger(__name__)

class FontStack:
    """A collection of :class:`Font` objects"""

    def __init__(self):
        self.stack = dict()

    def add_font(self, font):
        if self.stack.get(font.url, None) is None:
            self.stack[font.url] = font
        else:
            self.stack[font.url].aliases.append(font.name)

    def load_entry_point(self, ep_name):
        for entry_point in pkg_resources.iter_entry_points(ep_name):
            print("%s: %s" % (ep_name, entry_point))
            for name, file_name in entry_point.load().items():
                # add font ...
                font = Font('file://' + file_name, name)
                self.add_font(font)

    def load_css(self, css_url):
        base_url = "/".join(css_url.split('/')[:-1])
        at_rules = get_css_at_rules(css_url, FontFaceRule)
        for rule in at_rules:
            name_list = rule.declaration_token_values('font-family', 'string')
            url_list =  rule.declaration_token_values('src', 'url')

            for font_name in name_list:
                for url_str in url_list:
                    url = urlparse(url_str)
                    if url.scheme == '' and url.netloc == '' and url.path[0] != '/':
                        # is relative path name
                        url_str = base_url + "/" + url_str
                    # add font ...
                    font = Font(url_str, font_name)
                    self.add_font(font)

    def list_fonts(self, font_name):
        """Return list of :class:`Font` objects selected by ``font_name``.

        :param font_name:
            Name of the font
        """
        ret_val = []
        for font in self.stack:
            if ( font.name == font_name
                 or font_name in font.aliases):
                ret_val.append(font)
        return ret_val


def get_stack():
    """
    Returns a :py:class:`FontStack` instance with fonts loaded.

    Fonts are loaded from builtin fonts and entry points.

    entry points:

    - ``fonts_ttf``
    - ``fonts_otf``
    - ``fonts_woff``
    - ``fonts_woff2``

    builtin fonts:

    - :ref:`builtin_cantarell`
    - :ref:`builtiin_dejavu`

    """
    stack = FontStack()
    # register font files from entry points
    for ep_name  in ['fonts_ttf', 'fonts_otf', 'fonts_woff', 'fonts_woff2']:
        stack.load_entry_point(ep_name)

    # register builtin fonts
    base = fspath.FSPath(__file__).DIRNAME / 'files'
    for name in [ 'cantarell', 'dejavu']:
        css_file = base / name / name + ".css"
        stack.load_css('file:' + css_file)

    return stack

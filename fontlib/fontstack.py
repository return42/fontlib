# -*- coding: utf-8; mode: python; mode: flycheck -*-
"""
Font library
"""

import logging
import fspath

from .font import Font

log = logging.getLogger(__name__)

class FontStack:
    """A collection of :py:class:`.api.Font` objects"""

    def __init__(self):
        self.stack = dict()

    def add_font(self, font):
        """Add :py:class:`.api.Font` object to *this* stack."""
        exists = self.stack.get(font.url, None)
        if exists is None:
            log.debug("add font-family: '%s' with url %s", font.font_name, font.url)
            #log.debug("with unicode-range : %s", font.unicode_range())
            self.stack[font.url] = font
        else:
            if exists.match_name(font.font_name):
                log.warning("Font already exists, skip additional Font '%s' with url '%s'"
                            , font.font_name, font.url)
            else:
                log.debug("add alias '%s' to url %s", font.font_name, font.url)
                exists.aliases.append(font.font_name)

    def load_entry_point(self, ep_name):
        """Add :py:class:`.api.Font` objects from ``ep_name``.

        :param ep_name:
           String with the name of the entry point (one of: ``fonts_ttf``,
           ``fonts_otf`` ``fonts_woff``, ``fonts_woff2``)
        """
        for font in Font.from_entry_point(ep_name):
            self.add_font(font)

    def load_css(self, css_url):
        """Add :py:class:`.api.Font` objects from `@font-face`_ rules.

        :param css_url:
            URL of a CSS (stylesheet) file defining ``@font-face`` rules
        """
        for font in Font.from_css(css_url):
            self.add_font(font)

    def list_fonts(self, font_name):
        """Return list of :py:class:`.api.Font` objects selected by ``font_name``.

        :param font_name:
            Name of the font
        """
        ret_val = []
        for font in self.stack.values():
            if font.match_name(font_name):
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

    E.g. to include all fonts from the fonts-python_ project install::

        $ pip install font-amatic-sc font-caladea font-font-awesome \\
                      font-fredoka-one font-hanken-grotesk font-intuitive \\
                      font-source-sans-pro  font-source-serif-pro

    .. _fonts-python: https://github.com/pimoroni/fonts-python
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

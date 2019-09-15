# -*- coding: utf-8; mode: python; mode: flycheck -*-
"""
Implementation of class :py:class:`FontStack`.
"""

__all__ = ['FontStack', ]

import logging
import fspath

from .db import fontlib_session
from .font import Font
from .font import FontAlias
from .urlcache import NoCache

log = logging.getLogger(__name__)

class FontStack:
    """A collection of :py:class:`.api.Font` objects"""

    def __init__(self):
        self.cache = NoCache()

    def set_cache(self, cache):
        """set cache"""
        log.debug('set cache: %s', str(cache))
        self.cache = cache

    def add_font(self, font):
        """Add :py:class:`.api.Font` object to *this* stack."""

        session = fontlib_session()
        p_obj = font.get_persistent_object(session)

        if p_obj:
            if p_obj.match_name(font.name):
                log.info(
                    "Font with identical origin and font name already exists,"
                    " skip additional Font '%s' with url '%s'"
                    , font.name, font.origin)
            else:
                log.debug("add alias '%s' to url %s", font.name, font.origin)
                p_obj.aliases.append(FontAlias(alias = font.name))

        else:
            log.debug("add font-family: %s", font)
            session.add(font)

        self.cache.add_url(font.origin)

    def save_font(self, font, dest_file):
        """Save BLOB of :py:class:`.api.Font` into file <dest_file>

        :param origin: :py:class:`.api.Font` object
        :param dest_file: Filename of the destination
        """
        self.cache.save_url(font.origin, dest_file)

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

    def list_fonts(self, name=None):
        """Return generator of :py:class:`.api.Font` objects selected by ``name``.

        :param name:
            Name of the font
        """
        # FIXME
        for font in self.stack.values():
            if name is None or font.match_name(name):
                yield font

    @classmethod
    def from_cfg(cls, config):
        """
        Returns a :py:class:`FontStack` instance with fonts loaded.

        FIXME

        Fonts are loaded from builtin fonts and entry points.

        available builtin fonts:

        - :ref:`builtin_cantarell`
        - :ref:`builtiin_dejavu`

        available entry points:

        - ``fonts_ttf``
        - ``fonts_otf``
        - ``fonts_woff``
        - ``fonts_woff2``

        E.g. to include all fonts from the fonts-python_ project install::

            $ pip install font-amatic-sc font-caladea font-font-awesome \\
                          font-fredoka-one font-hanken-grotesk font-intuitive \\
                          font-source-sans-pro  font-source-serif-pro

        """
        # get FontStack and set cache from configuration

        stack = cls()
        cache_cls = config.getfqnobj('fontstack', 'cache', fallback=NoCache)
        cache_obj = cache_cls()
        stack.set_cache(cache_obj)

        # register font files from entry points
        for ep_name in config.getlist('fontstack', 'entry points'):
            stack.load_entry_point(ep_name)

        # register builtin fonts
        base = fspath.FSPath(__file__).DIRNAME / 'files'
        for name in config.getlist('fontstack', 'builtin fonts'):
            log.debug('register builtin font: %s', name)
            css_file = base / name / name + ".css"
            stack.load_css('file:' + css_file)

        # register google fonts
        base_url = config.get('google fonts', 'family base url')
        for family in config.getlist('google fonts', 'fonts'):
            stack.load_css(base_url + family)

        return stack

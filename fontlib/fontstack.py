# SPDX-License-Identifier: AGPL-3.0-or-later
"""Implementation of class :py:class:`FontStack`.

"""

__all__ = ['FontStack', 'BUILTINS']

import logging
import fspath

from . import event
from .font import Font
from .font import FontAlias
from .urlcache import NoCache

log = logging.getLogger(__name__)

BUILTINS = fspath.FSPath(__file__).DIRNAME / 'files'
"""Folder where the builtin fonts are in."""


class FontStack:
    """A collection of :py:class:`.font.Font` objects"""

    def __init__(self, app):
        self.app = app
        self.cache = NoCache()

    def set_cache(self, cache):
        """set cache"""
        log.debug('set cache: %s', str(cache))
        self.cache = cache

    def add_font(self, font):
        """Add :py:class:`.font.Font` object to *this* stack.

        :param .font.Font font:  font instance.

        :py:func:`.event.emit`:

        - ``FontStack.add_font`` (:py:class:`font <.font.Font>`) is released if
          the added font is new to *this* stack.

        - ``FontStack.add_alias`` (:py:class:`alias <.font.FontAlias>`,
          :py:class:`font <.font.Font>`) is released if the added font is
          detected as an alias.

        """

        p_obj = font.identity(self.app.db.session)

        if p_obj:
            if p_obj.match_name(font.name):
                log.info(
                    "Font with identical origin and font name already exists,"
                    " skip additional font '%s' with url '%s'"
                    , font.name, font.origin)
            else:
                log.debug("add alias '%s' to url %s", font.name, font.origin)
                alias = FontAlias(alias_name = font.name)
                event.emit('FontStack.add_alias', alias, font)
                p_obj.aliases.append(alias)

        else:
            event.emit('FontStack.add_font', font)
            log.debug("add font-family: %s", font)
            self.app.db.session.add(font)

        self.cache.add_url(font.origin)

    def save_font(self, font, dest_file):
        """Save BLOB of :py:class:`.font.Font` into file <dest_file>

        :param font.Font font: font instance
        :param fspath.fspath.FSPath dest_file: Filename of the destination
        """
        self.cache.save_url(font.origin, dest_file)

    def load_entry_point(self, ep_name):
        """Add :py:class:`.font.Font` objects from ``ep_name``.

        :param ep_name:
           String with the name of the entry point (one of: ``fonts_ttf``,
           ``fonts_otf`` ``fonts_woff``, ``fonts_woff2``)

        :py:func:`.event.emit`:

        - ``FontStack.load_entry_point`` (:py:obj:`ep_name <str>`) is released
          each time funcion is called.

        """
        event.emit('FontStack.load_entry_point', ep_name)
        for font in Font.from_entry_point(ep_name):
            self.add_font(font)

    def load_css(self, css_url):
        """Add :py:class:`.font.Font` objects from `@font-face`_ rules.

        :param str css_url:
            URL of a CSS (stylesheet) file defining ``@font-face`` rules

        :py:func:`.event.emit`:

        - ``FontStack.load_css`` (:py:obj:`css_url <str>`) is released each time
          function is called.

        """
        event.emit('FontStack.load_css', css_url)
        for font in Font.from_css(css_url):
            self.add_font(font)

    def list_fonts(self, name=None):
        """Return generator of :py:class:`.font.Font` objects selected by ``name``.

        :param name:
            Name of the font
        """
        for font in self.app.db.session.query(Font):
            if name is None or font.match_name(name):
                yield font

    def init_stack(self):
        """Init fonstack.  Register fonts from various resources into the
        fontlib database.

        - register builtin fonts (config: ``fontlib.fontstack.builtin_fonts``)
        - register entry points (config: ``fontlib.fontstack.entry_points``)
        - register google fonts (config: ``fontlib.googlefont.family_base_url``)

        """

        for name in self.app.cfg.get('fontlib.fontstack.builtin_fonts'):
            log.debug('register builtin font: %s', name)
            css_file = BUILTINS / name / name + ".css"
            self.load_css('file:' + css_file)

        for ep_name in self.app.cfg.get('fontlib.fontstack.entry_points'):
            self.load_entry_point(ep_name)

        fonts = self.app.cfg.get('fontlib.googlefont.fonts')
        url = self.app.cfg.get('fontlib.googlefont.family_base_url')
        for family in fonts:
            self.load_css(url + family)

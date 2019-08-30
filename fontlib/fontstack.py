# -*- coding: utf-8; mode: python; mode: flycheck -*-
"""
Font library
"""

import logging
import fspath

from .font import Font

log = logging.getLogger(__name__)

def get_FQN(name):
    """
    Return Python Objekt that is refered by full qualiffied name

    .. code-block:: python

      >>> get_FQN("fontlib.urlcache.URLCache")
      <class 'fontlib.urlcache.URLCache'>
    """
    (modulename, name) = name.rsplit('.', 1)
    m = __import__(modulename, {}, {}, [name], 0)
    return getattr(m, name)


class FontStack:
    """A collection of :py:class:`.api.Font` objects"""

    def __init__(self):
        #cache_cls = get_FQN("fontlib.urlcache.SimpleURLCache")
        cache_cls = get_FQN("fontlib.urlcache.NoCache")
        self.cache = cache_cls()
        self.stack = dict()

    def add_font(self, font):
        """Add :py:class:`.api.Font` object to *this* stack."""
        exists = self.stack.get(font.origin, None)

        if exists is None:
            log.debug("add font-family: %s", font)
            self.stack[font.origin] = font
            self.cache.add_url(font.origin)

        else:
            if exists.match_name(font.font_name):
                log.warning("Font already exists, skip additional Font '%s' with url '%s'"
                            , font.font_name, font.origin)
            else:
                log.debug("add alias '%s' to url %s", font.font_name, font.origin)
                exists.aliases.append(font.font_name)

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

    def list_fonts(self, font_name=None):
        """Return generator of :py:class:`.api.Font` objects selected by ``font_name``.

        :param font_name:
            Name of the font
        """
        for font in self.stack.values():
            if font_name is None or font.match_name(font_name):
                yield font


def get_stack(config):
    """
    Returns a :py:class:`FontStack` instance with fonts loaded.

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
    stack = FontStack()

    # register builtin fonts
    base = fspath.FSPath(__file__).DIRNAME / 'files'
    for name in config.getlist('fontstack', 'builtin fonts'):
        log.debug('register builtin font: %s', name)
        css_file = base / name / name + ".css"
        stack.load_css('file:' + css_file)

    # register font files from entry points
    for ep_name in config.getlist('fontstack', 'entry points'):
        stack.load_entry_point(ep_name)

    # register google fonts
    base_url = config.get('google fonts', 'family base url')
    for family in config.getlist('google fonts', 'fonts'):
        stack.load_css(base_url + family)

    return stack

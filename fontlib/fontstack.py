# -*- coding: utf-8; mode: python -*-
"""
Font library
"""
import pkg_resources
import fspath
import tinycss
from tinycss.fonts3 import FontFaceRule

from .font import Font

class FontStack:
    """A collection of :class:`Font` objects"""

    def __init__(self):
        self.stack = dict()
        self.get = self.stack.get

    def add_url(self, url, font_name):
        """Add a font resource

        :param url:
            URL of the font
        :param font_name:
            Name of the font
        """
        font = self.get(url, None)
        if font is not None:
            font.aliases.append(font_name)
        else:
            self.stack[url] = Font(url, font_name)

    def get_fonts(self, font_name):
        """get :class:`Font` objects by font name

        :param font_name:
            Name of the font
        """
        ret_val = []
        for obj in self.stack:
            if ( obj.name == font_name
                 or font_name in obj.aliases):
                ret_val.append(obj)
        return ret_val

    def load_from_css(self, css_file, folder=""):
        """load font resources from CSS @font-face rules

        :param css_file:
            file name of the css file
        :param folder:
            Name of base folder where the font files are located.
        """
        parser = tinycss.make_parser('fonts3')
        stylesheet = parser.parse_stylesheet_file(css_file)

        # filter @font-face rules
        font_face_rules = [ rule for rule in stylesheet.rules
                            if isinstance(rule, FontFaceRule) ]

        for rule in font_face_rules:
            l_font_family = []
            l_uri = []

            for decl in rule.declarations:
                if decl.name == 'font-family':
                    for token in decl.value:
                        l_font_family.append(token.value)

                if decl.name == 'src':
                    for token in decl.value:
                        if token.type == 'URI':
                            l_uri.append(token.value)

            for font_name in l_font_family:
                for url in l_uri:
                    if folder:
                        url = folder + '/' + url
                    self.add_url(url, font_name)

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
        for entry_point in pkg_resources.iter_entry_points(ep_name):
            for name, val in entry_point.load().items():
                stack.add_url(val, name)

    # register builtin fonts
    base = fspath.FSPath(__file__).DIRNAME / 'files'
    for name in [ 'cantarell', 'dejavu']:
        css_file = base / name / name + ".css"
        stack.load_from_css( css_file, folder=base)

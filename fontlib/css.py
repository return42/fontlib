# -*- coding: utf-8; mode: python; mode: flycheck -*-
# pylint: disable=too-few-public-methods
"""
CSS helper
"""

__all__ = ['get_css_at_rules', 'CSSRule', 'AtRule', 'FontFaceRule']

import logging
import re
from urllib.request import urlopen

import tinycss2

from .googlefont import is_google_font_url
from .googlefont import read_google_font_css

log = logging.getLogger(__name__)

def get_css_at_rules(css_url, at_class):
    """Get at-rules of type ``at_class`` from CSS ``css_url``.

    The CSS file is read by :py:func:`urlopen`.  If the URL points to the google
    fonts api, the CSS is read by :py:func:`.googlefont.read_google_font_css`.
    Both funtions return the byte stream from the URL, which is parsed by
    :py:func:`tinycss2.parse_stylesheet_bytes`.  The resulting CSS rules are
    filtered by ``at_class``.

    :type css_url:   str
    :param css_url:  URL of the CSS (stylesheet) file

    :type at_class:  css.AtRule
    :param at_class: class of the at-rule

    :rtype: [css.AtRule]
    :return: list of ``at_class`` objects
    """
    if is_google_font_url(css_url):
        css_bytes = read_google_font_css(css_url)
    else:
        with urlopen(css_url) as handle:
            css_bytes= handle.read()

    # parse css ...
    css_rules, _encoding = tinycss2.parse_stylesheet_bytes(css_bytes=css_bytes)

    # filter @font-face (at rules)
    font_face_rules =  [
        rule for rule in css_rules
        if (rule.type == 'at-rule' and rule.at_keyword == at_class.rule_name) ]

    # instances of class CSSRule
    css_rules = []
    for rule in font_face_rules:
        obj = at_class(css_url=css_url)
        css_rules.append(obj)
        obj.parse_css_rule(rule)

    log.debug("found %s at-rules", len(css_rules))
    return css_rules


def split_tokens(rule_tokens, t_type='literal', t_value=';'):
    """Split list of tokens into a list of token lists.

    By a delimiter, the ``rule_tokens`` list is splitted into groups.
    Delimiters are tokens with type ``t_type`` and value ``t_value``.
    Delimiter tokens and ``whitespace`` tokens are stripped from the
    returned lists.

    The default ``t_type`` and ``t_value`` are good to consume a list of
    declarations:

    - https://drafts.csswg.org/css-syntax-3/#consume-a-list-of-declarations

    :param rule_tokens:
        A list of :class:`tinycss.ast.Node`
    :param t_type:
        String with the type of the delimiter token (default=``literal``)
    :param t_value:
        String with the value of the delimiter token (default=``;``)
    :returns: a list of lists with token in (:class:`tinycss.ast.Node`)
    :return: list

    """
    decl_tokens = []
    current = []
    for token in rule_tokens:
        if token.type in ['whitespace',]:
            # strip whitespaces
            continue
        elif token.type == t_type and token.value == t_value:
            decl_tokens.append(current)
            current = []
        else:
            current.append(token)
    return decl_tokens


class CSSRule:
    """Base class for internal abstraction of a CSS rules."""

    rule_name = None
    """String with the name of the rule"""
    rule_type = None
    """String naming the type of the rule"""

    def __init__(self, css_url, *args, **kwargs):  # pylint: disable=unused-argument
        self.css_url = css_url
        """URL of the CSS (stylesheet) file"""
        self.content = []
        self.declarations = dict()
        """Python dict with CSS declarations"""

    def serialize(self):
        """Returns a string of the CSS rule."""
        return tinycss2.serialize(self.content)

    def parse_css_rule(self, rule):
        """Parse CSS rule

        TODO: needs some documentation
        """
        self.content = rule.content
        self.declarations = dict()

        for decl in split_tokens(self.content, t_type='literal', t_value=';'):
            decl_name = None
            colon = False

            for token in decl:
                # iterate until first ident-token
                if decl_name is None:
                    if token.type == 'ident':
                        decl_name = token.value.lower()
                        self.declarations[decl_name] = []
                    continue
                # iterate until first colon ``:``
                if decl_name and colon is False:
                    if token.type == 'literal' and token.value == ':':
                        colon = True
                    continue

                # parse with method parse_decl_<decl_name>, if this does not
                # exists, use self.parse_decl

                method_name = re.sub('[^a-zA-Z0-9]', '_', decl_name)
                parse_method = getattr(self, 'parse_decl_%s' % method_name, self.parse_decl)
                parse_method(decl_name, token)

    def parse_decl(self, decl_name, token):
        """Default method to parse declarations."""
        # ignore whitespace and literal tokens
        if token.type in ['whitespace', 'literal']:
            return
        self.declarations[decl_name].append(token)


class AtRule(CSSRule):
    """Internal abstraction of a CSS `at-rule`_."""

    rule_type = 'at-rule'

    # def declaration_token_values(self, decl_name, *token_types):
    #     """Get token values from tokens of ``decl_name`` and ``token_types``.

    #     Select token values from *this* at-rule declarations.  E.g. to get all
    #     ``url`` tokens from the declaration ``src`` use::

    #         url_list = my_rule.declaration_token_values('src', 'url')

    #     To select the name of a font-family declaration use ``string`` type::

    #         font_name = my_rule.declaration_token_values('font-family', 'string')

    #     :param decl_name:
    #         A string with the name of the declaration (e.g. ``src`` or
    #         ``font-family``).

    #     :param \\*token_types:
    #         A list of string arguments with the name of token's type (e.g.
    #         ``string`` or ``url``).

    #     :return:
    #         A list with the **values** of the selected tokens.
    #     """
    #     ret_val = []
    #     decl = self.declarations.get(decl_name, None)
    #     if decl is not None:
    #         ret_val = [ token.value for token in decl if token.type in token_types ]
    #     # log.debug("declaration_token_values(%s, *%s): --> %s", decl_name, token_types, ret_val)
    #     return ret_val


class FontFaceRule(AtRule):
    """Internal abstraction of a CSS ``@font-face``."""
    rule_name = 'font-face'

    def font_family(self):
        """Return a string with the font-family name

        This descriptor defines the font family name that will be used in all
        CSS font family name matching.  It is required for the @font-face rule
        to be valid (`CSS @font-face:font-family`_).
        """
        ret_val = []
        decl = self.declarations.get('font-family', None)
        if decl is None:
            log.error("invalid @font-face rule, missing declartion: font-family")
        else:
            ret_val = [ token.value for token in decl if token.type == 'string' ]
        return ' '.join(ret_val)

    def src(self):
        """Returns a dictionary with ``src`` values.

        This descriptor specifies the resource containing font data. It is
        required for the @font-face rule to be valid.  Its value is a
        prioritized, comma-separated list of external references or
        locally-installed font face names (`CSS @font-face:src`_).

        url:
          As with other URLs in CSS, the URL may be relative, in which case it
          is resolved relative to the location of the style sheet containing the
          @font-face rule.

          In the case of SVG fonts, the URL points to an element within a
          document containing SVG font definitions.

        local:
          When authors would prefer to use a locally available copy of a given
          font and download it if it's not, local() can be used.

          The local-value in the dictionary contains a comma-separated list of
          *local* font-face names (``<font-face-name>, <font-face-name>, ...``)

        format:
          The format hint contains a comma-separated list of format strings that
          denote well-known font formats.

        """
        # pylint: disable=too-many-branches
        ret_val = dict(url=None, format=None, local=[], )
        decl = self.declarations.get('src', None)
        if decl is None:
            log.error("invalid @font-face rule, missing declartion: src")
        else:
            for token in decl:

                if token.type == 'url':
                    ret_val['url'] = token.value

                elif token.type == 'function':
                    if token.name == 'format':
                        if not token.arguments:
                            log.error("invalid @font-face rule, declartion src: format(...) token missing argument")
                        else:
                            ret_val['format'] = ",".join([_.value for _ in token.arguments])
                    elif token.name == 'local':
                        if not token.arguments:
                            log.error("invalid @font-face rule, declartion src: local(...) token missing argument")
                        else:
                            ret_val['local'] = ",".join([_.value for _ in token.arguments])
                    else:
                        log.warning("@font-face rule, declartion src: ignore function token: %s", token)

                else:
                    log.warning("@font-face rule, declartion src: ignore token: %s", token)

        return ret_val


    def unicode_range(self):
        """Returns a comma separeted string with unicode ranges.

        This descriptor defines the set of Unicode codepoints that may be
        supported by the font face for which it is declared.  The descriptor
        value is a comma-delimited list of Unicode range (<urange>) values.  The
        union of these ranges defines the set of codepoints that serves as a
        hint for user agents when deciding whether or not to download a font
        resgource for a given text run (`CSS @font-face:unicode-range`_).
        """
        ret_val = []
        decl = self.declarations.get('unicode-range', None)
        if decl is not None:
            ret_val = [ token.serialize() for token in decl ]
        return ', '.join(ret_val)

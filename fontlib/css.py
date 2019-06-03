# -*- coding: utf-8; mode: python; mode: flycheck -*-
# pylint: disable=missing-docstring, too-few-public-methods
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
    """get at-rules of type ``at_class`` from CSS ``css_url``

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

    By a delimiter, the ``rule_token`` list is splitted into groups.
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

    def parse_css_rule(self, rule):
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

                method_name = re.sub('[^a-zA-Z0-9]', '_', decl_name)
                parse_method = getattr(self, 'parse_decl_%s' % method_name, self.parse_decl)
                parse_method(decl_name, token)

    def parse_decl(self, decl_name, token):
        # ignore whitespace and literal tokens
        if token.type in ['whitespace', 'literal']:
            return
        self.declarations[decl_name].append(token)


class AtRule(CSSRule):
    """Internal abstraction of a CSS at-rule."""

    rule_type = 'at-rule'

    def declaration_token_values(self, decl_name, *token_types):
        """Get token values from tokens of ``decl_name`` and ``token_types``.

        Select token values from *this* at-rule declarations.  E.g. to get all
        ``url`` tokens from the declaration ``src`` use::

            url_list = my_rule.declaration_token_values('src', 'url')

        To select the name of a font-family declaration use ``string`` type::

            font_name = my_rule.declaration_token_values('font-family', 'string')

        :param decl_name:
            A string with the name of the declaration (e.g. ``src`` or
            ``font-family``).

        :param \\*token_types:
            A list of string arguments with the name of token's type (e.g.
            ``string`` or ``url``).

        :return:
            A list with the **values** of the selected tokens.
        """
        ret_val = []
        decl = self.declarations.get(decl_name, None)
        if decl is not None:
            ret_val = [ token.value for token in decl if token.type in token_types ]
        # log.debug("declaration_token_values(%s, *%s): --> %s", decl_name, token_types, ret_val)
        return ret_val


class FontFaceRule(AtRule):
    """Internal abstraction of a CSS ``@font-face``."""
    rule_name = 'font-face'

    def font_family(self):
        return ' '.join(self.declaration_token_values('font-family', 'string'))


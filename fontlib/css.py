# -*- coding: utf-8; mode: python -*-
# pylint: disable=missing-docstring, too-few-public-methods
"""
CSS helper
"""

__all__ = ['get_css_at_rules', 'FontFaceRule']

import re
from urllib.request import urlopen

import tinycss2


def get_css_at_rules(css_url, at_class):

    # parse css ...
    with urlopen(css_url) as handle:
        css_rules, _encoding = tinycss2.parse_stylesheet_bytes(css_bytes = handle.read())

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

    return css_rules


def split_tokens(rule_tokens, t_type='literal', t_value=';'):
    """Split list of tokens into a list of token lists.

    By a delimiter, the ``rule_token`` list is spitted into groups.
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
    rule_name = None
    rule_type = None

    def __init__(self, css_url, *args, **kwargs):  # pylint: disable=unused-argument
        self.css_url = css_url
        self.content = []
        self.declarations = dict()

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
    rule_type = 'at-rule'

    def declaration_token_values(self, decl_name, *token_types):
        decl = self.declarations.get(decl_name, None)
        if decl is None:
            return []
        return [ token.value for token in decl if token.type in token_types ]

class FontFaceRule(AtRule):
    rule_name = 'font-face'

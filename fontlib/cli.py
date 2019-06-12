# -*- coding: utf-8; mode: python; mode: flycheck -*-

u"""fontlib -- main entry point for commandline interfaces"""

import sys
import logging
from logging.config import dictConfig

from fspath import CLI
from fspath.sui import SimpleUserInterface

from .fontstack import FontStack
from .fontstack import get_stack
from .log import cfg as log_cfg
from .mime import add_types
log = logging.getLogger(__name__)

# ==============================================================================
def _cli_parse_css(args):
# ==============================================================================

    u"""
    Parse ``@font-face`` rules from <url>.

    Load CSS (stylesheet) from <url> and filter ``@font-face`` rules.  E.g. google
    fonts API 'https://fonts.googleapis.com/css?family=Cute+Font|Roboto+Slab' or
    built-in *dejavu* fonts from url 'file:./fontlib/files/dejavu/dejavu.css'.
    """

    cli = args.CLI
    cli.UI.echo("load css from url: %s" % args.url)

    font_stack = FontStack()
    font_stack.load_css(args.url)

    cli.UI.rst_table(
        font_stack.stack.values()
        # <col-title>, <format sting>, <attribute name>
        , ("Name",     "%-50s",        "font_name")
        , ("URL",      "%-90s",        "url") )

# ==============================================================================
def _cli_list_fonts(args):
# ==============================================================================

    u"""
    List (builtin) fonts.
    """

    cli = args.CLI
    font_stack = get_stack()
    cli.UI.rst_table(
        font_stack.stack.values()
        # <col-title>, <format sting>, <attribute name>
        , ("Name",     "%-50s",        "font_name")
        , ("URL",      "%-90s",        "url") )


# ==============================================================================
def main():
# ==============================================================================

    u"""
    Tools from the fontlib library
    """

    dictConfig(log_cfg)
    add_types()

    cli    = CLI(description=main.__doc__)
    cli.UI = SimpleUserInterface(cli=cli)

    css_parse = cli.addCMDParser(_cli_parse_css, cmdName='css-parse')
    css_parse.add_argument(
        "url"
        , type = str
        , help = "<url> of ccs to parse"
        )
    css_parse = cli.addCMDParser(_cli_list_fonts, cmdName='list')

    # run ...
    cli()

if __name__ == '__main__':
    sys.exit(main())

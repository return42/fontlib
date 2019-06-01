# -*- coding: utf-8; mode: python -*-

u"""fontlib -- main entry point for commandline interfaces"""

import sys
import logging
from logging.config import dictConfig

from fspath import CLI
from fspath.sui import SimpleUserInterface

from .fontstack import FontStack
from .log import cfg as log_cfg

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

    fs = FontStack()
    fs.load_css(args.url)

    cli.UI.rst_table(
        fs.stack.values()
        # <col-title>, <format sting>, <attribute name>
        , ("Name",     "%-50s",        "name")
        , ("URL",      "%-90s",        "url") )


# ==============================================================================
def main():
# ==============================================================================

    u"""
    Tools from the fontlib library
    """

    dictConfig(log_cfg)

    cli    = CLI(description=main.__doc__)
    cli.UI = SimpleUserInterface(cli=cli)

    css_parse = cli.addCMDParser(_cli_parse_css, cmdName='css-parse')
    css_parse.add_argument(
        "url"
        , type = str
        , help = "<url> of ccs to parse"
        )

    # run ...
    cli()

if __name__ == '__main__':
    sys.exit(main())

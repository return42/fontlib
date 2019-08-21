# -*- coding: utf-8; mode: python; mode: flycheck -*-

u"""fontlib -- main entry point for commandline interfaces"""

import sys
import logging
from logging.config import dictConfig
from urllib.parse import urlparse

from fspath import CLI
from fspath import FSPath
from fspath.sui import SimpleUserInterface

from .fontstack import FontStack
from .fontstack import get_stack
from .log import cfg as log_cfg
from .mime import add_types
from .config import Config

log = logging.getLogger(__name__)

UNKNOWN = object()
CONFIG = Config()
USER_INI = FSPath("~/.fontlib.ini")

# pylint: disable=bad-continuation
CMDARG_TO_CFG = {
    # cli-argument    : (cfg-section, cfg-option) # see ./config.ini
    'builtins'        : ('fontstack', 'builtin fonts')
    , 'epfonts'       : ('fontstack', 'entry points')
    , 'google'        : ('google fonts', 'fonts')
}
# pylint: enable=bad-continuation

def main():
    """Tools from the fontlib library."""
    dictConfig(log_cfg)
    add_types()

    cli = CLI(description=main.__doc__)
    cli.UI = SimpleUserInterface(cli=cli)

    # config ...

    cli.add_argument(
        '-c', '--config'
        , help = 'specify config file'
        , dest = 'config'
        , type = FSPath
        , default = USER_INI
        , nargs = '?'
        , metavar = 'INI-FILE' )

    # cmd: list ...

    list_fonts = cli.addCMDParser(cli_list_fonts, cmdName='list')
    add_fontstack_options(list_fonts)

    # cmd: css-parse

    css_parse = cli.addCMDParser(cli_parse_css, cmdName='css-parse')
    css_parse.add_argument(
        "url"
        , type = str
        , help = "URL of stylesheet (CSS) to parse"
    )

    download_family = cli.addCMDParser(cli_download_family, cmdName='download')
    add_fontstack_options(download_family)
    download_family .add_argument(
        "dest"
        , type = FSPath
        , help = "Folder where the download will be placed."
    )
    download_family .add_argument(
        "family"
        , type = str
        , nargs = '+'
        , help = (
            "the font name, the value of CSS font-family property."
            "E.g.  'Roboto Slab' 'DejaVu Sans Mono'")
    )

    # run ...
    cli()


def cli_list_fonts(args):
    """List fonts from *builtins*, *fonts.googleapis.com* and other resources.

    Option --google add fonts from google fonts infrastructure.  Select font
    families from:

        https://fonts.google.com

    Option --ep-fonts add fonts from entry points, see:

        https://pypi.org/project/fonts

    To install fonts from the *python fonts project* e.g. run::

        $ pip install --user \\
              font-amatic-sc font-caladea font-font-awesome \\
              font-fredoka-one font-hanken-grotesk font-intuitive \\
              font-source-sans-pro font-source-serif-pro

    """
    init_cfg(args)

    cli = args.CLI
    stack = get_stack(CONFIG)

    def table_rows():

        for font in stack.list_fonts():

            closest = font.origin
            blob_state = stack.cache.url_state(font.origin)
            if blob_state == 'cached':
                closest = stack.cache.fname_by_url(font.origin)

            yield dict(
                ID = font.ID
                , font_name = font.font_name
                , format = font.format
                , origin = font.origin
                , blob_state = blob_state
                , closest = closest
                )

    cli.UI.rst_table(
        table_rows()
        # <col-title>,      <format sting>, <attribute name>
        , ("cache sate",    "%-10s",        "blob_state")
        , ("name",          "%-40s",        "font_name")
        , ("format",        "%-10s",        "format")
        , ("font ID",       "%-22s",        "ID")
        , ("location",      "%-90s",        "closest") )


def cli_parse_css(args):
    """Parse ``@font-face`` rules from <url>.

    Load CSS (stylesheet) from <url> and filter ``@font-face`` rules.  E.g. google
    fonts API 'https://fonts.googleapis.com/css?family=Cute+Font|Roboto+Slab' or
    built-in *dejavu* fonts from url 'file:./fontlib/files/dejavu/dejavu.css'.

    """
    init_cfg(args)
    cli = args.CLI
    cli.UI.echo("load css from url: %s" % args.url)

    font_stack = FontStack()
    font_stack.load_css(args.url)

    cli.UI.rst_table(
        font_stack.stack.values()
        # <col-title>, <format sting>, <attribute name>
        , ("name",          "%-40s",        "font_name")
        , ("format",        "%-10s",        "format")
        , ("font ID",       "%-22s",        "ID")
        , ("URL",           "%-90s",        "origin") )


def cli_download_family(args):
    """Download font-family <family> into folder <dest>."""

    init_cfg(args)

    cli = args.CLI
    stack = get_stack(CONFIG)

    if args.dest.EXISTS:
        cli.UI.echo("INFO: use existing folder %s" % args.dest)
    else:
        cli.UI.echo("INFO: createfolder %s" % args.dest)
        args.dest.makedirs()

    count = 0
    for font_family in args.family:
        c = 0

        for font in stack.list_fonts(font_family):
            url = urlparse(font.origin)
            dest_file = args.dest / FSPath(url.path).BASENAME
            if url.query:
                # the resource is not a typical file URL with a file name, lets use
                # the fonts resource ID as a file name
                dest_file = args.dest / str(font.ID) + '.' + font.format

            cli.UI.echo("[%s]: download %s from %s" % (
                font.font_name, dest_file, font.origin))
            stack.save_font(font, dest_file)
            c += 1
        if c == 0:
            cli.UI.echo("ERROR: unknow font-family: %s" % font_family)
        count += c

    cli.UI.echo("download %s files into %s" % (count, args.dest))

# ==============================================================================
# helper ...
# ==============================================================================

def add_fontstack_options(cmd):
    """Adds common fontstack options to comand"""
    cmd.add_argument(
        "--builtins"
        , dest = 'builtins'
        , default = CONFIG.get(*CMDARG_TO_CFG['builtins'][:2])
        , nargs = '?', type = str
        , help = "use builtin fonts"
        )

    cmd.add_argument(
        "--ep-fonts"
        , dest = 'epfonts'
        , default = CONFIG.get(*CMDARG_TO_CFG['epfonts'][:2])
        , nargs = '?', type = str
        , help = "use fonts from entry points"
        )

    cmd.add_argument(
        "--google"
        , dest = 'google'
        , default = CONFIG.get(*CMDARG_TO_CFG['google'][:2])
        , nargs = '?', type = str
        , help = "use fonts from fonts.googleapis.com"
        )


def init_cfg(args):
    """Update the :py:class:`.config.Config` object from command line arguments"""

    # load INI files ...

    if args.config != USER_INI and not args.config.EXPANDUSER.EXISTS:
        raise args.Error(42, 'config file does not extsts: %s' % args.config)
    CONFIG.read(args.config.EXPANDUSER)

    # update config from command line ..

    for arg_name, (cfg_sect, cfg_opt) in CMDARG_TO_CFG.items():
        value = args.__dict__.get(arg_name, UNKNOWN)
        if value is UNKNOWN:
            continue
        if value is None:
            value = ''
        log.debug("set %s/%s = %s", cfg_sect, cfg_opt, value)
        CONFIG.set(cfg_sect, cfg_opt, value)

# ==============================================================================
# call main ...
# ==============================================================================

if __name__ == '__main__':
    sys.exit(main())

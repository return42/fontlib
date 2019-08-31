# -*- coding: utf-8; mode: python; mode: flycheck -*-
# pylint: disable=global-statement

"""Command line tools from the fontlib library."""

import sys
import configparser
import logging.config
import platform
from urllib.parse import urlparse

from fspath import CLI
from fspath import FSPath
from fspath.sui import SimpleUserInterface

from . import __pkginfo__
from .fontstack import FontStack
from .fontstack import get_stack
from .log import DEFAULT_LOG_INI
from .log import FONTLIB_LOGGER
from .log import init_log
from .config import Config

UNKNOWN = object()
CONFIG = None

DEFAULT_WORKSPACE = FSPath('~/.fontlib').EXPANDUSER
CONFIG_INI = 'config.ini'
LOG_INI = 'log.ini'

log = logging.getLogger(__name__)

def main():
    global CONFIG
    init_main()
    app_ws = CONFIG.getpath('DEFAULT', 'workspace', fallback=DEFAULT_WORKSPACE)

    cli = CLI(description=__doc__)
    cli.UI = SimpleUserInterface(cli=cli)

    # config ...

    cli.add_argument(
        '-c', '--config'
        , help = 'specify config file'
        , dest = 'config'
        , type = FSPath
        , default = app_ws / CONFIG_INI
        , nargs = '?'
        , metavar = 'INI-FILE' )

    cli.add_argument(
        "--workspace"
        , dest = 'workspace'
        , default = CONFIG.get(*MAP_ARG_TO_CFG['workspace'][:2])
        , type = FSPath
        , help = "workspace"
        )

    # cmd: README ...

    readme = cli.addCMDParser(cli_README, cmdName='README')

    # cmd: version ...

    _ = cli.addCMDParser(cli_version, cmdName='version')

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

    # cmd: download ...

    download_family = cli.addCMDParser(cli_download_family, cmdName='download')
    add_fontstack_options(download_family)
    download_family.add_argument(
        "dest"
        , type = FSPath
        , help = "Folder where the download will be placed."
    )
    download_family.add_argument(
        "family"
        , type = str
        , nargs = '+'
        , help = (
            "Font's name, the value of CSS font-family property."
            "E.g. 'Roboto Slab' or 'DejaVu Sans Mono'"
        )
    )

    # cmd: config

    cfg = cli.addCMDParser(cli_config, cmdName='config')
    add_fontstack_options(cfg)
    cfg.add_argument(
        '--force'
        , action  = 'store_true'
        , help = 'force command'
    )
    cfg.add_argument(
        "subcommand"
        , type = str
        , choices=['show', 'install']
        , help = "available subcommands: %(choices)s"
    )
    cfg.add_argument(
        "argument_list"
        , type = str
        , nargs = '*'
        , help = "arguments of the subcommand"
        , metavar = 'ARG'
    )

    # run ...
    cli()

def cli_README(args):
    """prints README to stdout"""
    init_app(args)
    cli = args.CLI
    cli.UI.echo(__pkginfo__.docstring)

def cli_version(args):
    """prints version infos to stdout"""
    init_app(args)
    cli = args.CLI
    cli.UI.echo(" | ".join(
        [ __pkginfo__.version
          , platform.python_version()
          , platform.node()
          , platform.platform()]
    ))

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
    init_app(args)

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
    init_app(args)
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
    init_app(args)

    cli = args.CLI
    stack = get_stack(CONFIG)

    if args.dest.EXISTS:
        log.info("use existing folder %s", args.dest)
    else:
        log.info("createfolder %s", args.dest)
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

def cli_config(args):
    """Inspect configuration (working with INI files).

    commands:
      show:       print configuration
      install:    install default configuration (optional ARG1: <dest-folder>)

    """
    cli = args.CLI
    init_app(args, verbose=True)

    if args.subcommand == 'install':

        folder = CONFIG.getpath('DEFAULT', 'workspace', fallback=DEFAULT_WORKSPACE)
        if args.argument_list:
            folder = FSPath(args.argument_list[0])
        folder.makedirs()

        dest = folder / 'config.ini'
        cli.UI.echo("install:  %s" % dest)
        if dest.EXISTS and not args.force:
            raise args.Error(42, "file %s already exists (use --force to overwrite)" % dest)
        CONFIG.DEFAULT_INI.copyfile(dest)

        dest = folder / 'log.ini'
        cli.UI.echo("install:  %s" % dest)
        if dest.EXISTS and not args.force:
            raise args.Error(42, "file %s already exists (use --force to overwrite)" % dest)
        DEFAULT_LOG_INI.copyfile(dest)

        return

    if args.subcommand == 'show':

        cli.UI.rst_title("config.ini")
        CONFIG.write(cli.OUT)

        cli.UI.rst_title("log.ini")
        log_cfg = configparser.ConfigParser()
        log_cfg.read(CONFIG.get("logging", "config", fallback=DEFAULT_LOG_INI))
        log_cfg.write(cli.OUT)

        return

# ==============================================================================
# helper ...
# ==============================================================================

# pylint: disable=bad-continuation
MAP_ARG_TO_CFG = {
    # cli-argument    : (cfg-section, cfg-option) # see ./config.ini
    'builtins'        : ('fontstack', 'builtin fonts')
    , 'epfonts'       : ('fontstack', 'entry points')
    , 'google'        : ('google fonts', 'fonts')
    , 'workspace'     : ('DEFAULT', 'workspace')
}
"""Maps comand line arguments to config section & option"""
# pylint: enable=bad-continuation

def map_arg_to_cfg(args, cfg):
    """update application's CONFIG from command line arguments.."""
    for arg_name, (cfg_sect, cfg_opt) in MAP_ARG_TO_CFG.items():
        value = args.__dict__.get(arg_name, UNKNOWN)
        if value is UNKNOWN:
            continue
        if value is None:
            value = ''
        log.debug("set %s/%s = %s", cfg_sect, cfg_opt, value)
        cfg.set(cfg_sect, cfg_opt, str(value))

def add_fontstack_options(cmd):
    """Adds common fontstack options to comand"""

    cmd.add_argument(
        "--builtins"
        , dest = 'builtins'
        , default = CONFIG.get(*MAP_ARG_TO_CFG['builtins'][:2])
        , nargs = '?', type = str
        , help = "use builtin fonts"
        )

    cmd.add_argument(
        "--ep-fonts"
        , dest = 'epfonts'
        , default = CONFIG.get(*MAP_ARG_TO_CFG['epfonts'][:2])
        , nargs = '?', type = str
        , help = "use fonts from entry points"
        )

    cmd.add_argument(
        "--google"
        , dest = 'google'
        , default = CONFIG.get(*MAP_ARG_TO_CFG['google'][:2])
        , nargs = '?', type = str
        , help = "use fonts from fonts.googleapis.com"
        )

def init_main():
    """Init routine for the very first the main function."""
    global CONFIG

    # init main's CONFIG from INI file

    CONFIG = Config()
    app_ws = CONFIG.getpath('DEFAULT', 'workspace', fallback=DEFAULT_WORKSPACE)
    app_ws.makedirs()
    log.debug("using workspace at: %s", app_ws)

    # init main logging with (new) CONFIG settings

    log_cfg = CONFIG.get("logging", "config", fallback=DEFAULT_LOG_INI)
    env = CONFIG.config_env(
        app = 'cli'
        , workspace = DEFAULT_WORKSPACE
    )
    init_log(log_cfg, defaults=env)


def init_app(args, verbose=False):
    """Init the :py:obj:`CONFIG` object and LOG settings from command line arguments"""
    global CONFIG

    verbose = verbose or args.verbose
    _ = args.CLI.UI

    # init application's CONFIG from INI file

    if args.config != DEFAULT_WORKSPACE / CONFIG_INI:
        # assert config if --config was explicite set
        if not args.config.EXISTS:
            raise args.Error(42, 'config file does not exists: %s' % args.config)
    if verbose and args.config.EXISTS:
        _.echo("load configuration from: %s" % args.config)
    CONFIG.read(args.config)
    map_arg_to_cfg(args, CONFIG)

    app_ws = CONFIG.getpath('DEFAULT', 'workspace', fallback=DEFAULT_WORKSPACE)
    app_ws.makedirs()
    if verbose:
        args.ERR.write("using workspace: %s\n" % app_ws)
    app_ws.makedirs()

    # init app logging with (new) CONFIG settings

    logger = logging.getLogger(FONTLIB_LOGGER)

    if args.debug:
        CONFIG.set("logging", "level", 'debug')

    level = CONFIG.get("logging", "level").upper()
    if verbose:
        args.ERR.write("set log level of logger: %s (%s)\n" % (logger.name, level))

    logger.setLevel(level)

    log_cfg = CONFIG.getpath("logging", "config", fallback=None)

    if log_cfg is not None:
        if not log_cfg.EXISTS:
            raise args.Error( 42, (
                'log config file does not exists:'
                ' %s check your [logging]:config= setting at: %s'
            ) % (log_cfg, args.config))
        if verbose:
            args.ERR.write("load logging configuration from: %s\n" % log_cfg)
        env = CONFIG.config_env(app='cli', workspace=app_ws)
        init_log(log_cfg, defaults = env)

    if verbose:
        args.ERR.write(
            "log goes to:\n - "
            + "\n - ".join([str(h) for h in logger.handlers])
            + "\n")


# ==============================================================================
# call main ...
# ==============================================================================

if __name__ == '__main__':
    sys.exit(main())

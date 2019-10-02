# -*- coding: utf-8; mode: python; mode: flycheck -*-
# pylint: disable=global-statement, too-few-public-methods

"""Command line tools from the fontlib library.

Most commands do work with a workspace.  If you haven't used fontlib before it
might be good to create one first::

  fontlib workspace init <dest-folder> [-h]

Which creates a workspace at <dest-folder> and init this workspace with some
defaults registered.  Use the help option for more details.

"""

import re
import sys
import configparser
import logging.config
import platform

from urllib.parse import urlparse

from fspath import CLI
from fspath import FSPath
from fspath.sui import SimpleUserInterface
from fspath.progressbar import humanizeBytes
from fspath.progressbar import progressbar

from . import __pkginfo__
from . import db
from . import event

from .api import FontStack
from .api import BUILTINS # pylint: disable=unused-import
from .api import URLBlob

from .db import fontlib_session
from .config import init_cfg
from .config import get_cfg
from .config import DEFAULT_INI
from .log import DEFAULT_LOG_INI
from .log import FONTLIB_LOGGER
from .log import init_log

_development = True

try:
    from sqlalchemy import MetaData
    from sqlalchemy_schemadisplay import create_schema_graph
except ImportError as exc:
    _development = False


log = logging.getLogger('fontlib.cli')

UNKNOWN = object()
CONFIG_INI = 'config.ini'
LOG_INI = 'log.ini'
CTX = None

class Context:
    """Application's context"""

    def __init__(self, cli):
        init_cfg()
        self.CLI = cli

    @property
    def CONFIG(self):
        """Global configuration of the command line application.

        Managed in the *main loop* by :py:func:`init_main` and
        :py:func:`init_app`.

        """
        return get_cfg()

    @property
    def WORKSPACE(self):
        """Workspace of the command line application.

        Managed in the *main loop* by :py:func:`init_app`.

        """
        return self.CONFIG.getpath(
            'DEFAULT', 'workspace'
            , fallback = FSPath('~/.fontlib').EXPANDUSER )

def main():
    """main loop of the command line interface"""
    global CTX

    cli = CLI(description=__doc__)
    cli.UI = SimpleUserInterface(cli=cli)

    init_main(cli)

    # config ...

    cli.add_argument(
        '-c', '--config'
        , help = 'specify config file'
        , dest = 'config'
        , type = FSPath
        , default = CTX.WORKSPACE / CONFIG_INI
        , nargs = '?'
        , metavar = 'INI-FILE' )

    cli.add_argument(
        "--workspace"
        , dest = 'workspace'
        , default = CTX.CONFIG.get(*MAP_ARG_TO_CFG['workspace'][:2])
        , type = FSPath
        , help = "workspace"
        )

    cli.add_argument(
        '--debug-sql'
        , action  = 'store_true'
        , help    = 'debug sql engine' )

    # cmd: README ...

    _ = cli.addCMDParser(cli_README, cmdName='README')

    # cmd: SCHEMA ...

    if _development:
        schema = cli.addCMDParser(cli_SCHEMA, cmdName='SCHEMA')
        schema.add_argument(
            '--force'
            , action  = 'store_true'
            , help = 'force command'
        )
        schema.add_argument(
            "out"
            , type = FSPath
            , nargs = '?'
            , default = FSPath('./schema_diagram.svg')
            , help = "output file name of the generated diagram"
        )

    # cmd: version ...

    _ = cli.addCMDParser(cli_version, cmdName='version')

    # cmd: list ...

    _ = cli.addCMDParser(cli_list_fonts, cmdName='list')

    # cmd: css-parse

    css_parse = cli.addCMDParser(cli_parse_css, cmdName='css-parse')
    css_parse.add_argument(
        "url"
        , type = str
        , help = "URL of stylesheet (CSS) to parse"
    )

    # cmd: download ...

    download_family = cli.addCMDParser(cli_download_family, cmdName='download')
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

    # cmd: workspace

    workspace = cli.addCMDParser(cli_workspace, cmdName='workspace')
    add_fontstack_options(workspace)
    workspace.add_argument(
        "subcommand"
        , type = str
        , choices=['show', 'init']
        , help = "available subcommands: %(choices)s"
    )
    workspace.add_argument(
        "argument_list"
        , type = str
        , nargs = '*'
        , help = "arguments of the subcommand"
        , metavar = 'ARG'
    )

    # run ...
    cli()

def cli_README(args):
    """prints README to stdout

    Use ``--verbose`` to print URL auf http links.

    """
    init_app(args)
    cli = args.CLI
    _ = cli.UI

    readme = __pkginfo__.docstring
    if not args.verbose:
        # strip hyperrefs
        readme = re.sub(r'`(.*?)\s\<http.*?\>`_+', r"'\1'", readme, flags=re.S)
    _.echo(readme)

def cli_SCHEMA(args):
    # pylint: disable=line-too-long
    """Turn SQLAlchemy DB Model into a graph.

    !!! EXPERIMENTAL !!!

    .. hint::

         This feature is available in the *develop* environment.  To install
         requirements of the *develop* environment use::

            pip install .\\[develop,test\\]

    - `Declaring Extras <https://setuptools.readthedocs.io/en/latest/setuptools.html#declaring-extras-optional-features-with-their-own-dependencies>`_
    - `Install a package with setuptools extras. <https://pip.pypa.io/en/stable/reference/pip_install/#examples>`_


    You will need atleast SQLAlchemy and pydot along with graphviz for
    this.  Graphviz-cairo is higly recommended to get tolerable image quality.
    Further reading:

    - `sqlalchemy_schemadisplay <https://github.com/fschulze/sqlalchemy_schemadisplay>`__

    """
    init_app(args)
    cli = args.CLI
    _ = cli.UI

    fontlib_connector = CTX.CONFIG.get('DEFAULT', 'fontlib_db', fallback='sqlite:///:memory:')

    if args.out.EXISTS and not args.force:
        raise args.Error(42, "file %s already exists (use --force to overwrite)" % args.out)

    fmt = 'svg'
    if args.out.SUFFIX:
        fmt = args.out.SUFFIX[1:]

    # create the pydot graph object by autoloading all tables via a bound metadata object
    graph = create_schema_graph(
        metadata = MetaData(fontlib_connector)
        , show_datatypes = True  # The image would get big if we'd show the datatypes
        , show_indexes = True  # ditto for indexes
        , rankdir = 'LR'  # From left to right (instead of top to bottom)
        , concentrate = False  # Don't try to join the relation lines together
    )
    if fmt in graph.formats:
        _.echo("write format %s to file: %s" % (fmt, args.out))
        graph.write(args.out, format=fmt, encoding='utf-8') # write out the file
    else:
        raise args.Error(42, "unknown output format: %s" % fmt)

def cli_version(args):
    """prints version infos to stdout"""
    init_app(args)
    cli = args.CLI
    _ = cli.UI

    _.echo(" | ".join([
        __pkginfo__.version
        , platform.python_version()
        , platform.node()
        , platform.platform()
        ]))

def cli_list_fonts(args):
    """list fonts

    """
    init_app(args)
    cli = args.CLI
    _ = cli.UI

    stack = FontStack.get_fontstack(CTX.CONFIG)

    def table_rows():

        for font in stack.list_fonts():

            blob = stack.cache.get_blob_obj(font.origin)

            if blob is None:
                state = URLBlob.STATE_REMOTE
                url = urlparse(blob.origin)
                if url.scheme == 'file':
                    state = URLBlob.STATE_LOCAL
                blob = URLBlob(font.origin, state=state)

            closest = blob.origin
            if blob.state == blob.STATE_CACHED:
                closest = stack.cache.fname_by_blob(blob)

            yield dict(
                id = font.id
                , origin = font.origin
                , name = font.name
                , format = font.format
                , blob_state = blob.state
                , closest = closest
                )

    with db.fontlib_scope():

        _.rst_table(
            table_rows()
            # <col-title>,      <format sting>, <attribute name>
            , ("cache sate",    "%-10s",        "blob_state")
            , ("name",          "%-40s",        "name")
            , ("format",        "%-20s",        "format")
            , ("font ID",       "%-22s",        "id")
            , ("location",      "%-90s",        "closest") )


def cli_parse_css(args):
    """Parse ``@font-face`` rules from <url>.

    Load CSS (stylesheet) from <url> and filter ``@font-face`` rules.  E.g. google
    fonts API::

      css-parse 'https://fonts.googleapis.com/css?family=Cute+Font|Roboto+Slab'

    or built-in *dejavu* fonts from url::

      css-parse  'file:%(BUILTINS)s/cantarell/cantarell.css'
      css-parse  'file:%(BUILTINS)s/dejavu/dejavu.css'

    """
    cli = args.CLI
    _ = cli.UI

    # init application with an empty fontstack database
    CTX.CONFIG.set('DEFAULT', 'fontlib_db', value='sqlite:///:memory:')
    init_app(args)

    def table_rows():

        for font in stack.list_fonts():
            yield dict(
                id = font.id
                , origin = font.origin
                , name = font.name
                , format = font.format
                )

    with db.fontlib_scope():

        stack = FontStack.get_fontstack(CTX.CONFIG)
        _.echo("load css from url: %s" % args.url)
        stack.load_css(args.url)

        _.rst_table(
            table_rows()
            # <col-title>, <format sting>, <attribute name>
            , ("name",          "%-40s",        "name")
            , ("format",        "%-20s",        "format")
            , ("font ID",       "%-22s",        "id")
            , ("URL",           "%-90s",        "origin") )


def download_progress(url, font_name, font_format, cache_file, down_bytes, max_bytes):

    progress_max = max_bytes

    if max_bytes == 0:
        # max_bytes can be zero if content-lenght is not set in the header
        progress_max = down_bytes * 2

    if max_bytes == -1:
        progress_max = down_bytes

    progressbar(
        down_bytes, progress_max
        , prompt = "%s (%s) [%s]" % (font_name, font_format, humanizeBytes(progress_max, 1))
        , pipe = CTX.CLI.OUT
    )

    if max_bytes == -1:
        CTX.CLI.OUT.write('\n')


def cli_download_family(args):
    """Download font-family <family> into folder <dest>."""

    init_app(args)
    cli = args.CLI
    _ = cli.UI

    stack = FontStack.get_fontstack(CTX.CONFIG)

    event.add('urlcache.download.tick', download_progress)

    if args.dest.EXISTS:
        log.info("use existing folder %s", args.dest)
    else:
        log.info("createfolder %s", args.dest)
        args.dest.makedirs()

    count = 0

    with db.fontlib_scope():

        for font_family in args.family:
            c = 0

            for font in stack.list_fonts(font_family):
                url = urlparse(font.origin)
                dest_file = args.dest / FSPath(url.path).BASENAME
                if url.query:
                    # the resource is not a typical file URL with a file name, lets use
                    # the fonts resource ID as a file name
                    dest_file = args.dest / str(font.id) + '.' + font.format
                _.echo("[%s]: download from %s" % (font.name, font.origin))
                stack.save_font(font, dest_file)
                c += 1
            if c == 0:
                _.echo("unknow font-family: %s" % font_family)
            count += c

    msg = "non of selected fonts is registered in the FontStack"
    if count == 0:
        log.error(msg)
    else:
        msg = "downloaded %s files into %s" % (count, args.dest)

    _.echo(msg)
    return not count

def cli_config(args):
    """Inspect configuration (working with INI files).

    commands:

      :show:
         print configuration

      :install:
         install default configuration (optional ARG1: <dest-folder>)

    """

    init_app(args, verbose=True)
    cli = args.CLI
    _ = cli.UI

    if args.subcommand == 'install':

        folder = CTX.WORKSPACE
        if args.argument_list:
            folder = FSPath(args.argument_list[0])
        folder.makedirs()

        dest = folder / 'config.ini'
        _.echo("install:  %s" % dest)
        if dest.EXISTS and not args.force:
            raise args.Error(42, "file %s already exists (use --force to overwrite)" % dest)
        DEFAULT_INI.copyfile(dest)

        dest = folder / 'log.ini'
        _.echo("install:  %s" % dest)
        if dest.EXISTS and not args.force:
            raise args.Error(42, "file %s already exists (use --force to overwrite)" % dest)
        DEFAULT_LOG_INI.copyfile(dest)

        return

    if args.subcommand == 'show':

        _.rst_title("config.ini")
        CTX.CONFIG.write(cli.OUT)

        _.rst_title("log.ini")
        log_cfg = configparser.ConfigParser()
        log_cfg.read(CTX.CONFIG.get("logging", "config", fallback=DEFAULT_LOG_INI))
        log_cfg.write(cli.OUT)

        return

class print_font:  # pylint: disable=invalid-name
    """function object to print font to stdout"""
    def __call__(self, font):
        print(
            'add %s // %s // unicode range: %s' %
            (','.join([y.src_format for y in font.src_formats])
             , font.name, font.unicode_range or '--')
            , file = CTX.CLI.OUT)

class print_msg(str):  # pylint: disable=invalid-name
    """function object to print even-message to stdout"""
    def __call__(self, *args, **kwargs):
        msg = self % args
        print(msg, file = CTX.CLI.OUT)


def cli_workspace(args):
    """Inspect and init workspace.

    commands:
        :show:
           show current workspace location
        :init:
           init workspace (optional ARG1: <dest-folder>) from init-options:
           "--builtins", "--google", ""--ep-fonts"

    To register fonts from google fonts infrastructure.  Select font families
    from: https://fonts.google.com

    To install fonts (*entry points*) from the *python fonts project*
    (https://pypi.org/project/fonts) you can use e.g.::

        $ pip install --user \\
              font-amatic-sc font-caladea font-font-awesome \\
              font-fredoka-one font-hanken-grotesk font-intuitive \\
              font-source-sans-pro font-source-serif-pro

    """

    init_app(args)
    cli = args.CLI
    _ = cli.UI

    event.add('FontStack.load_entry_point'
              , print_msg('load entry point %s'))

    event.add('FontStack.load_css'
              , print_msg('load CSS %s'))

    event.add('FontStack.add_font'
              , print_font())

    event.add('FontStack.add_alias'
              , print_msg('add alias %s to font %s'))

    workspace = CTX.WORKSPACE

    if args.subcommand == 'init':

        if args.argument_list:
            workspace = FSPath(args.argument_list[0])

        _.echo("initing workspace at: %s" % workspace)
        workspace.makedirs()

        with db.fontlib_scope():
            FontStack.init_fontstack(CTX.CONFIG)

        return

    if args.subcommand == 'show':
        _.echo("%s" % workspace)
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
        , default = CTX.CONFIG.get(*MAP_ARG_TO_CFG['builtins'][:2])
        , nargs = '?', type = str
        , help = "register builtin fonts"
        )

    cmd.add_argument(
        "--ep-fonts"
        , dest = 'epfonts'
        , default = CTX.CONFIG.get(*MAP_ARG_TO_CFG['epfonts'][:2])
        , nargs = '?', type = str
        , help = "use fonts from entry points"
        )

    cmd.add_argument(
        "--google"
        , dest = 'google'
        , default = CTX.CONFIG.get(*MAP_ARG_TO_CFG['google'][:2])
        , nargs = '?', type = str
        , help = "register fonts from fonts.googleapis.com"
        )

def init_main(cli):
    """Init routine for the very first the main function."""

    global CTX

    cli_parse_css.__doc__ =  cli_parse_css.__doc__ % globals()

    # init main's context
    CTX = Context(cli)
    log.debug("initial using workspace at: %s", CTX.WORKSPACE)
    CTX.WORKSPACE.makedirs()

    # init event system

    event.init_dispatcher()

    # init main logging with (new) CONFIG settings

    log_cfg = CTX.CONFIG.get("logging", "config", fallback=DEFAULT_LOG_INI)
    env = CTX.CONFIG.config_env(app='cli', workspace=CTX.WORKSPACE)
    init_log(log_cfg, defaults = env)

def init_app(args, verbose=False): # pylint: disable=too-many-statements
    """Init the application.

    - init :py:obj:`Context.CONFIG` from arguments & INI file
    - init :py:obj:`Context.WORKSPACE`
    - init :py:obj:`.log.FONTLIB_LOGGER`
    - init DB engine configured in INI ``[DEFAULT]:fontlib_db``

    """
    # pylint: disable=too-many-branches

    global CTX

    verbose = verbose or args.verbose
    _ = args.CLI.UI

    # init application's CONFIG from INI file

    cfg = []

    if args.config != CTX.WORKSPACE / CONFIG_INI:
        # assert config if --config was explicite set
        if not args.config.EXISTS:
            raise args.Error(42, 'config file does not exists: %s' % args.config)
        cfg.append(args.config)

    elif args.workspace:
        # assert %(workspace)s/config.ini if --workspace was explicite set but
        # not --config
        if not args.workspace.EXISTS:
            raise args.Error(42, 'workspace folder does not exists: %s' % args.workspace)

        ini_file = args.workspace / 'config.ini'
        if ini_file.EXISTS:
            cfg.append(ini_file)
        else:
            log.info("Config file %s does not exists.", ini_file)

    if cfg:
        msg = "load additional configuration from: %s" % cfg
        log.info(msg)
        if verbose:
            _.echo(msg)

    CTX.CONFIG.read(cfg)
    map_arg_to_cfg(args, CTX.CONFIG)

    # init application's WORKSPACE from (new) CONFIG settings

    if not CTX.WORKSPACE.EXISTS:
        log.debug("initing workspace at: %s", CTX.WORKSPACE)
        CTX.WORKSPACE.makedirs()

    msg = "using workspace: %s\n" % CTX.WORKSPACE
    log.debug(msg)
    if verbose:
        _.echo(msg)

    # init app logging with (new) CONFIG settings

    logger = logging.getLogger(FONTLIB_LOGGER)

    if args.debug:
        CTX.CONFIG.set("logging", "level", 'debug')
    if args.debug_sql:
        logging.getLogger('sqlalchemy.engine').setLevel('INFO')

    level = CTX.CONFIG.get("logging", "level").upper()
    if verbose:
        args.ERR.write("set log level of logger: %s (%s)\n" % (logger.name, level))

    logger.setLevel(level)

    log_cfg = CTX.CONFIG.getpath("logging", "config", fallback=None)

    if log_cfg is not None:
        if not log_cfg.EXISTS:
            raise args.Error( 42, (
                'log config file does not exists:'
                ' %s check your [logging]:config= setting at: %s'
            ) % (log_cfg, args.config))
        if verbose:
            args.ERR.write("load logging configuration from: %s\n" % log_cfg)
        env = CTX.CONFIG.config_env(app='cli', workspace=CTX.WORKSPACE)
        init_log(log_cfg, defaults = env)

    if verbose:
        args.ERR.write(
            "log goes to:\n - "
            + "\n - ".join([str(h) for h in logger.handlers])
            + "\n")

    # init database
    db.fontlib_init(CTX.CONFIG)

# ==============================================================================
# call main ...
# ==============================================================================

if __name__ == '__main__':
    sys.exit(main())

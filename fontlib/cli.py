# SPDX-License-Identifier: AGPL-3.0-or-later
"""The fontlib_ library comes with a command line.  Use ``fontlib --help`` for a
basic help.  Most commands do work with a workspace.  If you haven't used
fontlib before it might be good to create one first::

  fontlib workspace init

Which creates a workspace and init this workspace with some defaults registered.

.. _fontlib_cli_options:

common options:

- ``-c / --config``: :origin:`fontlib/config.ini` (see :ref:`config`)
- ``-w / --workspace``: place where application persists its data

fontstack options:

- ``--builtins``: select :ref:`builtin_fonts`
- ``--ep-fonts``: :ref:`ep_points`
- ``--google``: :ref:`googlefont`

For a more detailed help to one of the sub commands type::

  $ fontlib <command> --help

"""

import re
import sys
import configparser
import logging.config
import platform
import urllib.parse

from fspath import CLI
from fspath import FSPath
from fspath.sui import SimpleUserInterface
from fspath.progressbar import humanizeBytes
from fspath.progressbar import progressbar

from . import __pkginfo__
from . import db
from . import event
from . import googlefont

from .api import FontStack
from .api import BUILTINS # pylint: disable=unused-import
from .api import URLBlob

from .config import init_cfg
from .config import get_cfg
from .config import DEFAULT_INI
from .log import DEFAULT_LOG_INI
from .log import FONTLIB_LOGGER
from .log import init_log

_development = True  # pylint: disable=invalid-name

try:
    from sqlalchemy import MetaData
    from sqlalchemy_schemadisplay import create_schema_graph
except ImportError as exc:
    _development = False  # pylint: disable=invalid-name


log = logging.getLogger('fontlib.cli')

UNKNOWN = object()
CONFIG_INI = 'config.ini'
LOG_INI = 'log.ini'
CTX = None

class Context:
    """Application's context"""
    # pylint: disable=invalid-name

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

    cli = CLI(description=__doc__)
    cli.UI = SimpleUserInterface(cli=cli)

    init_main(cli)

    cli.add_argument(
        '-c', '--config'
        , help = 'specify config file'
        , dest = 'config'
        , type = FSPath
        , default = CTX.WORKSPACE / CONFIG_INI
        , nargs = '?'
        , metavar = 'INI-FILE' )

    cli.add_argument(
        '-w', '--workspace'
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

    _ = cli.addCMDParser(cli_readme, cmdName='README')

    # cmd: SCHEMA ...

    if _development:
        schema = cli.addCMDParser(cli_schema, cmdName='SCHEMA')
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
        '--register'
        , action  = 'store_true'
        , help = 'register parsed fonts'
    )
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
        , choices = ['show', 'install']
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
        , choices = ['show', 'init']
        , help = "available subcommands: %(choices)s"
    )
    workspace.add_argument(
        "argument_list"
        , type = str
        , nargs = '*'
        , help = "arguments of the subcommand"
        , metavar = 'ARG'
    )

    # cmd: google

    google = cli.addCMDParser(cli_google, cmdName='google')
    google.add_argument(
        "--format"
        , dest = 'out_format'
        , default = 'raw'
        , choices = ['rst', 'raw']
        , type = str
        , help = ("output format:"
                  " rst: reStructuredText,"
                  " raw: unformated" )
        )
    google.add_argument(
        "subcommand"
        , type = str
        , choices = ['list', 'add']
        , help = "available subcommands: %(choices)s"
    )
    google.add_argument(
        "argument_list"
        , type = str
        , nargs = '*'
        , help = "arguments of the subcommand"
        , metavar = 'ARG'
    )

    # run ...
    cli()

def cli_readme(args):
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

def cli_schema(args):
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
        raise args.Error(42, f"file {args.out} already exists (use --force to overwrite)")

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
        _.echo(f"write format {fmt} to file: {args.out}")
        graph.write(args.out, format=fmt, encoding='utf-8') # write out the file
    else:
        raise args.Error(42, f"unknown output format:{fmt}")

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
    """list fonts registered in the workspace

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
                url = urllib.parse.urlparse(blob.origin)
                if url.scheme == 'file':
                    state = URLBlob.STATE_LOCAL
                blob = URLBlob(font.origin, state=state)

            closest = blob.origin
            if blob.state == blob.STATE_CACHED:
                closest = stack.cache.fname_by_blob(blob)

            yield {
                'id':            font.id
                , 'origin':      font.origin
                , 'name':        font.name
                , 'format':      font.format
                , 'blob_state':  blob.state
                , 'closest':     closest
            }

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

    if not args.register:
        # init application with an empty fontstack database
        CTX.CONFIG.set('DEFAULT', 'fontlib_db', value='sqlite:///:memory:')
    init_app(args)

    def table_rows():

        for font in stack.list_fonts():
            yield {
                'id':          font.id
                , 'origin':    font.origin
                , 'name':      font.name
                , 'format':    font.format
            }

    with db.fontlib_scope():

        stack = FontStack.get_fontstack(CTX.CONFIG)
        _.echo(f"load css from url: {args.url}")
        stack.load_css(args.url)

        _.rst_table(
            table_rows()
            # <col-title>, <format sting>, <attribute name>
            , ("name",          "%-40s",        "name")
            , ("format",        "%-20s",        "format")
            , ("font ID",       "%-22s",        "id")
            , ("URL",           "%-90s",        "origin") )

    if args.register:
        _.echo(f'fonts registered in workspace: {CTX.WORKSPACE}')

def download_progress(_url, font_name, font_format, _cache_file, down_bytes, max_bytes):
    """Callback that prints download progress bar.

    """
    progress_max = max_bytes
    if max_bytes == 0:
        # max_bytes can be zero if content-lenght is not set in the header
        progress_max = down_bytes * 2
    if max_bytes == -1:
        progress_max = down_bytes

    progressbar(
        down_bytes, progress_max
        , prompt = f"{font_name} ({font_format}) [{humanizeBytes(progress_max, 1)}]"
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
                url = urllib.parse.urlparse(font.origin)
                dest_file = args.dest / FSPath(url.path).BASENAME
                if url.query:
                    # the resource is not a typical file URL with a file name, lets use
                    # the fonts resource ID as a file name
                    dest_file = args.dest / str(font.id) + '.' + font.format
                _.echo(f"[{font.name}]: download from {font.origin}")
                stack.save_font(font, dest_file)
                c += 1
            if c == 0:
                _.echo(f"unknow font-family: {font_family}")
            count += c

    msg = "non of selected fonts is registered in the FontStack"
    if count == 0:
        log.error(msg)
    else:
        msg = f"downloaded {count} files into {args.dest}"

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
        _.echo(f"install:  {dest}")
        if dest.EXISTS and not args.force:
            raise args.Error(42, f"file {dest} already exists (use --force to overwrite)")
        DEFAULT_INI.copyfile(dest)

        dest = folder / 'log.ini'
        _.echo(f"install:  {dest}")
        if dest.EXISTS and not args.force:
            raise args.Error(42, f"file {dest} already exists (use --force to overwrite)")
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

class print_font:  # pylint: disable=invalid-name, too-few-public-methods
    """function object to print font to stdout"""
    def __call__(self, font):
        print(
            # pylint: disable=consider-using-f-string
            'add %s // %s // unicode range: %s' % (
                ','.join([y.src_format for y in font.src_formats]),
                font.name,
                font.unicode_range or '--'
            ),
            file = CTX.CLI.OUT,
        )

class print_msg(str):  # pylint: disable=invalid-name, too-few-public-methods
    """function object to print even-message to stdout"""
    def __call__(self, *args, **kwargs):
        msg = self % args
        print(msg, file = CTX.CLI.OUT)


def cli_workspace(args):
    """Inspect and init workspace.

    commands:

    - show: show current workspace location

    - init: init workspace from init-options: --builtins, --google, --ep-fonts::

          workspace init ~/.fontlib

      Second argument is the destination of the workspace (default: ~/.fontlib).

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

        # get worsspace's path

        if args.argument_list:
            workspace = FSPath(args.argument_list.pop(0))

        # finally check command line

        if args.argument_list:
            _.echo(f"WARNING: ignoring arguments: {','.join(args.argument_list)}")

        # init workspace

        _.echo(f"initing workspace at: {workspace}")
        workspace.makedirs()

        with db.fontlib_scope():
            FontStack.init_fontstack(CTX.CONFIG)

        return

    if args.subcommand == 'show':

        # finally check command line

        if args.argument_list:
            _.echo(f"WARNING: ignoring arguments: {','.join(args.argument_list)}")

        cfg_file = args.config if args.config.EXISTS else DEFAULT_INI
        _.echo(f"WORKSPACE: {workspace}")
        _.echo(f"CONFIG:    {cfg_file}")
        return

def cli_google(args):
    """tools for Google fonts

    commands:

    - list: print out list of known font names from fonts.googleapis.com::

        google --format=rst list 'Libre.*39'

    - add: font to FontStack::

        google --format=rst add 'Libre.*39'

      The second argument is a optional regular expression to filter font names
      by matching this expression (default: *None*).
    """
    # pylint: disable=too-many-branches
    init_app(args)
    _ = args.CLI.UI

    if args.subcommand in ('list', 'add'):

        # get match condition ...
        condition = None
        if args.argument_list:
            condition = args.argument_list.pop(0)
        if condition:
            condition = re.compile(condition)

        # finally check command line
        if args.argument_list:
            _.echo(f'WARNING: ignoring arguments: {",".join(args.argument_list)}')

    if args.subcommand == 'list':

        # output list ..
        if args.out_format == 'rst':
            _.rst_title("google font names")

        i = 0
        for name, item in googlefont.font_map(CTX.CONFIG).items():
            if condition is not None:
                if not condition.search(name):
                    continue
            i += 1
            msg = name
            if args.out_format == 'rst':
                msg = f"{i:4d}. {name} --> {item['css_url']}"
            _.echo(msg)

        if args.out_format == 'rst':
            _.echo('')

    if args.subcommand == 'add':

        event.add('FontStack.add_font', print_font())
        event.add('FontStack.add_alias', print_msg('add alias %s to font %s'))
        i = 0

        with db.fontlib_scope():
            stack = FontStack.get_fontstack(CTX.CONFIG)

            for name, item in googlefont.font_map(CTX.CONFIG).items():
                if condition is not None:
                    if not condition.search(name):
                        continue
                i += 1

                _.echo(f"{i:4d}. read font-family '{name}' from CSS: {item['css_url']}")
                stack.load_css(item['css_url'])

# ==============================================================================
# helper ...
# ==============================================================================

MAP_ARG_TO_CFG = {
    # cli-argument    : (cfg-section, cfg-option) # see ./config.ini
    'builtins'        : ('fontstack', 'builtin fonts')
    , 'epfonts'       : ('fontstack', 'entry points')
    , 'google'        : ('google fonts', 'fonts')
    , 'workspace'     : ('DEFAULT', 'workspace')
}
"""Maps command line arguments to config section & option"""

def map_arg_to_cfg(args, cfg):
    """update application's CONFIG from command line arguments.."""
    for arg_name, (cfg_sect, cfg_opt) in MAP_ARG_TO_CFG.items():
        value = args.__dict__.get(arg_name)
        if value is None:
            continue
        log.debug("set %s/%s = %s", cfg_sect, cfg_opt, value)
        cfg.set(cfg_sect, cfg_opt, str(value))

def add_fontstack_options(cmd):
    """Adds common fontstack options to command"""

    cmd.add_argument(
        "--builtins"
        , dest = 'builtins'
        , nargs = '?', type = str
        , help = f"register builtin fonts / e.g. '{CTX.CONFIG.get(*MAP_ARG_TO_CFG['builtins'][:2])}'"
        )

    cmd.add_argument(
        "--ep-fonts"
        , dest = 'epfonts'
        , nargs = '?', type = str
        , help = f"use fonts from entry points / e.g. '{CTX.CONFIG.get(*MAP_ARG_TO_CFG['epfonts'][:2])}'"
        )

    cmd.add_argument(
        "--google"
        , dest = 'google'
        , nargs = '?', type = str
        , help = f"register fonts from fonts.googleapis.com / e.g. '{CTX.CONFIG.get(*MAP_ARG_TO_CFG['google'][:2])}'"
        )

def init_main(cli):
    """Init routine for the very first the main function."""

    global CTX  # pylint: disable=global-statement

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

    verbose = verbose or args.verbose
    _ = args.CLI.UI

    # set some base logging while app's runtime is build up
    logger = logging.getLogger(FONTLIB_LOGGER)
    if args.debug:
        args.ERR.write(f"set log level of logger: {logger.name} (DEBUG)\n")
        logger.setLevel('DEBUG')
        logging.getLogger('sqlalchemy.engine').setLevel('INFO')

    # init application's CONFIG from INI file

    cfg = None

    if args.workspace:
        # assert %(workspace)s/config.ini if --workspace was explicite set
        if not args.workspace.EXISTS:
            raise args.Error(42, f'workspace folder does not exists: {args.workspace}')

        ini_file = args.workspace / 'config.ini'
        if ini_file.EXISTS:
            cfg = ini_file
        else:
            log.info("Config file %s does not exists.", ini_file)

    elif args.config.EXIST:
        cfg = args.config
    else:
        raise args.Error(42, f'config file does not exists: {args.workspace}')

    if cfg:
        _.echo(f"init configuration from: {cfg}")
        init_cfg(cfg)

    map_arg_to_cfg(args, CTX.CONFIG)

    # init application's WORKSPACE from (new) CONFIG settings

    if not CTX.WORKSPACE.EXISTS:
        _.echo("initing workspace at: %s", CTX.WORKSPACE)
        CTX.WORKSPACE.makedirs()

    msg = f"using workspace: {CTX.WORKSPACE}\n"
    log.debug(msg)
    if verbose:
        _.echo(msg)

    # init app logging with (new) CONFIG settings

    if args.debug:
        CTX.CONFIG.set("logging", "level", 'debug')
    if args.debug_sql:
        logging.getLogger('sqlalchemy.engine').setLevel('INFO')

    level = CTX.CONFIG.get("logging", "level").upper()
    logger.setLevel(level)

    log_cfg = CTX.CONFIG.getpath("logging", "config", fallback=None)

    if log_cfg is not None:
        if not log_cfg.EXISTS:
            raise args.Error(
                42, ( f'log config file does not exists:'
                      f' {log_cfg} check your [logging]:config= setting at: {args.config}'
                     ))
        if verbose:
            args.ERR.write(f"load logging configuration from: {log_cfg}\n")
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

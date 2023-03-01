# SPDX-License-Identifier: AGPL-3.0-or-later
"""

FIXME: needs a revision

The fontlib_ library comes with a command line.  Use ``fontlib --help`` for a
basic help.  Most commands do work with a workspace.  If you haven't used
fontlib before it might be good to create one first::

  fontlib workspace init

Which creates a workspace and init this workspace with some defaults registered.

.. _fontlib_cli_options:

common options:

- ``-c / --config``: :origin:`fontlib/fontlib.toml` (see :ref:`config`)
- ``-w / --workspace``: place where application persists its data

fontstack options:

- ``--builtins``: select :ref:`builtin_fonts`
- ``--ep-fonts``: :ref:`ep_points`
- ``--google``: :ref:`googlefont`

For a more detailed help to one of the sub commands type::

  $ fontlib <command> --help
"""

import sys
import re
import platform
import logging
import click
import fspath

from fontlib import app
from fontlib import event
from fontlib import __pkginfo__

log = logging.getLogger(__name__)

@click.group()
@click.option(
    '--debug/--no-debug',
    envvar = 'FONTLIB_DEBUG',
    default = False,
    help = "enable debug messages",
    show_default = True,
)
@click.option(
    '--config',
    envvar = 'FONTLIB_CONFIG',
    type = fspath.FSPath,
    default = None,
    help = "TOML configuration file",
    show_default = True,
)
@click.option(
    '--workspace',
    envvar = 'FONTLIB_WORKSPACE',
    default = '~/.fontlib',
    type = fspath.FSPath,
    help = "Location of Fontlib's workspace",
    show_default = True,
)
@click.pass_context
def cli(ctx, debug, config, workspace):
    """Fontlib's command line interface."""

    if config and not config.EXISTS:
        raise click.ClickException(f"config file does not exists: {config}")

    if workspace and workspace.EXISTS:
        ws_cfg = workspace / "fontlib.toml"
        if not config and ws_cfg.EXISTS:
            click.echo(f'using config from workspace: {ws_cfg}')
            # sys.stderr.write(f'using config from workspace: {ws_cfg}\n')
            config = ws_cfg

    # init event system
    event.init_dispatcher()

    # build application's context
    ctx.obj = app.Application(
        config_file = config,
        workspace_folder = workspace,
        debug = debug,
    )
    ctx.obj.init()

    if config and config.ABSPATH != ctx.obj.config_file:
        click.secho(
            f"ignoring config argument ({config}), using config file at: {ctx.obj.config_file}",
            fg = 'red',
            err = True,
        )

    if workspace and workspace.ABSPATH != ctx.obj.workspace_folder:
        click.secho(
            f"WARN: ignoring workspace argument, using workspace at: {ctx.obj.workspace_folder}",
            fg = 'red',
            err = True,
        )

# version

@cli.command()
def version():
    """Prompt version info."""
    click.echo(
        f"fontlib: {__pkginfo__.version}"
        f" | pyton: {platform.python_version()}"
        f" | node: {platform.node()}"
        f" | platform: {platform.platform()}"
    )

# project

@cli.group
def project():
    """Maintenance tools for the development of the fontlib project."""

@project.command
@click.option(
    '--hide-url/--show-url',
    default = False,
    type = bool,
    help = "strip URLs from README",
    show_default = True,

)
def readme(hide_url):
    """Generate content of the ./README.rst file."""
    txt = __pkginfo__.README
    if hide_url:
        # strip hyperrefs
        txt = re.sub(r'`(.*?)\s\<http.*?\>`_+', r"'\1'", txt, flags=re.S)
    click.echo_via_pager(txt)

@project.command
def requirements():
    """Generate content of the ./requirements.txt file."""
    click.echo_via_pager(__pkginfo__.requirements_txt)

@project.command
@click.pass_obj
def requirements_dev(_ctx):
    """Generate content of the ./requirements_dev.txt file."""
    click.echo_via_pager(__pkginfo__.requirements_dev_txt)

# workspace

@cli.group
def workspace():
    """Maintenance tools for Fontlib's workspace."""

    class _msg(str):  # pylint: disable=invalid-name, too-few-public-methods
        """function object to print even-message to stdout"""
        def __call__(self, *args, **kwargs):
            click.echo(self % args)

    class _font:  # pylint: disable=invalid-name, too-few-public-methods
        """function object to print font to stdout"""
        def __call__(self, font):
            click.echo(
                # pylint: disable=consider-using-f-string
                'add %s // %s // unicode range: %s' % (
                ','.join([y.src_format for y in font.src_formats]),
                    font.name,
                    font.unicode_range or '--'
                ),
            )

    event.add('FontStack.load_entry_point', _msg('load entry point %s'))
    event.add('FontStack.load_css', _msg('load CSS %s'))
    event.add('FontStack.add_font', _font())
    event.add('FontStack.add_alias', _msg('add alias %s to font %s'))

@workspace.command
@click.pass_obj
def info(fontlib_app):
    """Prompt workspace setup."""
    _info(fontlib_app)

def _info(fontlib_app):
    workspace_folder = fontlib_app.workspace_folder
    ws_exists = "" if workspace_folder.EXISTS else " (not exists)"
    click.echo(
        f"WORKSPACE config is: {fontlib_app.config_file}"
        + "\n  - name: " + fontlib_app.cfg.get('fontlib.name')
        + "\n  - location: " + workspace_folder + ws_exists
        + "\n  - fonstack cache methode: " + fontlib_app.cfg.get('fontlib.fontstack.cache')
        + "\n  - log config: " + fontlib_app.cfg.get('fontlib.logging.config')
        + "\n  - log level: " + fontlib_app.cfg.get('fontlib.logging.level')
    )

@workspace.command
@click.pass_obj
def init(fontlib_app):
    """Create and initialize WORKSPACE."""
    if not fontlib_app.workspace_folder.EXISTS:
        click.echo(f"create workspace: {fontlib_app.workspace_folder}")
        fontlib_app.workspace_folder.makedirs()
    else:
        click.secho(
            f"workspace: {fontlib_app.workspace_folder} already exists",
            fg = 'red',
            err = True,
        )

    print("ToDO ...")

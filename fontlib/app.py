# SPDX-License-Identifier: AGPL-3.0-or-later
"""Runtime environment (RTE) of the fontlib application
"""

import sys
import logging
import logging.config
import fspath
import pytomlpp as toml

from .config import Config
from .db import FontlibDB
from .fontstack import FontStack
log = logging.getLogger(__name__)

FONTLIB_TOML = fspath.FSPath(__file__).DIRNAME / "fontlib.toml"
"""Base configuration (schema) of the fontlib applicatons."""

FONTLIB_LOG_INI = fspath.FSPath(__file__).DIRNAME / "log.ini"

FONTLIB_LOGGER  = 'fontlib'
"""Name of :py:obj:`fontlib` 's (topmost) logger"""

CFG_DEPRECATED = {
    "fontlib.fontstack.foo" : (
        "The configuration 'fontlib.foo' exists only for test purposes.  Don't use"
        " it in your real project config."
    )
}

def log_cfg_env(cfg):
    """Environment of the logger configuration."""
    env = {
        'fontlib.name' :      cfg.get('fontlib.name'),
        'fontlib.workspace' : cfg.path('fontlib.workspace'),
    }
    return env


class Application:
    """Application's RTE."""

    _fontstack = None
    _db = None

    def __init__(self, config_file=None, workspace_folder=None, debug=False):

        self.cfg = None
        self.debug = debug
        self.config_file = fspath.FSPath(config_file).ABSPATH if config_file else None
        self.workspace_folder = fspath.FSPath(workspace_folder).ABSPATH if workspace_folder else None
        self._init_state = []

    def init(self):
        """Initialize the runtime environment"""

        self._db = None
        self._fontstack = None
        self.init_cfg()
        self.init_log()
        self.check_cfg()
        self.init_ws()

    def init_cfg(self):
        """Initialize the configuration."""
        # pylint: disable=too-many-branches

        if 'init_cfg' in self._init_state:
            return

        if self.config_file and not self.config_file.EXISTS:
            raise FileNotFoundError(f"Config file '{self.config_file}' does not exists!")

        # default configuration (config schema)

        self.cfg = Config(cfg_schema=toml.load(FONTLIB_TOML), deprecated=CFG_DEPRECATED)

        # customized configuration

        if self.workspace_folder and self.workspace_folder.EXISTS:
            ws_cfg = self.workspace_folder / "fontlib.toml"
            if ws_cfg.EXISTS:
                sys.stderr.write(f'using config from workspace: {ws_cfg}\n')
                self.config_file = ws_cfg

        if self.config_file:
            upd_cfg = toml.load(self.config_file)
            is_valid, issue_list = self.cfg.validate(upd_cfg)

            # while loading the configuration the loggin is not initialized yet
            # --> write messagges to stderr
            for msg in issue_list:
                sys.stderr.write(str(msg) + '\n')
            if not is_valid:
                raise TypeError(f"schema of {self.config_file} is invalid, can't update from!")
            self.cfg.update(upd_cfg)

        # force debug from application
        if self.debug:
            self.cfg.set('fontlib.logging.level', 'DEBUG')

        ws_default = fspath.FSPath(self.cfg.default('fontlib.workspace'))
        cfg_ws = self.cfg.path('fontlib.workspace')

        if self.workspace_folder:
            if cfg_ws.ABSPATH == ws_default.ABSPATH:
                # customized config did not changed the default value --> force
                # workspace from application
                self.cfg.set('fontlib.workspace', self.workspace_folder.ABSPATH)
            else:
                sys.stderr.write(f"use workspace from configuration: {cfg_ws.ABSPATH}\n")
                self.workspace_folder = cfg_ws.ABSPATH
        else:
            cfg_ws = self.cfg.path('fontlib.workspace')
            if self.config_file and not cfg_ws.ISABSPATH:
                # when the workspace path in the configuration is relative, set
                # workspacee path to absolute path based on the directory where
                # the configuration is located.
                self.cfg.set('fontlib.workspace', (self.config_file.DIRNAME / cfg_ws).ABSPATH)

        if not self.config_file:
            self.config_file = FONTLIB_TOML

        self._init_state.append('init_cfg')

    def init_log(self):
        """Initialize the logging"""

        if 'init_log' in self._init_state:
            return
        if 'init_cfg' not in self._init_state:
            raise RuntimeError("can't initalized log before config is initalized")

        msg_list = []

        level = self.cfg.get("fontlib.logging.level")
        msg_list.append(f"set applications's log level: {level}")

        config_ini = self.cfg.path("fontlib.logging.config", None)
        if config_ini is None:
            config_ini = FONTLIB_LOG_INI
        elif not config_ini.EXISTS:
            msg_list.append(f"log config does not exists at: {config_ini}")
            config_ini = FONTLIB_LOG_INI
        msg_list.append(f"init log config from: {config_ini}")

        logging.config.fileConfig(config_ini, defaults=log_cfg_env(self.cfg))
        logging.getLogger(FONTLIB_LOGGER).setLevel(level)

        # log all messages from above / after logger is initalized
        for msg in msg_list:
            log.info(msg)

        self._init_state.append('init_log')

    def init_ws(self, force_create=False):
        """Initialize workspace."""
        cfg_ws = self.cfg.path('fontlib.workspace')
        if not cfg_ws.EXISTS:
            if force_create is True:
                log.debug("create workspace: %s", cfg_ws.ABSPATH)
                cfg_ws.makedirs()
            else:
                log.warning("missing workspace: %s", cfg_ws.ABSPATH)
        self._init_state.append('init_ws')

    def check_cfg(self):
        """Check configuration for plausibility."""

        log.debug("config:    %s", self.config_file)
        log.debug("workspace: %s", self.cfg.get('fontlib.workspace'))

        # check module and cache class exists
        self.cfg.pyobj('fontlib.fontstack.cache')

        log_level = self.cfg.get('fontlib.logging.level')
        valid_levels = ["NOTSET", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if log_level not in valid_levels:
            raise ValueError(f"'{log_level}' is not a valid log level, choose one from: {valid_levels}")

    @property
    def db(self) -> FontlibDB:  # pylint: disable=invalid-name
        """Session and DB engine of the fontlib application."""
        if self._db is None:
            self._db = FontlibDB(self.cfg)
        return self._db

    @property
    def fontstack(self) -> FontStack:
        """Collection of :py:class:`fontlib.font.Font` objects."""
        if self._fontstack is None:
            self._fontstack = FontStack(self)
        return self._fontstack

# -*- coding: utf-8; mode: python -*-

u"""fontlib -- main entry point for commandline interfaces"""

import sys

from fspath import CLI
from fspath.sui import SimpleUserInterface

# ==============================================================================
def main():
# ==============================================================================

    u"""
    Tools from the fontlib library
    """
    cli    = CLI(description=main.__doc__)
    cli.UI = SimpleUserInterface(cli=cli)

    # ...

    # run ...
    cli()

if __name__ == '__main__':
    sys.exit(main())

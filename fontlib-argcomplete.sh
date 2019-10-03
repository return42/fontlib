#!/usr/bin/env bash
# -*- coding: utf-8; mode: sh -*-
# ----------------------------------------------------------------------------
# Purpose:  fontlib bash argcomplete
# ----------------------------------------------------------------------------
#
# To get in use of bash completion, install ``argcomplete``:
#
# .. code-block:: bash
#
#    pip install argcomplete
#
#  and add the following to your ``~/.bashrc``:
#
# .. code-block:: bash
#
#    source ./path/to/fontlib-argcomplete.sh
#
function _py_fontlib() {
    local IFS=$(echo -e '\v')
    COMPREPLY=( $(IFS="$IFS" \
                     COMP_LINE="$COMP_LINE" \
                     COMP_POINT="$COMP_POINT" \
                     _ARGCOMPLETE_COMP_WORDBREAKS="$COMP_WORDBREAKS" \
                     _ARGCOMPLETE=1 \
                     "$1" 8>&1 9>&2 1>/dev/null) )
    if [[ $? != 0 ]]; then
        unset COMPREPLY
    fi
}
complete -o nospace -o default -F _py_fontlib fontlib

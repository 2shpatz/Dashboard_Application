#!/bin/bash
# export PYTHONPATH="$PYTHONPATH:$LAB_DIR:$TOOLS_DIR"
script_path=$(readlink -f "${BASH_SOURCE:-$0}")
dir_path=$(dirname $script_path)
DASH_APPS_DIR=${DASHBOARD_APPS_DIR:=$dir_path"/.."}
export DASHBOARD_APPS_DIR=${DASHBOARD_APPS_DIR}
pip3 install -r $DASH_APPS_DIR/utils/requirements.txt

python3 $DASH_APPS_DIR/card_select/index.py
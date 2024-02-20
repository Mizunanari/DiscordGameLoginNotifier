#-------------------------------------------------------------------------------
# Definitions
#-------------------------------------------------------------------------------

TOOLKIT=palworld-server-toolkit
GAMEUSERSETTINGS=${PAL_DIR}/Saved/Config/LinuxServer/GameUserSettings.ini
SERVER_ID=$(sed -nre 's/^DedicatedServerName=(\w+)/\1/p' ${GAMEUSERSETTINGS} 2>/dev/null)
SAVE_DIR=${PAL_DIR}/Saved/SaveGames/0/${SERVER_ID}

#-------------------------------------------------------------------------------
# Toolkit
#-------------------------------------------------------------------------------

function fixSaveData() {
  if [ ! -d ${PAL_DIR} ]; then
    echo "${PAL_DIR} does not found."
    echo "run test.sh first."
    exit 1
  fi
  if [ ! -f ${SAVE_DIR}/Level.sav ]; then
    echo "${SAVE_DIR}/Level.sav does not found."
    exit 1
  fi
  cd ${SAVE_DIR}
  python3 -m palworld_server_toolkit.editor --fix-missing --del-unref-item Level.sav
}

function listPlayers() {
  cd ${SAVE_DIR}/Players
  palworld-player-list --host ${LOCAL_IP} --port ${RCON_PORT:-25575} --password ${ADMIN_PASSWORD:-admin}
}

function taskset() {
  palworld-server-taskset
}

function needToolkit() {
  if [ ! $(which palworld-save-editor) ]; then
    echo "Toolkit is not installed yet."
    echo "Please run \`$(basename $0) tool-update\` first."
    exit 1
  fi
}

#-------------------------------------------------------------------------------
# Sub Commands
#-------------------------------------------------------------------------------

USAGE="${USAGE}
  ---( toolkit )---
  tool-update       ... update ${TOOLKIT}
  tool-uninstall    ... uninstall ${TOOLKIT}
  fix               ... fix Level.sav
  list              ... list players
  taskset           ... assign to P-core
"

case ${ARGV[0]} in
"tool-update")
  python3 -m pip install --upgrade ${TOOLKIT} psutil
  exit 0
  ;;
"tool-uninstall")
  needToolkit && python3 -m pip uninstall ${TOOLKIT}
  exit 0
  ;;
"fix")
  needToolkit && needStop && fixSaveData
  exit 0
  ;;
"list")
  needToolkit && needRun && listPlayers
  exit 0
  ;;
"taskset")
  needToolkit && needRun && taskset
  exit 0
  ;;
esac

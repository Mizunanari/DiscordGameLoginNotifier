#!/bin/bash

#-------------------------------------------------------------------------------
# Import or make .env
#-------------------------------------------------------------------------------
if [ ! -f .env ]; then
  cat > .env <<EOF
#TZ='Asia/Tokyo'
#PUID=1000
#PGID=1000
#PORT=8211
#RCON_PORT=25575
#ADMIN_PASSWORD='admin'
DISCORD_WEBHOOK_URL=''
EOF
  echo "Please edit the .env file according to your environment."
  exit 1
fi

source .env

#-------------------------------------------------------------------------------
# Definitions
#-------------------------------------------------------------------------------

IMAGE=ghcr.io/mizunanari/dgln
TAG=latest
CONTAINER_NAME=${CONTAINER_NAME:-pal}

SCRIPT_DIR=$(dirname $0)
SERVER_DIR=${SCRIPT_DIR}/palworld
PAL_DIR=${SERVER_DIR}/Pal
PALWORLDSETTINGS=${PAL_DIR}/Saved/Config/LinuxServer/PalWorldSettings.ini

LOCAL_IP=$(hostname -I | awk '{print $1}')

#-------------------------------------------------------------------------------
# Docker utility
#-------------------------------------------------------------------------------
function getStatus() {
  docker inspect -f '{{json .State.Status}}' ${CONTAINER_NAME} 2> /dev/null
}

function needStop() {
  STATUS=$(getStatus)
  if [ "${STATUS}" = '"running"' ]; then
    echo "${CONTAINER_NAME} container already running..."
    echo "Please docker compose down first."
    exit 1
  fi
}

function needRun() {
  STATUS=$(getStatus)
  if [ ! "${STATUS}" = '"running"' ]; then
    echo "${CONTAINER_NAME} container does not running."
    echo "Please \`$0 run\` first."
    exit 1
  fi
}

function showIni() {
  if [ ! -f ${PALWORLDSETTINGS} ]; then
    echo "${PALWORLDSETTINGS} has not been created yet."
    exit 1
  fi
  cat ${PALWORLDSETTINGS} | sed -re 's/,/,\n/g'
}

#-------------------------------------------------------------------------------
# Test
#-------------------------------------------------------------------------------

function needDiscord() {
  if [ "${DISCORD_WEBHOOK_URL}" = "" ]; then
    echo "Please set DISCORD_WEBHOOK_URL in the .env file."
    exit 1
  fi
}

function runTest() {
  echo '----------------------------------------------------------'
  echo "You can connect ${LOCAL_IP}:${PORT:-8211} from PalWorld client."
  echo 'And see Discord channel.'
  echo 'Press Ctrl+C to close test session.'
  echo '----------------------------------------------------------'
  trap 'docker compose down' 2
  docker compose up
}

#-------------------------------------------------------------------------------
# Main
#-------------------------------------------------------------------------------

USAGE="Usage: $(basename $0) <sub-commands>
sub-commands:
  build             ... build docker image
  clean             ... clean server files
  run               ... run test
  ini               ... show PalWorldSettings.ini
"

declare -a ARGV=($@)
case ${ARGV[0]} in
"build")
  docker build -t ${IMAGE}:${TAG} ..
  exit 0
  ;;
"clean")
  needStop && rm -rf ${SERVER_DIR} && echo "clean."
  exit 0
  ;;
"run")
  needDiscord && needStop && runTest
  exit 0
  ;;
"ini")
  showIni
  exit 0
  ;;
esac

PLUGINS=$(ls ${SCRIPT_DIR}/sub.d/*.inc.sh 2> /dev/null)
for SUB in ${PLUGINS}; do
  source ${SUB}
done

echo "${USAGE}"

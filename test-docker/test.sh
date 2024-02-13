#!/bin/bash

#-------------------------------------------------------------------------------
function clean () {
  echo "test clean."
  rm -rf palworld
}

function make_env () {
  cat > .env <<EOF
PORT=8211
RCON_PORT=25575
ADMIN_PASSWORD=admin
WEBHOOK=''
EOF
}

function getStatus() {
  docker inspect -f '{{json .State.Status}}' pal 2> /dev/null
}

#-------------------------------------------------------------------------------

if [ "$1" = "clean" ]; then
  clean
  exit
fi

if [ ! -f .env ]; then
  make_env
  echo "それぞれの環境に合わせて.envファイルを編集してください。"
  exit
fi
source .env

# テストする（Ctrl+Cでテスト終了）
IP=$(hostname -I | awk '{print $1}')
echo '-----------------------------------------------------'
echo "You can connect ${IP}:${PORT} from PalWorld client."
echo 'And see Discord channel.'
echo 'Press Ctrl+C to close test session.'
echo '-----------------------------------------------------'
trap 'docker compose down' 2
docker compose up


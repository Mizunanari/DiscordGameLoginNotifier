from mcrcon import MCRcon
from pprint import pprint
from datetime import datetime as dt

import requests

import os, json, csv, io, argparse, time

# ShowPlayersで不正なUIDの時に発行される
INVALID_PLAYER_UID = '00000000'

settings = {
    'discord': {
        # Discord Webhook URL
        'webhook_url': ''
    },
    'rcon' : {
        # Palworld サーバIPアドレス
        'address': '127.0.0.1',
        # RCONポート(RCONPort)
        'port': 25575,
        # RCONパスワード(AdminPasswordと同じ)
        'password': ''
    },
    'time': {
        # プレイヤ情報の取得間隔
        'fetch_player_interval_sec': 5,
        # 自動でプレイヤキックを行うか
        'use_auto_player_kick': False,
        # ロード中にプレイヤキックを行うとサーバが無限ロードされるので安全よりに設定する方がよい
        'auto_kick_player_interval_sec': 3 * 60,
        # ループ間隔 変更不要
        'loop_interval_sec': 2
    },
    'data': {
        # ファイルパス
        'log_filepath': 'player_log.json',
        # セーブデータファイル名文字数 変更不要
        'save_filename_length': 32,
        # セーブファイル拡張子 変更不要
        'save_file_extension': 'sav'
    }
}

def init_setting():
    """引数から設定を初期化
    """
    parser = argparse.ArgumentParser(description="Outputs log of Palworld Server's connectee information")
    parser.add_argument('--webhook_url', help='Discord Webhook URL', default='')
    parser.add_argument('--address', help='Server address', default='127.0.0.1')
    parser.add_argument('--port', help='RCON port', default=25575)
    parser.add_argument('--password', help='Admin password', default='')
    parser.add_argument('--log_filepath', help='Player log filepath', default='player_log.json')

    args = parser.parse_args()
    settings['discord']['webhook_url'] = args.webhook_url
    settings['rcon']['address'] = args.address
    settings['rcon']['port'] = int(args.port)
    settings['rcon']['password'] = args.password
    settings['data']['log_filepath'] = args.log_filepath

def import_players_json() -> dict:
    """ログを読み込み(過去のプレイヤ情報の復元)

    Returns:
        {
            steamid(string) : 
            {
                name: string, 
                playeruid: string,
                steamid: string,
                playeruid_hex: string,
                sav_filename: string
            }
        }: rcon showplayersから取得し整形された情報
    """
    if not os.path.isfile(settings['data']['log_filepath']):
        return {}

    with open(settings['data']['log_filepath'], 'r', encoding='utf-8') as f:
        player_log = json.load(f)
    
    return player_log

def export_players_json(player_log: dict):
    """ログを出力

    Args:
        player_log (
        {
            steamid(string) : 
            {
                name: string, 
                playeruid: string,
                steamid: string,
                playeruid_hex: string,
                sav_filename: string
            }
        }): プレイヤー情報
    """
    with open(settings['data']['log_filepath'], 'w', encoding='utf-8') as f:
        json.dump(player_log, f, ensure_ascii=False)

def fetch_players(rcon: MCRcon) -> dict:
    """接続中のユーザ情報を取得

    Args:
        rcon (MCRcon): RCON

    Returns:
        player_log (
        {
            steamid(string) : 
            {
                name: string, 
                playeruid: string,
                steamid: string,
                playeruid_hex: string,
                sav_filename: string
            }
        }): 接続中のユーザ情報
    """
    players = {}
    for _ in range(3):
        try:
            res = rcon.command('ShowPlayers')
            reader = csv.reader(io.StringIO(res))
            
            # ヘッダ情報の読み取りを飛ばす
            next(reader)

            for row in reader:
                name = row[0]
                playeruid = row[1]
                steamid = row[2]

                is_invalid_playeruid = playeruid == INVALID_PLAYER_UID
                if is_invalid_playeruid:
                    continue
                
                playeruid_hex = format(int(playeruid), 'x')
                playeruid_hex_padded = playeruid_hex.ljust(settings['data']['save_filename_length'], '0')
                sav_filename = f"{playeruid_hex_padded}.{settings['data']['save_file_extension']}"

                players[steamid] = {
                    "name": name,
                    "playeruid": playeruid,
                    "steamid": steamid,
                    "playeruid_hex": playeruid_hex,
                    'sav_filename': sav_filename
                }

        except:
            rcon.connect()

    return players

def print_login_players(login_players: dict):
    """ログイン中のプレイヤを表示

    Args:
        login_players (dict): ログイン中のプレイヤ情報
    """
    
    player_count = len(login_players)
    for player in login_players.values():
        name = player['name']
        staemid = player['steamid']
        print(f'{name}({staemid})')

def extract_new_players(all_players: dict, login_players: dict):
    """新規プレイヤを抽出

    Args:
        all_players (dict): 過去に取得済みのプレイヤ情報
        login_players (dict): 現在ログイン中のプレイヤ情報
    """

    new_players = {}
    for steamid, value in login_players.items():
        old_player = steamid in all_players
        if old_player:
            continue

        new_players[steamid] = value

    return new_players

def send_discord_webhook(login_players: dict, is_login: bool):
    """Discord Webhookを使用してプレイヤ情報を送信

    Args:
        player (dict): プレイヤ情報
    """

    if is_login:
        login_or_logout = 'ログイン'
    else:
        login_or_logout = 'ログアウト'

    player_count = len(login_players)
    for player in login_players.values():
        name = player['name']
        staemid = player['steamid']

    webhook_url = settings['discord']['webhook_url']

    if not webhook_url:
        raise Exception('Discord Webhook URLが設定されていない')

    message = f'{name}（{staemid}）が{login_or_logout}しました'
    headers = {"Content-Type": "application/json"}
    data = {"content": message}
    request = requests.post(
        webhook_url,
        data=json.dumps(data).encode(),
        headers=headers,
    )
    if request.status_code != 204:
        print(f'Discord Web Hookの送信に失敗した。status_code: {request.status_code}')

if __name__ == "__main__":

    init_setting()

    prev_fetch_time = dt.now()

    with MCRcon(settings['rcon']['address'], settings['rcon']['password'], settings['rcon']['port']) as rcon:
        old_login_players = {}
        login_players = {}
        while True:

            old_login_players = import_players_json()
            login_players = fetch_players(rcon)
            new_login_players = extract_new_players(old_login_players, login_players)
            
            if new_login_players:
                send_discord_webhook(new_login_players, True)
            
            export_players_json(login_players)
            time.sleep(settings['time']['loop_interval_sec'])
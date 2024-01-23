from mcrcon import MCRcon
from pprint import pprint
from datetime import datetime as dt

import os, json, csv, io, argparse, time

# ShowPlayersで不正なUIDの時に発行される
INVALID_PLAYER_UID = '00000000'

settings = {
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
        'fetch_player_interval_sec': 30,
        # 自動でプレイヤキックを行うか
        'use_auto_player_kick': False,
        # ロード中にプレイヤキックを行うとサーバが無限ロードされるので安全よりに設定する方がよい
        'auto_kick_player_interval_sec': 3 * 60,
        # ループ間隔 変更不要
        'loop_interval_sec': 15
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
    parser.add_argument('--address', help='Server address', default='127.0.0.1')
    parser.add_argument('--port', help='RCON port', default=25575)
    parser.add_argument('--password', help='Admin password', default='')

    parser.add_argument('--fetch_player_interval_sec', help='RCON fetch player interval(sec)', default=30)
    # parser.add_argument('--use_auto_player_kick', help='Use auto kick', default=False)
    # parser.add_argument('--auto_kick_player_interval_sec', help='Auto kick interval(sec)', default=3*60)

    parser.add_argument('--log_filepath', help='Player log filepath', default='player_log.json')

    args = parser.parse_args()
    settings['rcon']['address'] = args.address
    settings['rcon']['port'] = int(args.port)
    settings['rcon']['password'] = args.password

    settings['time']['fetch_player_interval_sec'] = int(args.fetch_player_interval_sec)
    # settings['time']['use_auto_player_kick'] = bool(args.use_auto_player_kick)
    # settings['time']['auto_kick_player_interval_sec'] = int(args.auto_kick_player_interval_sec)

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
        print('-----import player log-----')
        pprint(player_log)
    
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
        print('-----export player log-----')
        json.dump(player_log, f, ensure_ascii=False)

def fetch_new_players(rcon: MCRcon, old_players: dict):
    """接続中かつ新規のユーザを取得

    Args:
        rcon (MCRcon): RCON
        old_player_log (dict): 過去に取得済みのプレイヤ情報
    """
    print('-----fetch players-----')
    new_players = {}
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

                is_valid_playeruid = playeruid != INVALID_PLAYER_UID
                if is_valid_playeruid:
                    print(f'Invalid user -> name: {name} staemid: {steamid}')
                    continue
                
                playeruid_hex = format(int(playeruid), 'x')
                playeruid_hex_padded = playeruid_hex.ljust(settings['data']['save_filename_length'], '0')
                sav_filename = f"{playeruid_hex_padded}.{settings['data']['save_file_extension']}"

                exists_old_log =  steamid in old_players
                if exists_old_log:
                    continue

                new_players[steamid] = {
                    "name": name,
                    "playeruid": playeruid,
                    "steamid": steamid,
                    "playeruid_hex": playeruid_hex,
                    'sav_filename': sav_filename
                }

        except:
            rcon.connect()

    return new_players

if __name__ == "__main__":
    print('----start sav filename logger-----')

    init_setting()

    prev_fetch_time = dt.now()

    with MCRcon(settings['rcon']['address'], settings['rcon']['password'], settings['rcon']['port']) as rcon:
        print('-----rcon connect success-----')

        all_players = import_players_json()
        while True:
            now = dt.now()
            need_fetch = (now - prev_fetch_time).total_seconds() >= settings['time']['fetch_player_interval_sec']
            if need_fetch:
                new_players = fetch_new_players(rcon, all_players)
                all_players = {**all_players, **new_players}
                prev_fetch_time = now
            
                exists_new_player = len(new_players) > 0
                if exists_new_player:
                    export_players_json(all_players)

            time.sleep(settings['time']['loop_interval_sec'])
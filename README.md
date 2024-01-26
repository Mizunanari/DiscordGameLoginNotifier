# DiscordGameLoginNotifier

## 概要

PalworldのサーバにRCON接続して一定時間毎にコマンドを使用してログイン情報をポーリングします。プレイヤのログインやログアウトを検知するとDiscordに通知を送信します。

## Setup

PalWorldゲームサーバと同一のサーバで動作させる場合の手順です。

### 1. DiscordでWebHook URLを発行する

「サーバー設定」 > 「アプリ/連携サービス」 > 「ウェブフック」 > 「新しいウェブフック」よりWebフックを作成し、URLをコピーする。

### 2. RCONを設定する

PalWorldのサーバアプリケーションの[設定パラメータ](https://tech.palworldgame.com/optimize-game-balance)で`RCONEnabled`と`RCONPort`を設定し、RCONを有効化します。

| 設定項目    | 設定例 |
| ----------- | ------ |
| RCONEnabled | True   |
| RCONPort    | 25575  |

### 3. DiscordGameLoginNotifierをクローン

DiscordGameLoginNotifierをサーバにクローンします。

```bash
git clone https://github.com/Mizunanari/DiscordGameLoginNotifier.git
cd DiscordGameLoginNotifier
```

### 4. ".env"ファイルを作成する

example.envを元に、.envファイルを作成します。

```bash
cp example.env .env
```

ファイルの中は下記のようになっています。

```text
DGLN_DISCORD_WEBHOOK_URL=''
DGLN_RCON_ADDRESS='127.0.0.1'
DGLN_RCON_PORT='25575'
DGLN_RCON_PASSWORD=''
DGLN_LOOP_INTERVAL_SEC='5'
DGLN_LOG_FILEPATH='player_log.json'
```

| 変数                     | 説明                                                         | 例              |
| ------------------------ | ------------------------------------------------------------ | --------------- |
| DGLN_DISCORD_WEBHOOK_URL | Discordで発行したWebHookのURLを指定する                      | -               |
| DGLN_RCON_ADDRESS        | RCONのアドレスを指定する                                     | 192.168.100.50  |
| DGLN_RCON_PORT           | RCONのポートを指定する                                       | 25575           |
| DGLN_RCON_PASSWORD       | RCONのAdmin Passwordを指定する                               | -               |
| DGLN_LOOP_INTERVAL_SEC   | RCONから取得するプレイヤ情報のポーリング間隔（秒）を指定する | 5               |
| DGLN_LOG_FILEPATH        | 出力するログイン中プレイヤのJSONファイルの名前を指定する     | player_log.json |

### 5. Pythonパッケージのインストール

Ubuntuの場合は、`sudo apt install python3.10-venv`を実行しておく必要がある。

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

###  実行する

tmux経由で実行し、バックグラウンドでも動作するようにします。

```
tmux new -s DiscordGameLoginNotifier
python3 ./discord-game-login-notifier/main.py
```

## 参考

- Discord Web Hook
    - https://discord.com/developers/docs/resources/webhook
    - [Webhooksへの序章](https://support.discord.com/hc/ja/articles/228383668-%E3%82%BF%E3%82%A4%E3%83%88%E3%83%AB-Webhooks%E3%81%B8%E3%81%AE%E5%BA%8F%E7%AB%A0)
- PalWorld
    - https://tech.palworldgame.com/optimize-game-balance
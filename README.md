# Palworld server player logger

## Summary

PalworldのサーバにRCON接続して一定時間毎にプレイヤ情報を出力します。

ユーザがサーバに接続できないとき、ユーザのセーブデータが壊れている可能性があります。

常にログを取ることで壊れたセーブデータの特定を容易にします。

RCON connection to Palworld's server outputs player information at regular intervals.

If a user cannot connect to the server, the user's save data may be corrupted.

Constant logging makes it easier to identify corrupted saved data.

## Attention

何らかの原因によって`ShowPlayers`コマンドが使えないサーバがあります。

このサーバに対してスクリプトを使用するとスクリプトは応答しなくなります。

For some reason, some servers do not allow the `ShowPlayers` command.

If you use the script against this server, the script will not respond.

## Options

次のコマンドを実行してヘルプを参照してください。

Run the following commands for help

`python .\main.py -h`

## Command example

- `python .\main.py --password abcdefg`
- `python .\main.py --address 123.456.789.0 --port 1234 --password abcdefg`

## Log example

- Valid user information

```json
{
    "76561198035441627": {
        "name": "rin_jugatla",
        "playeruid": "1166585980",
        "steamid": "76561198035441627",
        "playeruid_hex": "4588b07c",
        "sav_filename": "4588b07c000000000000000000000000.sav"
    }
}
```

- Invalid user information

If it is invalid, it is not logged to a file, but logged to the console.

```json
{
    "76561198035441627": {
        "name": "rin_jugatla",
        "playeruid": "00000000",
        "steamid": "76561198035441627",
        "playeruid_hex": "0",
        "sav_filename": "00000000000000000000000000000000.sav"
    }
}
```

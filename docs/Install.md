# インストールと運用

サーバへの導入、更新、常駐（systemd --user）、リバースプロキシの
置き方をまとめる。全体の紹介は [../README.md](../README.md)、
画面の使い方は [User.md](User.md)、開発環境の用意は
[Developer.md](Developer.md) を見ること。

## 1. 動かす環境

| もの | 内容 |
| --- | --- |
| サーバ OS | Linux, FreeBSD |
| 言語 | Python 3.14 以上（[uv](https://docs.astral.sh/uv/) でインストール） |
| クライアント | スマホ・タブレット・PC の Google Chrome |
| 前段 | Nginx, Apache などのリバースプロキシ |

## 2. インストール

Python 3.14 以上と [uv](https://docs.astral.sh/uv/) が必要。

```sh
git clone https://github.com/ytani01/ytsched.git
cd ytsched
uv tool install .
```

`~/.local/bin/ytsched` にコマンドが入る。

```sh
ytsched webapp --datadir ~/ytsched/data --port 10085
```

`--datadir` の既定は `~/ytsched/data`、`--port` の既定は 10085、
URL の前置き `--urlprefix` の既定は `/ytsched`。

## 3. 更新

リポジトリを `git pull` したうえで、どちらかを実行する。

```sh
uv tool install --reinstall .   # リポジトリのカレントディレクトリから
uv tool upgrade ytsched         # どこからでも実行できる
```

## 4. systemd --user への登録

ログイン中だけでなく常駐させたい場合は、systemd --user のユニットを
作る。ポートや `--datadir` は環境ごとに違うため、リポジトリには
含めていない。`~/.config/systemd/user/ytsched.service` として、
次の内容で作成する。

```ini
[Unit]
Description=YT Scheduler (ytsched) web server
Documentation=https://github.com/ytani01/ytsched
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
ExecStart=%h/.local/bin/ytsched webapp --datadir %h/ytsched/data --port 10085
Restart=on-failure
RestartSec=5
KillSignal=SIGINT
TimeoutStopSec=10

[Install]
WantedBy=default.target
```

作成したら、有効化して起動する。

```sh
systemctl --user daemon-reload
systemctl --user enable --now ytsched.service
```

状態とログの確認。

```sh
systemctl --user status ytsched.service
journalctl --user -u ytsched.service -f
```

停止・再起動・自動起動の解除。

```sh
systemctl --user restart ytsched.service
systemctl --user stop ytsched.service
systemctl --user disable --now ytsched.service
```

ログインしていない間も動かし続けたい場合（サーバ用途では通常こちら）は、
lingering を有効にする。

```sh
sudo loginctl enable-linger $USER
```

## 5. リバースプロキシ

**認証はこのアプリでは行わず、前段のリバースプロキシに任せる。**
単一ユーザ専用なので、この方がアプリ自体の脆弱性の影響を小さくできる。
リバースプロキシ側で用意するもの:

* SSL
* Basic 認証
* クライアント証明書

アプリはローカルの port（既定 10085）で待ち受けるだけにして、外からは
リバースプロキシ経由でしか届かないようにする。

## 6. 日本の祝日を登録する

`ytsched holiday` で、内閣府の CSV から祝日を取り込んで予定として
登録できる。年は 1 つ以上を引数で指定する。

```sh
ytsched holiday 2026 2027 --datadir ~/ytsched/data
ytsched holiday 2026 --dry-run          # 書き出さずに件数だけ見る
```

同じ日付で同じ名称の予定が既にあれば飛ばすので、何度実行しても増えない。
オプションの詳細は [Developer.md](Developer.md) を見ること。

## 7. 旧形式からの移行

10 年以上前に Perl CGI 版で作ったタブ区切りのデータは、
`ytsched migrate` で JSON Lines へ変換する。元の `.cgi` は消さない。

```sh
ytsched migrate --datadir ~/ytsched/data
ytsched migrate --datadir ~/ytsched/data --dry-run
```

データ形式そのものは [data-format.md](data-format.md) にある。

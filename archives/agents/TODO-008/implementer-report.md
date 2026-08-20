# TODO-008 implementer 報告

## 1. `install.sh` / `Ytsched.src` の削除

`git rm` で削除した。

```
$ git rm install.sh Ytsched.src
rm 'Ytsched.src'
rm 'install.sh'

$ git status --short
D  Ytsched.src
D  install.sh
?? archives/agents/TODO-008/
```

（`archives/agents/TODO-008/` は依頼書とこの報告ファイル。コミットは
main が行うので、こちらでは commit していない。）

## 2. 他に参照している箇所

`grep -rn "install\.sh\|Ytsched\.src\|boot-Ytsched\|~/bin/Ytsched"`
（`.git` を除く）の結果、**削除が必要な参照は無かった**。
残っている一致は、次のとおり文書側のものだけ。

| ファイル | 行 | 内容 | 扱い |
| --- | --- | --- | --- |
| `TODO.md` | 20, 27, 31, 32 | TODO-008 の項目そのもの | main が扱う。触っていない |
| `archives/agents/TODO-002/verifier.md` | 52 | 当時の記録 | archives なので直さない |
| `archives/agents/TODO-002/migrator.md` | 23 | 当時の記録 | archives なので直さない |
| `archives/todo/TODO-002. uv プロジェクトへの移行.md` | 84 | 当時の記録 | archives なので直さない |
| `archives/agents/TODO-008/implementer-request.md` | 6, 21, 23, 24, 28, 76 | 今回の依頼書 | そのまま |

コード・設定側の確認結果:

- `README.md` — `install.sh` への言及は無い。`## Install` が `TBD` の
  ままなので、ここは TODO-009 の担当（書き換えていない）
- `pyproject.toml` — 参照無し。`[project.scripts]` は
  `ytsched = "ytsched.__main__:cli"` のままで変更不要
- `mise.toml` — 参照無し（`upgradeproject` / `lint` / `test` / `build`
  はすべて `uv` 経由）
- CI 設定（`.github/` など）は**このリポジトリに存在しない**
- リポジトリ直下に `CLAUDE.md` はまだ無い（TODO-010 の担当）
- `pkgs.txt`（`install.sh` が読んでいた apt パッケージ一覧）も
  リポジトリに存在しない。孤児ファイルの残骸は無かった

参考: 揃える先の `~/work/tmr` にも `install.sh` 相当のものは無く、
`uv tool install` 前提の構成になっていることを確認した。

## 3. `uv tool install` の手順（実行結果）

```
$ cd /home/ytani/work/ytsched
$ uv tool install .
Resolved 4 packages in 450ms
   Building ytsched @ file:///home/ytani/work/ytsched
      Built ytsched @ file:///home/ytani/work/ytsched
Prepared 1 package in 162ms
Installed 4 packages in 4ms
 + click==8.4.2
 + loguru==0.7.3
 + tornado==6.5.8
 + ytsched==0.1.dev19+geef7e69ce.d20260820 (from file:///home/ytani/work/ytsched)
Installed 1 executable: ytsched

$ which ytsched
/home/ytani/.local/bin/ytsched

$ uv tool dir --bin
/home/ytani/.local/bin

$ uv tool dir
/home/ytani/.local/share/uv/tools
```

`ytsched --help`:

```
Usage: ytsched [OPTIONS] [COMMAND] [ARGS]...

  sample package

Options:
  -h, --help  Show this message and exit.

Commands:
  webapp   Web server
  x-data1  test
```

`ytsched webapp --help`:

```
Usage: ytsched webapp [OPTIONS]

  Web server

Options:
  -p, --port INTEGER        port number, default=10085
  -r, --webroot PATH        Web root directory, default='/home/ytani/.local/sh
                            are/uv/tools/ytsched/lib/python3.14/site-
                            packages/ytsched/webroot'
  -w, --datadir PATH        data directory, default='/home/ytani/ytsched/data'
  --days INTEGER            +/- days, default=45
  -l, --size_limit INTEGER  upload size limit, default=104857600
  -v, --version             print version
  -d, --debug               debug flag
  -h, --help                Show this message and exit.
```

`--webroot` の既定値が uv tool のインストール先
（`~/.local/share/uv/tools/ytsched/.../ytsched/webroot`）を指しており、
**同梱の webroot が正しく解決されている**ことを確認した。
`--datadir` の既定値も `~/ytsched/data` のままで、TODO-008 の方針どおり。

その他に通したもの:

- `ytsched x-data1 --help` — 正常終了（exit 0）
- `ytsched webapp -v` — `Ytsched 0.1.dev19+geef7e69ce.d20260820 by Yoichi
  Tanibayashi`（exit 0）

## 4. 自分で確かめた起動確認（簡易）

依頼では HTTP の確認は verifier に任せてよいとあるが、
インストール直後に動くところまでは自分でも見ておいた。
**`--datadir` には一時ディレクトリを指定し、`~/ytsched/data` は触っていない。**

```
$ TMPD=$(mktemp -d .../scratchpad/dataXXXX)
$ ytsched webapp --datadir "$TMPD" -p 10186 &
$ curl -s -o /dev/null -w "code=%{http_code}\n" http://localhost:10186/ytsched/
code=200
```

- ログは stderr に出た（`08/20 10:17:16 ℹ️ INFO webapp.py:126 main()>
  start server: run forever ..`）。systemd 配下なら journald に入る
- `--datadir` に指定したディレクトリは `os.makedirs(..., exist_ok=True)`
  で自動作成される（`webapp.py`）ので、ユニット側での事前作成は不要
- 参考: `/ytsched/2026/08/20` のような日付付き URL は 404 になった。
  ルーティングは `/`, `/ytsched`, `/ytsched/`, `/ytsched/edit` のみで、
  日付はクエリで渡す作り。**これは元からの仕様で、今回の変更とは無関係**

## 5. systemd --user のユニット例

リポジトリには置いていない（依頼どおり、文面のみ）。
配置先は `~/.config/systemd/user/ytsched.service`。

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

配置と起動:

```sh
mkdir -p ~/.config/systemd/user
$EDITOR ~/.config/systemd/user/ytsched.service   # 上の内容を書く

systemctl --user daemon-reload
systemctl --user enable --now ytsched.service

# 状態とログ
systemctl --user status ytsched.service
journalctl --user -u ytsched.service -f

# 停止・再起動・自動起動の解除
systemctl --user restart ytsched.service
systemctl --user stop ytsched.service
systemctl --user disable --now ytsched.service
```

ログインしていない間も動かし続けたい場合（サーバ用途では通常こちら）:

```sh
sudo loginctl enable-linger $USER
```

このユニット例は `systemd-analyze --user verify` に通してあり、
警告・エラーなしで exit 0 だった（実際に `enable --now` はしていない。
稼働確認は verifier に任せる）。

`ytsched` を更新したとき:

```sh
cd ~/work/ytsched
uv tool install --reinstall .        # あるいは uv tool upgrade ytsched
systemctl --user restart ytsched.service
```

## 6. 単独で決めた判断

1. **`ExecStart` のパスを `%h/.local/bin/ytsched` と書いた。**
   依頼は「`uv tool install` の実際のインストール先を確かめてそのパスを
   使う」だった。実測は `/home/ytani/.local/bin/ytsched` で、`%h` は
   systemd がホームディレクトリへ展開する指定子なので、実行時には同じ
   絶対パスになる。`--datadir %h/ytsched/data` と書き方を揃えられ、
   README に載せたときにユーザー名を書き換えずに済むのでこちらにした。
   リテラルで `/home/ytani/.local/bin/ytsched` と書いても同じ。
2. **`Environment=PATH=...` を入れなかった。** `ExecStart` を絶対パスに
   したので PATH に依存しない。余分な行を増やさない方を選んだ。
3. **`--port 10085` を明示した。** 既定値と同じで省略もできるが、
   ユニットは「環境ごとにポートが違うから同梱しない」という前提の例なので、
   直す場所が一目で分かる方がよいと考えた。
4. **`KillSignal=SIGINT` を入れた。** Tornado の IOLoop は SIGINT で
   素直に終わる。既定の SIGTERM でも落ちるが、より穏やかに止まる方に
   寄せた。**要らなければ 2 行（`KillSignal` / `TimeoutStopSec`）を
   削ってよい。**
5. **`Documentation=` に GitHub の URL を書いた。** `git remote -v` が
   `git@github.com:ytani01/ytsched.git` なので、それに対応する
   `https://github.com/ytani01/ytsched` を書いた。要らなければ行ごと
   削ってよい。

## 7. 気づいたが直さずに残したもの

- `README.md` の `## Install` は `TBD` のまま、`## 使用環境` の
  「言語: Python3」も古いまま。**TODO-009 の範囲**なので触っていない
- `ytsched --help` の説明文が `sample package` のまま。テンプレートの
  残りと思われる。**どの TODO 項目にも入っていない**ので報告のみ
- `webapp.py` の先頭にシェバンが残っている（`EXE001`）。**TODO-015 の
  範囲**なので触っていない
- `webapp.py:85` に `print("%s %s by %s" % ...)` の printf 書式が残る
  （`UP031`）。**TODO-015 の範囲**

## 8. うまくいかなかったところ

特に無し。削除・インストール・`--help` の確認はすべて意図どおりに通った。

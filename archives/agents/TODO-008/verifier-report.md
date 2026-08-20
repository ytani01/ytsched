# TODO-008 verifier 報告

## 1. `install.sh` / `Ytsched.src` の削除

`git status` で両ファイルが削除としてステージされていることを確認した。

```
$ git status
On branch develop
Changes to be committed:
  (use "git restore --staged <file>..." to unstage)
	deleted:    Ytsched.src
	deleted:    install.sh

Untracked files:
	archives/agents/TODO-008/
```

○ 両ファイルとも `D`（削除・ステージ済み）になっている。

## 2. `uv tool install` が実際に動くこと

```
$ cd /home/ytani/work/ytsched
$ uv tool install --reinstall .
Resolved 4 packages in 366ms
   Building ytsched @ file:///home/ytani/work/ytsched
      Built ytsched @ file:///home/ytani/work/ytsched
Prepared 4 packages in 114ms
Uninstalled 4 packages in 2ms
Installed 4 packages in 1ms
 ~ click==8.4.2
 ~ loguru==0.7.3
 ~ tornado==6.5.8
 ~ ytsched==0.1.dev19+geef7e69ce.d20260820 (from file:///home/ytani/work/ytsched)
Installed 1 executable: ytsched

$ which ytsched
/home/ytani/.local/bin/ytsched
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

`--webroot` の既定値が `uv tool install` のインストール先
（`/home/ytani/.local/share/uv/tools/ytsched/lib/python3.14/
site-packages/ytsched/webroot`）を指していることを確認した。

### webapp の起動と HTTP 応答

一時ディレクトリを datadir にして起動し、`run_in_background` 相当で
バックグラウンド実行した。

```
$ TMPD=$(mktemp -d .../scratchpad/ytsched-data-XXXXXX)
# → /tmp/claude-649/.../scratchpad/ytsched-data-SWocP4
$ nohup ytsched webapp --datadir "$TMPD" -p 10287 \
    > "$TMPD/server.log" 2>&1 &
$ sleep 2
$ curl -s -o "$TMPD/response.html" \
    -w "code=%{http_code}\n" http://localhost:10287/ytsched/
code=200
```

サーバログ（stderr）:

```
08/20 10:19:52 ℹ️ INFO webapp.py:126 main()> start server: run forever ..
```

例外・トレースバックは無かった。

取得した HTML（`response.html`, 126768 バイト）を確認した。
`grep -c '{{'` / `grep -c '{%'` はともに 0 件で、テンプレートの
プレースホルダが生で残っていないことを確認した。`<title>` に
バージョン文字列（`Ytsched: 0.1.dev19+geef7e69ce.d20260820`）が
展開されており、静的ファイルへのリンク
（`/ytsched/static/css/my.css?v=...` など）も生成されていた。
webroot（テンプレート・静的ファイル）が正しく解決されていることを
確認できた。

確認後、プロセスを停止した。

```
$ ps -fp <pid>
... /home/ytani/.local/share/uv/tools/ytsched/bin/python3 \
    /home/ytani/.local/bin/ytsched webapp --datadir ... -p 10287
$ kill <pid>
$ ps aux | grep '[y]tsched webapp'
（出力なし → 停止確認OK）
```

（補足: `pgrep -f "ytsched webapp --datadir ..."` は `pgrep` 自身の
コマンドライン文字列にもパターンがマッチしてしまい、毎回別の PID が
ヒットして紛らわしかった。実プロセスの停止確認は
`ps aux | grep '[y]tsched webapp'`（自己マッチしない書き方）で行った。
この点は今回の作業のやり方の問題であり、ytsched 側の不具合ではない）

○ `uv tool install` は問題なく通り、`ytsched` コマンドと `webapp`
サブコマンドは意図どおりに動作し、HTTP 200 で応答した。

## 3. systemd --user のユニット例の検証

`implementer-report.md` の「5. systemd --user のユニット例」の内容を
一時ファイルへ書き出し、`systemd-analyze --user verify` に通した。

```
$ cat > /tmp/.../scratchpad/ytsched.service << 'EOF'
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
EOF

$ systemd-analyze --user verify /tmp/.../scratchpad/ytsched.service
$ echo "exit=$?"
exit=0
```

標準出力・標準エラーとも何も出力されず（警告・エラー無し）、
終了コードは 0 だった。

`ExecStart` のパス `%h/.local/bin/ytsched` は、2 で確認した
`which ytsched` の実際のパス `/home/ytani/.local/bin/ytsched` と
一致する（`%h` は systemd がホームディレクトリ
`/home/ytani` へ展開する指定子であり、実行時に同じ絶対パスになる）。

依頼どおり、`systemctl --user enable --now` などの恒常的な変更を
伴う操作は行っていない。

○ ユニット例は構文上問題なく、実行パスの整合性も取れている。

## 全体の結論

TODO-008 の 3 つのチェック項目は、いずれも実際に確認でき、
問題は見つからなかった。

1. `install.sh` / `Ytsched.src` の廃止 — ○ `git rm` により削除が
   ステージされている
2. `uv tool install` の手順 — ○ インストール・`--help`・
   webapp の起動と HTTP 200 応答・webroot の解決まで実際に動作した
3. systemd --user のユニット例 — ○ `systemd-analyze --user verify`
   が警告・エラー無しの exit 0。`ExecStart` のパスも実測と整合

見つかった不具合は無し。implementer-report.md にある
「7. 気づいたが直さずに残したもの」「8. うまくいかなかったところ」の
記載についても、今回の確認範囲では追加の問題は見つからなかった。

# TODO-008. uv tool install 方式へ

見込み: main = Sonnet 5 / effort medium、担当 = implementer + verifier
実施: main = Sonnet 5 / effort medium、担当 = implementer + verifier

分担の理由と各担当の報告は
[archives/agents/TODO-008/](../agents/TODO-008/) にある。

## きっかけ

2021 年に書いた `install.sh` / `Ytsched.src` は、venv を手動で作り
`~/bin/Ytsched` という起動スクリプトを生成する仕組みだった。
`pyproject.toml` の整備（TODO-004）で `[project.scripts] ytsched = ...`
がすでに入っており、`uv tool install` でそのまま `ytsched` コマンドが
使える状態になっていたため、古い仕組みを廃止して `uv tool install` へ
一本化することにした。

起動スクリプト（`~/bin/Ytsched`）は廃止すると決めた（2026-08-20）。
データディレクトリは `~/ytsched/data` のまま変えない。

## やったこと

- `install.sh` と `Ytsched.src` を `git rm` で削除した。他に参照している
  箇所が無いか `grep -rn` で確認し、コード・設定側の参照は無いことを
  確認した（`README.md` の `## Install` は `TBD` のままで、これは
  TODO-009 の担当）
- `uv tool install .` を実行し、`~/.local/bin/ytsched` にコマンドが
  入ることを確認した。`WebServer.DEF_WEBROOT` は
  `os.path.dirname(os.path.abspath(__file__))` を基準にしているため、
  インストール先が変わっても同梱の `webroot/`（テンプレート・静的
  ファイル）を正しく解決できている
- systemd --user 向けのユニット例をまとめた（**リポジトリには置かない**。
  ポートや datadir が環境ごとに違うため）。配置先は
  `~/.config/systemd/user/ytsched.service`、`ExecStart` は
  `%h/.local/bin/ytsched webapp --datadir %h/ytsched/data --port 10085`。
  内容は下記「systemd --user のユニット例」のとおり。README への転記は
  TODO-009 で行う

### systemd --user のユニット例

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

更新したとき:

```sh
cd ~/work/ytsched
uv tool install --reinstall .        # あるいは uv tool upgrade ytsched
systemctl --user restart ytsched.service
```

`KillSignal` / `TimeoutStopSec`（Tornado の IOLoop を SIGINT で穏やかに
止めるため）と `Documentation`（`git remote -v` の GitHub URL）は任意。
削っても動く。

## テスト

verifier が実装者の報告を自分の手元で再現し、不具合は見つからなかった
（`archives/agents/TODO-008/verifier-report.md`）。

| 確認 | 結果 |
| --- | --- |
| `install.sh` / `Ytsched.src` の削除 | `git status` で両方とも削除がステージ済み |
| `uv tool install --reinstall .` | 成功。`which ytsched` → `~/.local/bin/ytsched` |
| `ytsched --help` / `ytsched webapp --help` | 正常表示。`--webroot` 既定値がインストール先の同梱 `webroot/` を指す |
| `ytsched webapp --datadir <一時dir>` の起動 | `curl` で 200。テンプレート展開済み（`{{`/`{%` の生残り 0 件）、バージョン文字列・静的ファイルリンクとも正しく出力 |
| `systemd-analyze --user verify` | 警告・エラー無し、exit 0。`ExecStart` のパスは実測の `which ytsched` と整合 |

`--datadir` にはどちらの担当も一時ディレクトリを使い、`~/ytsched/data`
の実データには触れていない。`systemctl --user enable --now` などの
恒常的な変更は行っていない（構文検証のみ）。

## 気づいたが直さなかったもの

- `ytsched --help` の説明文が `sample package` のまま（`__main__.py` の
  `cli` の docstring）。TODO-007 の archives にも同種の指摘
  （`__main__.py` の docstring が別プロジェクトの写し間違い）が残って
  おり、今回も同じ箇所を implementer が見つけた。どの TODO 項目にも
  入っていないので、ここでは直していない
- `webapp.py` のシェバンと `print("%s %s by %s" % ...)` の printf 書式は
  TODO-015 の範囲

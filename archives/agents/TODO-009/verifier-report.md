# TODO-009 verifier 報告

対象: `README.md` の Install / 使用環境 / 課題・問題点 節の更新
（未コミット、`git diff README.md` で確認）

## 1. `uv tool install .` 手順

- 環境: `uv 0.12.5`、`/usr/bin/python3.14`（Python 3.14.7）
- 既に `ytsched` が uv tool として入っていたため、事前に
  `uv tool uninstall ytsched` してから README の手順を再現した。
- `uv tool install .`（`/home/ytani/work/ytsched`、develop ブランチ）
  → ○ 成功。`ytsched==0.1.dev20+gadee33508.d20260820` が入り、
  `~/.local/bin/ytsched -> ~/.local/share/uv/tools/ytsched/bin/ytsched`
  のシンボリックリンクが作成された。
- `ytsched --help` → ○ 正常表示（`webapp` / `x-data1` コマンドあり）。
- `ytsched webapp --help` → ○ 正常表示。`--datadir` の既定値は
  `/home/ytani/ytsched/data`（README の記載と整合）。
- `uv tool install --reinstall .` → ○ 成功（
  `Uninstalled 4 packages` → `Installed 4 packages`）。
- webapp 起動確認: `ytsched webapp --datadir <一時ディレクトリ>
  --port 12345` をバックグラウンドで起動し、3 秒後に
  `curl -o /dev/null -w '%{http_code}' http://localhost:12345/ytsched/`
  → **200**。ログ（`webapp.py:126 main()> start server: run
  forever ..`）に例外・トレースバックなし。確認後 `kill` してプロセス
  終了を確認済み。実データ（`~/ytsched/data`）には触れていない。

## 2. systemd --user ユニットの構文検証

- README 記載の ini をそのまま一時ファイルに書き、
  `systemd-analyze --user verify <一時ファイル>` を実行
  → **exit=0**、標準出力・標準エラーとも空（警告・エラー無し）。
  検証後、一時ファイルは削除済み。実際の `enable` はしていない。
- `ExecStart=%h/.local/bin/ytsched ...` の `%h` は `$HOME`
  （`/home/ytani`）に展開される。`which ytsched` の実際の出力
  `/home/ytani/.local/bin/ytsched` と一致することを確認 → ○

## 3. `requires-python` と README「使用環境」節の整合

- `pyproject.toml` 10 行目: `requires-python = ">=3.14"`
- `README.md` 111 行目「言語: Python 3.14 以上（uv でインストール）」
- `README.md` 125 行目「Python 3.14 以上と uv が必要。」
- いずれも整合している → ○

## 4. 「課題・問題点」の文面修正

`git diff README.md` で確認した差分（該当部分のみ抜粋）。

```
-  - 数十年分の検索をいかに効率よく検索するか？
+  - 数十年分のデータを、いかに効率よく検索するか？
...
-  - 手書きき同様、繰り返し書き込む必要がある
+  - 手書きの手帳と同様、繰り返し書き込む必要がある。
...
-    UIを工夫して対応するしかない
+    UIを工夫して対応するしかない。
```

- 検索機能の改良（数十年分のデータの検索効率）という論点、
  期間・繰り返しスケジュールの 2 点（繰り返し書き込みが必要／
  UI の工夫で対応するしかない）という内容は変わっていない。
  誤字（「検索をいかに」→「データを、いかに」、「手書きき」→
  「手書きの手帳」）の訂正と句点の追加のみ → ○ 内容は変えていない

## 問題点

見つからなかった。すべて確認項目○。

## 備考

- 確認のため一時的に既存の uv tool（TODO-008 で入れたもの）を
  アンインストールし、README 手順で入れ直した。中身は同じリポジトリの
  develop ブランチから入れているため、実質的な環境変化は無い。

# TODO-036 verifier 報告

対象（すべて未コミット、`git status --short` で確認済み）:

- `src/ytsched/click_utils.py`（新規）
- `src/ytsched/__main__.py`（変更）
- `src/ytsched/webapp.py`（変更）

## 1. 決まった手順

- `mise run fmt` → ○（ruff format: 23 files unchanged / ruff check: All checks passed）
- `mise run lint` → ○（fmt + typecheck が実行され、いずれも通った）
- `mise run typecheck` → ○（basedpyright: 0 errors, 0 warnings, 0 notes / mypy:
  Success: no issues found in 20 source files）
- `mise run test` → ○（`uv run pytest tests` で **412 passed**、実装者の報告と一致）

`mise run upgradeproject` は走らせていない。

## 2. CLI が実際に動くか

- `uv run ytsched --version` / `-V` / `-v` → 3 つとも
  `ytsched 0.1.1.dev6+g061772762` を出して終了。○
- `uv run ytsched --help` / `-h` / 引数なし → いずれも同じヘルプ
  （`-V, -v, --version` / `-d, --debug` / `-h, --help` とサブコマンド一覧）
  が出る。○
- `uv run ytsched webapp --help` / `migrate --help` / `x-data1 --help` →
  3 つとも末尾に `-V, -v, --version` / `-d, --debug` / `-h, --help` が
  並んでいることを目視確認。○
- `uv run ytsched webapp -V` → `ytsched 0.1.1.dev6+g061772762` を出して
  `exit code: 0`。サーバは起動していない（プロセスが残らないことを
  `timeout 5` 経由で確認）。○

## 3. `--debug` の合成

**migrate（4 通り、`--dry-run --datadir <tmp>`。DEBUG 行数は `grep -c DEBUG`）**

| コマンド | DEBUG 行数 |
|---|---|
| `--debug migrate --dry-run` | 3（出る） |
| `migrate -d --dry-run` | 3（出る） |
| `--debug migrate -d --dry-run` | 3（出る） |
| `migrate --dry-run`（デバッグ無し） | 0（出ない） |

依頼書どおりの結果。○

**webapp（4 通り、`--datadir <tmp> --port <空きポート>` を `timeout 3` で
起動し、標準出力・標準エラーをログファイルへ落として確認）**

| コマンド | DEBUG 行数 | Application の `'debug'` |
|---|---|---|
| `--debug webapp` | 7（出る） | `True` |
| `webapp -d` | 7（出る） | `True` |
| `--debug webapp -d` | 7（出る） | `True` |
| `webapp`（デバッグ無し） | 0（出ない） | （ログに設定行自体が出ない） |

`'autoreload': True` も `--debug` 有りのケースで確認した（1 パターン目で
明示的に grep、他は debug の値が揃っていれば同じ設定のはずなので省略）。
`WebServer` まで `--debug` が届いていることを確認できた。○

## 4. webapp が起動して応答するか

```
TMP=$(mktemp -d)
uv run ytsched webapp --datadir "$TMP" --port 10295 &
curl -s -o resp.html -w "%{http_code}\n" http://localhost:10295/ytsched
```

- HTTP ステータス: **200**
- `resp.html` に `{{` / `{%` の生残りは無し（`grep -n` で 0 件）
- バージョン文字列 `0.1.1.dev6+g061772762` が 3 箇所で描画されていた
  （`WebServer` の `version` 引数を削除したあとも、`Application` 側の
  `version=VERSION` がテンプレートへそのまま渡っていることを確認）
- サーバのログ（stdout/stderr）に例外・トレースバックは無し。出ていたのは
  `INFO webapp.py:121 main()> start server: run forever ..` の 1 行のみ

起動したプロセスは `kill` で停止済み。実データディレクトリ
（`~/ytsched/data`）には触れていない。

## 5. 文書に書かれた手順

- `README.md` の `ytsched webapp --datadir ~/ytsched/data --port 10085`、
  `docs/Developer.md` の同じ形と `ytsched migrate --datadir ~/ytsched/data`
  は、実データの代わりに `mktemp -d` の一時ディレクトリで構文・実行結果を
  確認した。両方とも通る（`migrate` は空ディレクトリに対して
  `no target file .. check --datadir` の警告を出しつつ exit code 0）
- `mise run webapp`（`uv run ytsched webapp` そのもの）は 2 の確認と同じ
  経路なので別途は走らせていない

## 気づいたこと（コードは直していない）

- 実装者の報告にある「`--version` の表示が `Ytsched` ではなく `ytsched`
  になる」件は、依頼書どおり main の判断待ちのまま。動作自体に問題は無い
- `pgrep -af "ytsched webapp"` で確認したところ、検証と無関係に
  `-p 12345 -u /ytsched2` で動いている既存の `ytsched webapp` プロセスが
  常駐していた（今回の確認とは無関係、既存の開発用プロセスと思われる。
  こちらには一切触れていない）

## 結論

依頼書にある確認項目はすべて実際に手を動かして確かめ、実装者の報告と
食い違う点は無かった。不具合は見つからなかった。

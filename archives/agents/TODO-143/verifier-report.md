# TODO-143 verifier 報告

## 確認結果（すべて○）

- `uv run pytest -q` → 589 passed（152.52s）
- `uv run ruff format --check src/ytsched/trash.py src/ytsched/main_handler.py tests/test_trash.py tests/test_web.py`
  → 4 files already formatted
  （`uv run ruff format --check`（全体）は 9 件 unformatted と出るが、
  すべて `archives/todo/*.md` で今回の変更と無関係。既存の状態）
- `uv run ruff check` → All checks passed!
- `uv run basedpyright src/ytsched/trash.py src/ytsched/main_handler.py`
  → 0 errors, 0 warnings, 0 notes
- `uv run mypy src/ytsched/trash.py src/ytsched/main_handler.py`
  → Success: no issues found in 2 source files

## アプリ起動確認

一時ディレクトリ（`mktemp -d`）を `--datadir` に指定して
`uv run ytsched webapp --datadir <tmp> --port 18765` をバックグラウンドで起動。

- 0 件のとき: `curl http://127.0.0.1:18765/` → HTTP 200。
  週間表示フッターのゴミ箱リンク内に
  `<span class="my-fs-xx-small align-middle">(0)</span>` を確認
- `trash.jsonl` へ 105 件（各行 JSON、`trashed_at` を文字列で持つ）を
  直接追記後、再度 curl → 同じ箇所が `(105)</span>` に変化。
  `entries()` の `max_entries=100` に引きずられず正しく数えている
- サーバログ（stdout+stderr）に `error` / `traceback` / `exception` は
  出ていない（起動ログの INFO のみ）
- HTML に `{{` `{%` の生残りなし（テンプレートは展開済み）
- 確認後、`pgrep -f` で PID を確認して `kill`、停止を確認

## 問題

見つからなかった。

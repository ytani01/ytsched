# TODO-132 verifier 報告

## 1. mise / pytest

- `mise run fmt` → ruff format 38 files unchanged、ruff check All checks passed
- `mise run typecheck` → basedpyright 0 errors/0 warnings/0 notes、mypy Success (35 source files)
- `mise run lint` → fmt/typecheck に加え eslint も完走（エラー無し）
- `uv run pytest -q` → **555 passed**（implementer 報告と一致）

## 2. 追加テストの妥当性

`tests/test_main_handler.py` の
`test_todo_deadline_sets_has_todo_important` と
`test_canceled_important_todo_is_not_important` を読んだ。

- 重要な ToDo（`!報告書`）の日が `True`、ふつうの ToDo（`連絡`）の日が
  `False` を確認している
- 取り消し済み（`(欠)!報告書`）が `False` になることも確認している

依頼の 3 条件（重要な ToDo の日が真、普通の ToDo の日が偽、取り消し済みの
重要な ToDo が偽）を過不足なくカバーしている。判定の根拠は薄くない。

## 3. 日付ファイルに ToDo 型の行が混ざった場合

`src/ytsched/sched_load.py` の `load_month_cal()` を読んだ。
`day_sde` のうち `is_todo()` が真のものを `todo_sde_list` に分け、
`has_todo_important = date1 in todo_important_dates or any(sde.is_important() for sde in todo_sde_list)`
としており、日付ファイル側に混ざった ToDo 型行の重要判定もコード上
拾えている（TODO-129 で `has_todo` に対して足した経路と同じ形）。

ただし **この経路（日付ファイル混在 + 重要 ToDo）に対応するテストは
見当たらなかった**。`test_todo_in_day_file_is_shown_as_todo` は
`has_sched`/`has_todo` のみを見ており、`has_todo_important` は見ていない。
依頼どおり、テストを足さずここに報告するに留める。

## 4. アプリの起動と見た目

一時ディレクトリ（`/tmp/.../scratchpad/ytsched-datadir`）に
`ToDo.jsonl`（重要な ToDo `!重要な報告書` を 8/31、ふつうの ToDo
`ふつうの連絡` を 8/30）と、日付ファイル `2026/08/29.jsonl`（予定）を
用意し、`uv run ytsched webapp --datadir <一時ディレクトリ> --port 18321`
を起動。

- `curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:18321/` → `200`
- `curl 'http://127.0.0.1:18321/?year=2026&month=8'` の HTML を確認
  - 8/31（重要 ToDo）: `<div class="my-mini-cal-sq my-mini-cal-sq-important"></div>`
  - 8/30（ふつう ToDo）: `<div class="my-mini-cal-sq"></div>`（`-important` 無し）
  - 8/29（予定のみ）: `<div class="my-mini-cal-dot"></div>`
  - `{{ }}` / `{%` の生残りは無し
- CSS（`my.css`）を確認: `.my-mini-cal-sq { box-sizing: border-box; width: 6px; height: 6px; border: 2px solid #28F; }`、`.my-mini-cal-sq-important { border-color: #E33; }`。外寸はドット（6px）と揃っている
- スクリーンショットで拡大表示し、8/29 が青ドット、8/30 が青の枠のみ四角、
  8/31 が赤の枠のみ四角（塗りつぶしなし）であることを目視で確認した
  - `/home/ytani/tmp/playwright-mcp/todo-132-minical.png`（全体）
  - `/home/ytani/tmp/playwright-mcp/todo-132-minical-zoom.png`（ミニカレンダー拡大）
- サーバのログ（`ytsched-server.log`）に例外・トレースバックは無し
- 確認後、`pgrep -fa "ytsched webapp.*18321"` で PID を確認し `kill` で停止

## 見つけた問題

実装上の不具合は見つからなかった。上記 3. の「日付ファイル混在 + 重要
ToDo」の組み合わせにテストが無い点だけ、判断が要る点として報告する
（依頼の指示どおりテストは足していない）。

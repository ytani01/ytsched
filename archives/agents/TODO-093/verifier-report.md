# TODO-093 verifier 報告

依頼書の 5 項目のみ確認。作業ディレクトリ `/home/ytani/work/ytsched`（develop）。

## 結果

| # | 項目 | 結果 |
|---|---|---|
| 1 | `mise run lintjs` / `mise run fmtjs` | ○ lintjs エラーなし。fmtjs は 9 ファイルすべて unchanged（`.js` 書き換えなし。`git status` も変化なし） |
| 2 | `mise run lint`（ruff / eslint / basedpyright / mypy） | ○ 全部緑。ruff check All checks passed / eslint エラーなし / basedpyright 0 errors / mypy Success（28 files） |
| 3 | `mise run test` | ○ 481 passed（64.56s） |
| 4 | `uv run pytest tests/test_browser.py` ×3 | △ 1・2 回目 22 passed。3 回目のみ `test_tap_again_stops_auto_page_turn` が 1 件 failed（21 passed）。下記のとおり **TODO-093 由来ではなく既存の flaky** |
| 5 | 一時 datadir で起動 → curl | ○ 下記 |

## 4 の切り分け

3 回目の失敗内容（`tests/test_browser.py:266`）:

```
AssertionError: assert '2026-09-21' == '2026-09-14'
- 2026-09-14
+ 2026-09-21
FAILED tests/test_browser.py::test_tap_again_stops_auto_page_turn
```

止めるタップの後にもう 1 週送られている（自動ページ送り停止のレース、`AutoTurnMsec=300`）。

`git stash` で TODO-093 の変更を退避し、クリーンな develop で
`test_tap_again_stops_auto_page_turn` と `test_double_tap_starts_auto_page_turn`
を 3 回実行:

- クリーン 1 回目: 同じ assert で failed（`'2026-09-21' == '2026-09-14'`）
- クリーン 2 回目: 2 passed
- クリーン 3 回目: 同じ assert で failed

変更なしでも 2/3 で落ちた。**既存の flaky（TODO-084 の停止タイミング）で、
TODO-093 の変更由来ではない。** TODO-093 は自動ページ送りの start/stop
（`main-page.js` の `startAutoPageTurn` 等）に触れていない。`stash pop` で復元済み。

## 5 の詳細

コマンド: `uv run ytsched webapp --datadir <mktemp -d> --port 5599`（バックグラウンド）、
`curl -s "http://localhost:5599/ytsched/?date=2020-01-08"`

- HTTP 200
- `<div id="week_wrap" class="my-week-wrap" data-monday="2020-01-06">` を確認。
  2020-01-08 は水曜、その週の月曜は 2020-01-06 で一致
- `id="date_from"` は HTML に無し（grep 0 件）
- 生の `{{` / `{%` は無し（各 grep 0 件）
- サーバログに error / traceback / exception なし
- `pgrep -f "ytsched webapp"` で PID を確認して kill 済み。残プロセスなし

## main の判断が要る点

- test_browser.py の flaky（`test_tap_again_stops_auto_page_turn`）は
  TODO-093 とは無関係の既存問題。TODO-093 の範囲外なのでこのまま進めてよいか、
  別 TODO を立てるかは main 判断。

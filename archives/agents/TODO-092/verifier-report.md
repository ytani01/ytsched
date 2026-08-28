# TODO-092 verifier 報告

挙動を変えない掃除（I〜L）の動作確認。結論: 問題なし。

## 確認結果

| 項目 | 結果 | 値 |
|------|------|----|
| 1. `mise run test` | ○ | 473 passed / 1 failed（下記、本変更と無関係） |
| 2. `mise run typecheck` | ○ | basedpyright 0 errors, mypy Success (27 files) |
| 3. `mise run lint` | ○ | ruff format 30 files unchanged, ruff check All passed |
| 4. アプリ起動 + curl | ○ | 下記 |
| 5. `test_todo_urgency` | ○ | `pytest -k todo_urgency` → 7 passed |

想定は 474 passed。内訳は 473 passed + 1 failed で合計 474。件数は想定どおり。

## 1. の失敗テストについて

`tests/test_browser.py::test_tap_again_stops_auto_page_turn`
- 症状: 自動送り停止後に `data-monday` が `2026-09-14` の想定に対し `2026-09-21`
  （1 週分進んだまま）。自動ページ送り（TODO-084）のタイミング依存。
- 単体で再実行 → `1 passed`（4.37s）。flaky。実装者報告の「別テスト 1 件が
  flaky」と一致。テンプレート掃除とは無関係（`test_browser.py` は未変更）。

## 4. 起動確認

コマンド:
```
uv run ytsched webapp --datadir <一時dir>   # ポート 10085 で listen
curl -s -o - -w '%{http_code}' http://localhost:10085/ytsched/
```

- `GET /ytsched/` → 200。HTML に生の `{{ }}` `{% %}` なし（grep 0 件）。
- `GET /ytsched/?date=2021-03-01` → 200。未展開の `{{ }}` `{% %}` 0 件。
- 検索モード `GET /ytsched/?date=2021-03-01&search_str=会議` → 200。
  未展開の `{{ }}` `{% %}` 0 件。期間・件数の表示は `(in 1826 days)`
  （5 年 + 1 日 = 整数。`timedelta` の生表記や壊れた値なし）。
  `date.resolution` への置換は正しく動作。
- サーバログ: `start server: run forever ..` の 1 行のみ。例外・
  トレースバック・warning なし。
- 終了: PID 2436907 を kill。ポート 10085 解放、`ytsched webapp` プロセス残なし。

## main の判断が要る点

- 実装者が「単独で決めた判断」として挙げた `delta_day1` → `date.resolution`
  置換（`main.html` 検索バーの `(in N日)` 表示）。表示は `(in 1826 days)` で
  正常。値・表示とも変化なしを確認済みだが、依頼の「grep で参照が無いことを
  確かめてから消す」から外れた対応なので、採否は main が判断。

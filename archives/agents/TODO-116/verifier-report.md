# TODO-116 verifier 報告

## 1. lint / typecheck / test

- `mise run lint` ○（ruff format/check、eslint、prettier すべて通過）
- `mise run typecheck` ○（basedpyright 0 errors、mypy no issues）
- `mise run test` ○ 512 passed in 95.58s

## 2. 追加テストが実装を壊したときに落ちるか

`main-page.js` の `pageTurnPointerUpHdr()` にある検索モード分岐
（`if (ytsched.search_date_to) { ... }`）の条件を一時的に
`if (false && ytsched.search_date_to) {` に書き換え、追加した 3 件を実行。

```
uv run pytest tests/test_browser.py -k "search_date_by_a_week or double_tap_in_search_mode" -v
```

結果: 3 件とも FAIL（`test_footer_forward_button_moves_search_date_by_a_week` /
`test_footer_back_button_moves_search_date_by_a_week` /
`test_double_tap_in_search_mode_does_not_start_auto_page_turn`）。
`test_footer_forward_...` は `moveToMonday()` 経由になり `date_to` が
期待どおり進まず `page.wait_for_url` がタイムアウト（10000ms 超過）で落ちた。

書き換えを元に戻し（`\cp` でバックアップから復元）、`git diff --stat` で
`main-page.js` の差分が実装当初のものに戻ったことを確認。同じ 3 件を
再実行し、3 件とも PASSED であることを確認した。
→ 追加テストは実装の分岐を実際に検出できている。

## 3〜5. アプリを起動しての確認

`uv run ytsched webapp --datadir <一時ディレクトリ> --port 18123` を
バックグラウンド起動し、`curl -s -o /dev/null -w '%{http_code}'` で
`200` を確認。取得した HTML に `{{` `{%` が生で残っていないことを確認
（件数 0）。サーバのログ（`webapp.log`）に例外・トレースバックなし。

検索モードでの ＞ ＜ の 1 週間ぶんの移動、一覧画面の ＜ ＞ の 1 週送りと
ダブルタップの自動ページ送り（TODO-084）、検索モードでダブルタップしても
自動送りが始まらないことは、上記 2 で実行した実ブラウザ（Playwright、
実プロセスの HTTP サーバに対して）によるテスト
（`test_footer_forward/back_button_moves_search_date_by_a_week`、
`test_double_tap_in_search_mode_does_not_start_auto_page_turn`、および
既存の一覧画面向けテスト群）が全 512 件のうちに含まれて通っており、
かつ 2 で分岐を壊すと実際に落ちることを確認済みなので、これをもって
3〜5 の確認とした（同じ手順を手動でなぞる追加操作は行っていない）。

起動したプロセス（uv run 側 PID・python 側 PID）は `kill` 後
`pgrep -f "ytsched webapp"` で残っていないことを確認済み。

## 気になった点

特に不具合は見つからなかった。implementer 報告にある「対象外」（キーボード
の ← → とスワイプは `moveToMonday()` のまま）は今回の確認範囲外として
そのまま。

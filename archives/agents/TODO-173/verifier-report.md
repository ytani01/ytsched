# TODO-173 verifier report

## lint / test

- `mise run lint`（fmt / fmtjs / typecheck / lintjs） → ○ 全て通過
- `mise run test` → ○ `665 passed in 188.63s`。新規テスト
  `test_home_button_in_month_view_moves_the_gauge_needle` を含む
  `tests/test_browser.py` の 62 件も通過

## 起動・手動確認

`--datadir` は一時ディレクトリ、`--port 10086` で起動。
`pgrep` で PID 確認後 `kill`（`pkill` 未使用）。

Playwright を直接叩いて確認（date=2026-07-15、今日 2026-09-03 と同じ
7〜12 月ブロック外だが 1〜6 月ブロック側で確認。テストの
`_same_block_other_month` と同じ考え方）:

1. 月間表示・ホームボタン: `?date=2026-07-15&view=month` を開くと
   針は `-1.6m`。`#home_button` クリックで `±0` になり、
   URL は `?date=2026-08-31&view=month`（今週の月曜）へ更新。○
2. 直後に `page.go_back()`（popstate） → URL は
   `?date=2026-07-15&view=month` に戻り、針も `-1.6m` に戻った。○
3. 同状態でキーの `Home` → 針が `±0` になった（URL は
   `?date=2026-09-03&view=month`。`cur_day` を今日の日付で送っている
   模様で、月曜日固定の home_button と表現が違うが、針は正しく `±0`）。○
4. 月間表示のブロック送り（`#forward_button`）: `2026-07-15` から
   1 回押すと `?date=2027-01-01&view=month`、針は `+3.9m`
   （ブロック先頭の位置。今までどおり）。○
5. 週間表示: `#forward_button` で週送り→針が動く、`#home_button` で
   `±0` に戻る。いずれも今までどおり動いた。○
6. 検索モード: `#search_str` に入力して検索アイコンをクリック →
   ページが遷移し、`{{ }}` や `{%` の生残りは無し。表示は壊れていない
   （テストデータが空なので検索結果自体は関係ない挙動だが、テンプレート
   展開は正常）。○

サーバログ（`webapp.log`）に例外・トレースバックは無し。既存の
`ToDo_Days='1y'` 警告のみ（本件と無関係、既知）。

## 見つけたこと

特になし。完了条件（依頼に書かれたもの）はすべて満たしていることを
確認した。

## 判断が要る点

なし。

# TODO-123 verifier 報告

## 最終結果

- ○ `uv run pytest tests/test_browser.py -k 'auto_page_turn_in_search_mode' -v`
  - 3 passed, 39 deselected（前送り・後送り・同じボタンでの停止）
- ○ `uv run pytest tests/test_browser.py -k 'tap_outside_stops_auto_page_turn_without_week_slide_in_search_mode' -v`
  - 1 passed, 41 deselected（検索欄を押すと停止、週枠に
    `.my-week-wrap-sliding` が付かないこと）
- ○ `npx eslint src/ytsched/webroot/static/js/main-page.js`
  - 成功
- ○ `git diff --check`
  - 成功

## 差分確認

- `sessionStorage` の方向を読み直し後の `onloadHdr()` で読み、
  `AutoTurnMsec` ごとに `moveActiveDate()` を実行する。
- 検索画面の `moveActiveDate()` は `slideWeekWrap()` を通らない。
- フッター外の `pointerdown` は `stopAutoPageTurn()` を呼ぶ。

## 判断

問題は確認していない。main の判断が必要な点はない。

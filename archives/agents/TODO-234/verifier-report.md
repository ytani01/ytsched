# TODO-234 verifier 報告

対象: HEAD `0b7411d`。コードは直していない。

## 1. `uv run pytest tests/test_browser.py -k "home or flash"` ○
20 passed, 80 deselected（72.92s）。

## 2. 壊すと落ちるか（`cp` で `$S/*.orig` に複製→`sed -i` で壊す→`cp` で戻す。`git checkout` は使っていない）
全部 `-k "home or flash"`（20 件）で流した。

| 壊し方 | 結果 | 落ちたテスト |
|---|---|---|
| `main-page.js` 177 行 `ytsched.flashDate(today_str);` を削除 | ○ 落ちた（1 failed, 19 passed） | `test_home_button_single_click_puts_today_on_top_and_flashes` |
| `main-page.js` 107 行 `date: today_str` → `ytsched.getLocaltimeDateString(ytsched.mondayOf(today_str))` | ○ 落ちた（3 failed, 16 passed, **1 skipped**） | `test_home_button_double_tap_reloads_the_week_view` / `test_home_button_double_tap_returns_to_the_week_view_from_month` / `test_home_button_double_click_flashes_today_not_monday` |
| `keyboard.js` 117 行 `ytsched.flashDate(today_str);` を削除 | ○ 落ちた（1 failed, 19 passed。名前は `-k home_key` で再実行して確認） | `test_home_key_flashes_today` |

- 壊し方 2 の実行だけ 1 件 skipped になった（1 回目の通常実行と壊し方 1・3 では skip 無し）。どのテストが skip したかは `-rs` を付けておらず未確認。実害は未確認。
- 戻したあと `cmp` で `main-page.js` / `keyboard.js` が複製と一致。

## 3. 検索画面のホームボタンのダブルタップ ○
`uv run pytest tests/test_browser.py::test_home_button_double_tap_returns_to_the_top_screen_from_search` を 3 回続けて流した:
3 回とも 1 passed（5.85s / 3.44s / 4.57s）。

## 4. `git status --short`
空ではない。変わっているのは次の 2 つで、私が書き換えたものではない（ソース・テストは無変更）:
- ` M .claude/global-rules-seen`
- ` M archives/agents/TODO-234/model-check.md`（`hooks/model-check.py` が追記するファイル。作業中に 5 行増えた）

## main の判断が要る点
- 壊し方 2 のときの skipped 1 件（上記）。気になるなら `-rs` で再確認を頼んでほしい。

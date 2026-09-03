# TODO-180 verifier 報告

## 1. lint / pytest

- `mise run lint` → ○（ruff format / ruff check / eslint / basedpyright / mypy すべて通過）
- `uv run pytest -q` → 671 passed, 2 failed（全 673 件）
  - 失敗した 2 件（`test_tap_again_stops_auto_page_turn` /
    `test_home_button_double_tap_by_touch_returns_to_the_top_screen[600]`）は
    単独で再実行すると両方通過（`2 passed in 10.55s`）。フルスイート実行時の
    タイミング起因のフレークで、TODO-180 の diff（gauge.js / main-page.js /
    test_browser.py）とは無関係と判断
  - TODO-180 で追加した 3 件（`test_gauge_drag_needle_does_not_pass_this_week_on_reload`
    / `_month` / 既存の `test_gauge_drag_needle_does_not_jump_back_on_release`）を
    単独実行 → `3 passed in 10.18s`

## 2. playwright で実際に動かして確認

一時ディレクトリ (`scratchpad/ytsched-data`) を `--datadir` に指定し、
`ytsched webapp --port 18080` を起動して確認（依頼の 5 シナリオ + console
エラー確認）。テストコードと同じ `sessionStorage` へのログ収集の仕組みを
流用したスクリプトで検証。

- 週間表示 +5w（範囲外）ドラッグして離す → 読み直し発生、離したあとの
  `#gauge_r` の `style.left` のログは `['LOAD:', '60.7432%']` のみ。
  50% を経由せず、移り先の位置（60.74%）に一致 ○
- 月間表示 +3y（範囲外）ドラッグして離す → 読み直し発生、ログは
  `['LOAD:', 'LOAD:', '83.5873%', '83.5873%']`。50% を経由せず、
  移り先（83.59%）に一致、`view=month` も維持 ○
- 週間表示 +4w（範囲内）ドラッグして離す → 読み直しは起きず（ログ空）、
  離したあと針は動かず、最終位置は目的地（59.54%）と一致 ○（TODO-179 の
  挙動を維持）
- `?date=X` → `?date=Y`（10 週先）で開き直す演出（TODO-049）→ 最初の
  記録が `LOAD:`（空、transition 無しで X の位置に置かれた状態）で
  始まり、そのあと Y の位置へ動く。演出は健在 ○
- 週間表示のホームボタン → 中央 50% に戻る ○
- 月間表示のホームボタン（TODO-173）→ `±0` へ戻り、月間表示のまま
  （読み直しなし）○
- 週送り（`ArrowRight`）→ 50% から 53.79% へ変化、想定どおり動く ○
- console エラー・`pageerror` は一度も発生せず ○
- サーバのログ（`server.log`）に例外・トレースバックなし。出ていたのは
  `ToDo_Days='1y'` の警告のみで、既存の挙動・TODO-180 とは無関係

検証に使ったスクリプトは
`/tmp/claude-649/-home-ytani-work-ytsched/47b590b0-3869-4eb8-aa75-99d25401a3e0/scratchpad/verify_todo180.py`
（一時ディレクトリなので保存不要）。

## 3. 気づいた懸念

特になし。挙動・テストとも依頼どおり。

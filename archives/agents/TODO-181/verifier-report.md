# TODO-181 verifier 報告

## 結果まとめ

| 確認項目 | 結果 |
|----------|------|
| 差分が依頼どおり（`assert` → `if elapsed >= interval_msec: pytest.skip(...)`） | ○ tests/test_browser.py:1066-1070 |
| `mise run lint` | ○ 通過（ruff format / ruff check / eslint / basedpyright 0 errors / mypy Success: 40 files） |
| pytest 3 回（`-k "double_tap or home_button" -rs`） | ○ 3 回とも 13 passed / 0 skipped / 0 failed |
| skip 分岐（スクラッチ、混雑時） | ○ `_pytest.outcomes.Skipped` 送出、メッセージが「機械が混雑:」で始まる、tap 1 回 |
| skip されない分岐（スクラッチ、余裕あり） | ○ 最後まで進み tap 2 回 |

## 使ったコマンド

- `mise run lint`
- `uv run pytest tests/test_browser.py -k "double_tap or home_button" -rs -q`（3 回）
- `uv run python <scratchpad>/check_skip.py`

## pytest の詳細

3 回とも `13 passed, 58 deselected`（約 44〜45 秒）。skipped 0 件、failed 0 件。
`_double_tap_home_in_search` 由来の AssertionError は出ていない。
この開発機は今回空いていたため skipped は出なかった（依頼どおり 0 件でも可）。

## スクラッチ確認

`tests/test_browser.py` から `_double_tap_home_in_search` を import し、
`page` をスタブ（`wait_for_selector` 内で `time.sleep(0.05)`）、`tap` を
呼び出し回数カウンタにした。リポジトリのファイルは変更していない。
スクリプト: `/tmp/claude-649/-home-ytani-work-ytsched/6e301425-7bb8-4753-b1f1-e1cac81e22c6/scratchpad/check_skip.py`

- `interval_msec=10`: `Skipped` 例外。`str(exc)` =
  「機械が混雑: 1 回目の読み直しに 50 ミリ秒かかり、10 ミリ秒後の 2 回目を置けない」。
  `startswith("機械が混雑:")` = True。tap は 1 回だけ。
- `interval_msec=100000`: skip されず最後まで到達。tap 2 回。

## 懸念

- 依頼 4 のとおり。読み直しが恒常的に遅くなるリグレッションが入った場合、
  `elapsed >= interval_msec` を満たす経路（`interval_msec` = 500 / 600）は
  fail ではなく skipped に変わり、`test_home_button_double_tap_by_touch_returns_to_the_top_screen`
  などの退行を黙って見逃す余地がある。`-rs` を付けないと skip 理由が
  流れて気づきにくい。CI ログで skipped 件数を監視するなどの運用がないと、
  「混雑」と「本当に遅くなった」の区別は人が理由文を読むまで付かない。
  TODO-165 で無条件 skip を避けた趣旨（主要な退行テストが黙って消える）とは、
  混雑時に限る点で線を引いているが、境界（180〜360 想定に対し 500/600）は
  そこそこ余裕があり、遅延リグレッションが 500ms 超まで進めば隠れうる。
- `None` 経路・呼び出し側は変更なしを確認済み。範囲外の変更は無い。

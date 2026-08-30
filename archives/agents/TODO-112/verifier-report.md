# TODO-112 verifier 報告

## 結果

- ○ 対象2件を10回連続で実行: 計20件が合格（各回 `2 passed, 23 deselected`、8.91〜9.53秒）。
- × `mise run test`: 506件中502件合格、4件失敗（73.11秒）。対象の `tests/test_browser.py` は25件すべて合格。

## 実行コマンド

```sh
for n in {1..10}; do .venv/bin/pytest tests/test_browser.py -k 'double_tap_starts_auto_page_turn or tap_again_stops_auto_page_turn' -q || exit $?; done
mise run test
```

初回の対象テストは隔離環境でポートを開けず、両件ともセットアップ時に
`PermissionError: [Errno 1] Operation not permitted` となった。ローカルHTTPサーバーの
起動を許可した再実行で上記20件は合格した。

## 失敗詳細

- `tests/test_web.py::TestMonthMiniCal::test_day_click_scrolls_to_date`
- `tests/test_web.py::TestInvalidArgs::test_auto_turn_msec_default`
- `tests/test_web.py::TestInvalidArgs::test_auto_turn_msec_from_conf`
- `tests/test_web.py::TestInvalidArgs::test_broken_auto_turn_msec_falls_back_to_the_default`

いずれもレンダリングHTMLにあるべき JavaScript の文字列が見つからない AssertionError。
TODO-112 の変更対象外で、対象ブラウザーテストは通過している。`mise run test` の
`fmtjs` は JavaScriptファイル8件を整形し、作業ツリーに変更が残った。コードは編集していない。

## 追加確認

- ○ TODO-107 後の `window.ytsched.*` のHTML文字列期待値へ更新した4件を独立実行: `4 passed in 0.30s`。
- ○ main の `pytest tests` 実行結果を確認: 506件すべて合格。これは main の実行結果であり、verifier による全件再実行ではない。

```sh
.venv/bin/pytest tests/test_web.py::TestMonthMiniCal::test_day_click_scrolls_to_date tests/test_web.py::TestInvalidArgs::test_auto_turn_msec_default tests/test_web.py::TestInvalidArgs::test_auto_turn_msec_from_conf tests/test_web.py::TestInvalidArgs::test_broken_auto_turn_msec_falls_back_to_the_default -q
```

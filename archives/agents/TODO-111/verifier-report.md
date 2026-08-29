# TODO-111 verifier 報告

## 結果

- ○ 対象ブラウザテスト: 3 passed、21 deselected（10.58 秒）
- ○ Ruff: format は 31 files left unchanged、check は All checks passed
- ○ Prettier: JavaScript 9 ファイル unchanged
- ○ ESLint: 成功
- ○ basedpyright: 0 errors、0 warnings、0 notes
- ○ mypy: 28 source files、問題なし
- × 全 pytest: 503 passed、2 failed（132.73 秒）
- TODO-111 の対象テストに不具合は見つからなかった

## 実行コマンド

```console
uv run pytest tests/test_browser.py -v -k 'week_move_updates_date_inputs or week_move_does_not_reload_the_page or long_search_result_loads_without_javascript_error'
mise run test
```

## 全 pytest の失敗

- `tests/test_browser.py::test_double_tap_starts_auto_page_turn`
- `tests/test_browser.py::test_tap_again_stops_auto_page_turn`

どちらも `page.wait_for_function()` が期待する週への遷移を待ったまま、
10 秒で `playwright._impl._errors.TimeoutError` になった。

## 判断が要る点

全体確認の失敗2件を、TODO-111 の完了前に再調査するか判断が必要。

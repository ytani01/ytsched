# TODO-206 verifier 報告

終了。コードは直していない（壊した 4 か所は全部戻し、`git diff` の md5 が壊す前と一致。`git diff --stat` は 11 files, 90 insertions, 6 deletions のまま）。

## 1. mise run
- ○ `mise run fmt`: 42 files left unchanged / All checks passed!
- ○ `mise run typecheck`: basedpyright 0 errors, 0 warnings, 0 notes / mypy Success: no issues found in 39 source files
- ○ `mise run lint`: 通過（eslint / fmtjs 含む）
- ○ `mise run test`: 706 passed in 146.13s（ブラウザテスト含む）

## 2. 壊すと落ちるか
- ○ a. `xsrf_cookies=True` の行を削除 → `tests/test_webapp.py::test_xsrf_settings - KeyError: 'xsrf_cookies'`
  （test_web.py / test_webapp.py を `-x` で実行したので 1 件で停止。他に落ちるかは未確認）
- ○ b. `expires_days` を 30 → `tests/test_webapp.py::test_xsrf_settings - AssertionError`（1 failed, 182 passed）
- ○ c. `main.html` の `todo_days_form` 内の `xsrf_form_html`（424 行）を削除 →
  `tests/test_web.py::TestXsrf::test_forms_have_xsrf_hidden - assert 2 == 3`（1 failed, 182 passed）
- ○ d. `nav.js` の 192〜197 行（コメント + `_xsrf` を足す処理 + 空行）を削除 → `tests/test_browser.py` が落ちた。
  例: `test_home_button_single_tap_still_reloads_search_screen`,
  `test_home_button_double_tap_returns_to_the_top_screen_from_search` ほか
  （`FAILED` 行は先頭 8 件のみ確認。総数は未集計）

## 3. 実起動（`--port 18765`、datadir は mktemp -d、cookie jar 使用）
- ○ 一覧 GET: 200
- ○ cookie `_xsrf` の Expires = 1822248552、取得時刻 1790712552。差は 31536000 秒 = 365 日
- ○ トークン付き POST（`_xsrf=<token>&todo_days=7`）: 302
- ○ トークン無し POST: 403。本文に「画面が古くなっています。一覧へ戻って、もう一度操作してください。」と `(403)` が出た
- サーバのログに Traceback / Error なし。起動した PID（825161, 825165）は kill 済み

## 気づいたこと（報告のみ）
- 私の起動とは別に、`ytsched webapp --datadir /tmp/tmp.Q70CqDAIOo --port 10197`（PID 792163, 792167）が動いている。
  私のものではないので触っていない。ブラウザテストの残り、または別の起動の可能性がある（実害は未確認）。

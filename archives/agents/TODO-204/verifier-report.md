# TODO-204 verifier 報告

## 1. lint / typecheck / test
- ○ `mise run lint`: 終了 0（fmtjs・lintjs とも問題なし。出力は末尾のみ確認）
- ○ `mise run typecheck`: basedpyright 0 errors, 0 warnings, 0 notes / mypy Success: no issues found in 39 source files
- ○ `mise run test`: 703 passed in 169.20s

## 2. 壊すと落ちるか
コマンド: `uv run pytest -q tests/test_web.py -k "TestConflict or test_update_sde_not_found"`（通常は 6 件）
- a. `is_conflict()` が常に False: 3 failed, 3 passed。落ちたのは test_fix_sent_twice_is_409 / test_todo_fix_sent_twice_is_409 / test_update_from_other_tab_is_409
- b. `sde_id` 欄の `{% if not new_flag %}` を外す: 1 failed, 5 passed。落ちたのは test_new_from_edit_page_is_not_409
- c. `ERROR_MESSAGES` から 409 の行（2 行分）を消す: 3 failed, 3 passed。落ちたのは a と同じ 3 件
- 戻し確認: 試す前後の `git diff` が完全に一致（cmp）
- 補足: c は `test_update_sde_not_found` を含め 404 系は落ちなかった（範囲外なので未確認）

## 3. ブラウザ（Playwright python、chromium、400x800、port 18204、datadir は scratchpad）
- ○ 新規から「更新」: 200。編集画面へ戻り sde_id `…-1`、409 にならない
- ○ タブ A で更新 → sde_id `…-2` へ。タブ B（`…-1` のまま）で更新 → 409
- ○ 409 の画面の本文: 「この予定は、編集画面を開いたあとで変更されています。一覧から開き直してください。」「一覧へ戻る」「(409)」
- ○ 「一覧へ戻る」で一覧が開く: 200、`/ytsched/?date=2026-09-30`
- ○ データ `data/2026/10/01.jsonl`: 1 行（sde_id `…-2` のみ。重複なし）
- ○ サーバのログ: Traceback 0 件
- コンソール（全部）: log `cmd=update` ×3、error `Failed to load resource: the server responded with a status of 409 (Conflict)`、その後の一覧画面で log `onloadHdr`・`scrollToDate`・`scrollToId` ×2。pageerror は 0 件。error は 409 応答に伴うブラウザ標準のもの 1 件のみ
- ○ スクリーンショット `~/tmp/playwright-mcp/TODO-204-409.png`: 説明文（2 行に折り返し）・「一覧へ戻る」リンク・「(409)」が映る。欠け・余計なものなし。余白は下に広く空いている（デザインは評価しない）
- サーバは停止済み（curl で応答なしを確認）

## 気づいたこと（範囲外）
- テンプレートの `{{ }}` `{%` は 409 画面に生では残っていない

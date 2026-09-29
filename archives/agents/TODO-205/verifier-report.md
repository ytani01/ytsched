# TODO-205 verifier 報告

- ○ `mise run lint`: ruff/eslint とも問題なし（fmtjs は unchanged）
- ○ `mise run typecheck`: basedpyright 0 errors, 0 warnings, 0 notes / mypy Success: no issues found in 39 source files
- ○ `uv run pytest tests/test_web.py -q -k Trash`: 29 passed, 145 deselected
- ○ 壊すと落ちる: `_restore()` を `self._sd.add_sde(restored.date, restored)` に戻すと `TestTrashHandler::test_restore_todo_goes_to_todo_file_and_edit_opens` が FAILED（1 failed）。退避から復元し `git diff --stat` は退避前と同一
- ○ 実アプリ（`--datadir` は一時ディレクトリ、trash.jsonl に type `□買い物` を 1 件）:
  - GET /ytsched/trash 200、復活 POST（_xsrf 付き）302 → `/ytsched/?date=2021-03-01`
  - `ToDo.jsonl` に `(復活)ノートを買う` が入り、日付ファイルは作られない
  - 一覧 `/ytsched/?date=2021-03-01` 200、復活行に `data-todo-flag="true"`（リンクは main-page.js が作るため curl では href が取れない）
  - `/edit?date=2021-03-01&sde_id=<新ID>&todo_flag=true` 200（ノートを買う を含む）。参考: todo_flag 無しは 404
  - ログに Traceback なし。アプリは停止済み
- 不具合なし

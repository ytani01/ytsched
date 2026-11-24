# TODO-238 verifier 報告（定型の確認: tests/README.md と tests/ の一致）

- 実行: `git status --short` / `git diff --stat` / `ls tests/*.py` / `rg -o '^- `[a-z_]+\.py`' tests/README.md`
- git 状態: TODO.md・archives/agents/TODO-238/model-check.md・tests/README.md が変更、reviewer-report.md が未追跡。依頼外の変更なし。
- ls tests/*.py: 16 件（helpers.py, make_test_data.py, test_attach.py, test_browser.py, test_fix_id.py, test_handler.py, test_handler_util.py, test_holiday.py, test_main_handler.py, test_migrate.py, test_mylog.py, test_notify.py, test_trash.py, test_web.py, test_webapp.py, test_ytsched.py）
- README の一覧: 16 件。
- 結果: ○ 一致（過不足なし。README 側の欠け・余分は無し）。

判定の対象は作業ツリーの tests/README.md（未コミットの変更を含む）。説明文の中身とテストの実行は対象外。

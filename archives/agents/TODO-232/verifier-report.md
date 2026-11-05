# TODO-232 verifier 報告

対象: `412d3ce`（`tests/test_browser.py` の待つ条件を `h > 300 && h < 360` に）

1. ○ `uv run pytest tests/test_browser.py -k test_detail_fills_between_bars_and_blur_shrinks_it` を 8 回続けて実行: **8 回中 8 回通った**（各 `1 passed`、約 2.3〜2.7 秒）
2. ○ 壊すと落ちる: `src/ytsched/webroot/static/js/edit-page.js` 230 行 `window.addEventListener("resize", resizeHdr);` をコメントアウト（複製は scratchpad に作成）→ 同テストが `1 failed`。
   `playwright._impl._errors.TimeoutError: Page.wait_for_function: Timeout 30000ms exceeded.`（`_wait_detail_height` の待ちで失敗）
   書き戻し: 複製から戻し、sha256 一致を確認。`git diff --stat` 空、`git status --short` は未追跡の `archives/agents/` 配下のみ（`git checkout` は使っていない）。

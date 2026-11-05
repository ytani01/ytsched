# TODO-231 verifier 報告

対象: `94e099b`（`package-lock.json` のみ）。`git status`/`git diff --stat` は実行前後とも、未追跡の `archives/agents/` 以外に変更なし（`npm ci` はロックを書き換えなかった）。

- ○ `npm ci`: 成功。`4 moderate severity vulnerabilities`（立てたときの 5 件 [moderate 4・high 1] から high が消えた）
- ○ `npm audit`: 4 moderate。`minimatch 7.0.0 - 11.0.0`（GHSA-g3hv-75wg-m249）→ `@eslint/config-array` → `eslint` → `@eslint/js`。fix は `npm audit fix --force` のみで `eslint@9.39.5`（breaking）。流していない
- ○ `npm audit --omit=dev`: `found 0 vulnerabilities`
- ○ `mise run lint`: 終了 0。ruff 通過、basedpyright 0 errors/0 warnings/0 notes、mypy `Success: no issues found in 39 source files`、fmtjs 全 `(unchanged)`、`lintjs`（eslint src/ytsched/webroot/static/js）指摘なし
- × `uv run pytest tests/test_browser.py -k "test_detail_fills or test_detail_focus_does_not_move or test_detail_click_does_not_fill or test_detail_manual_height"`:
  - 1 回目: `1 failed, 4 passed`。`test_detail_fills_between_bars_and_blur_shrinks_it` が `tests/test_browser.py:3007`
    `assert filled["top"] == pytest.approx(filled["bar_bottom"], abs=1)` で `Obtained: 234 / Expected: 45 ± 1`
  - 同じ `-k test_detail_fills`（2 件）の再実行: 2 passed
  - 依頼のコマンドを続けて 3 回再実行: 3 回とも `5 passed`
  - 実測 4 回中 1 回落ちた。再現は一度きり。原因は調べていない（`package-lock.json` との関係は未確認、実害は未確認。直前の別テスト実行との並行や負荷の影響かも未確認）

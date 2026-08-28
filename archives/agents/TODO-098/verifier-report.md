# TODO-098 verifier 報告

依頼書: `archives/agents/TODO-098/verifier-task.md` の 7 項目を確認。

## 結果

| # | 項目 | 判定 | 得られた値 |
|---|------|------|-----------|
| 1 | `npx eslint src/ytsched/webroot/static/js` | ○ | 終了コード 0・出力なし。対象 9 ファイル。`git diff --stat` に `static/js/*.js` の変更なし |
| 2 | `mise run lintjs` | ○ | 終了コード 0 |
| 3 | `mise run lint` | ○ | 終了コード 0。ruff format 31 files unchanged / ruff check passed / basedpyright 0 errors / mypy no issues in 28 files / lintjs 通過 |
| 4 | `mise run test` | △ | 下記 |
| 5 | `rm -rf node_modules && npm ci` | ○ | 終了コード 0、ロックファイルから 71 packages。実行後 `npx eslint ...` も終了コード 0 |
| 6 | git 混入なし | ○ | 下記 |
| 7 | `eslint.config.js` の中身 | ○ | 下記 |

## 使ったコマンド

```
npx eslint src/ytsched/webroot/static/js
git diff --stat
mise run lintjs
mise run lint
mise run test
rm -rf node_modules && npm ci
git status --porcelain
git check-ignore node_modules
git check-ignore package-lock.json
npx eslint --rule '{"no-undef":"error","no-unused-vars":"error"}' src/ytsched/webroot/static/js
```

## #4 `mise run test` — フレーク（main の判断が要る）

- 1 回目・2 回目: `tests/test_browser.py::test_tap_again_stops_auto_page_turn`
  が 1 件だけ FAILED（`AssertionError: assert '2026-09-21' == '2026-09-14'`、
  `tests/test_browser.py:266`）。他 480 件は passed。
- 3 回目: 481 passed（全通過）。
- 単独実行 `pytest ...::test_tap_again_stops_auto_page_turn` は passed。
- 追跡している変更（`.gitignore` / `docs/Developer.md` / `mise.toml`）を stash した
  状態でも `tests/test_browser.py` 単独で passed / failed が揺れた。
- TODO-098 の変更は pytest が読むものに触れていない（新規は JS ツール用の
  ファイルのみ、追跡している変更は .gitignore・docs・mise.toml の `[tools]`/`lintjs`）。
- 判断: 自動ページ送りのタイミング依存テストのフレークで、TODO-098 とは
  無関係と見る。ただし本項目の作業中に顕在化したので報告する。

## #6 git 混入なし

- `git status --porcelain` の `??` は `archives/agents/TODO-098/` /
  `eslint.config.js` / `package.json` / `package-lock.json` のみ。
- `git check-ignore node_modules` → 終了コード 0（ignore されている）。
- `git check-ignore package-lock.json` → 終了コード 1（ignore されない）。
- 注: `.gitignore` に `*.lock` があるが `package-lock.json` は `.json`
  終わりなので影響なし（上の check-ignore で確認済み）。
- node は `v26.8.1`（`mise.toml` の `node = "26.8.1"` と一致）。
  `.venv` は Python 3.14.7。

## #7 eslint.config.js

- `rules`: `"no-undef": "off"` / `"no-unused-vars": "off"`。
- `files`: `["src/ytsched/webroot/static/js/**/*.js"]` に限定。
- 設定ファイルは編集しない方針のため、一時的に `error` へ戻す代わりに
  CLI の `--rule` で上書きして確認 →
  `159 problems (159 errors, 0 warnings)`。設定が効いていることを確認。

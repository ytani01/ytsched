# TODO-233 verifier 報告

作業ツリーの差分: TODO.md / src/README.md / main-page.js / tests/test_browser.py と `archives/agents/TODO-233/`（依頼どおり。ほかの変更なし）。

1. `mise run fmt` ○ — 差分は増えず（`git diff --stat` 4 files, 79 insertions, 19 deletions のまま）。
2. `mise run lint` ○（ruff・eslint とも All checks passed / エラー無し）、`mise run typecheck` ○（basedpyright 0 errors, 0 warnings、mypy Success: no issues found in 39 source files）。
3. `uv run pytest -q tests/test_browser.py -k flash` ○ 7 passed / `tests/test_web.py -k flash` ○ 4 passed。
4. 実測（`archives/agents/TODO-233/verifier-check.py <datadir> <port>`、一時 datadir、/usr/bin/chromium、412x300）:
   - a ○ `?date=2026-11-08` → `.my-flash` 1 件、うち `#date-2026-11-08 .my-date-col.my-flash` 1 件。url `/?date=2026-11-08`
   - b ○ 日付なし（その日 40 件）→ `.my-flash` 0 件（url は `?date=2026-11-08` に書き換わっている）
   - c ○ a のあと 6 秒待ち `ytsched.pushDateInUrl` で 2026-11-22 へ移動、さらに 6 秒後 `go_back()`（popstate）→ `.my-flash` 0 件、url `?date=2026-11-08`
   - c2 ○ ミニカレンダーの日（`[data-date]` の 4 つめ）をクリック → url `?date=2026-10-28`（画面内移動）→ 6 秒後 `go_back()` → `.my-flash` 0 件

## 判断が要る点（実害は未確認）
- 最初の試行で、ミニカレンダーの別のリンクをクリックしたところ `/ytsched/?date=2026-11-01&view=month` へページ全体の読み込みで遷移し、`go_back()` 後は `?date=2026-11-08` を読み込み直して `#date-2026-11-08 .my-date-col` に my-flash が 1 件付いた。TODO.md の「リロードや戻る/進むでも `?date=` があれば毎回点滅」に沿うので仕様どおりと見るが、依頼 c の「戻るで 0 件」は popstate（同じ文書内の戻り）に限る。このケースのスクリプトは残していない（上の c/c2 のみ）。

## その他
- 実測中、`ytsched webapp`（PID 1155229、利用者の常駐サーバ）が動いているが、自分が起動したものは終了済み。
- 実データ（`~/ytsched/data`）は触っていない。

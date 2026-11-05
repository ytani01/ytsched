# TODO-229 verifier 報告

対象: `0652f52`（`main-page.js` のコメントと `scrollBy(0, dy)`）。実アプリを `--datadir` 一時ディレクトリで起動、`/usr/bin/chromium` + Playwright。
スクリプト: `uv run python archives/agents/TODO-229/verify_scroll.py`（viewport 412x800、当日に予定 40 件）

1. ○ `getComputedStyle(documentElement).scrollBehavior` = `auto`（body も `auto`）。`rg scroll-behavior src` は 0 件、読み込む CSS は `css/my.css` のみ（Bootstrap の `<link>` 無し）
2. ○ `?flash_date=…&flash_sde_id=id-39` で開くと `scrollBy(0, 482)` が 1 回。呼び出し直後（同期）の `scrollY`: 192 → **674**（移動後の値。アニメーションしていない）。最終 `scrollY` も 674
3. ○ `?sde_align=top` で開いた読み込み直後、`requestAnimationFrame` ごとに記録した `scrollY` の値の集合は `[0, 192]` のみ。途中の値なし。最終 192

食い違い・不具合: なし。作業ツリーの変更: 報告・スクリプト以外なし。

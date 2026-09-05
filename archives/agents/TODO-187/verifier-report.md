# TODO-187 verifier 報告

## 走らせたこと・結果

1. `mise run lint` / `mise run typecheck` → 両方通った
   （ruff format/check、eslint、prettier、basedpyright 0 errors、
   mypy Success: no issues found in 40 source files）
2. `uv run pytest tests/test_browser.py` → **77 passed**（実装者の報告と一致。
   新しい 4 件を含めて全数が実際に走っている）
3. `uv run pytest --ignore=tests/test_browser.py` → **611 passed**
4. アプリを一時ディレクトリ（`/tmp/ytsched-todo187-data`）で起動し
   （`uv run ytsched webapp --datadir ... --port 18187`）、
   `curl` で HTTP 200 を確認。取得した HTML に `{{ }}` / `{%` の生残りなし。
   Playwright（幅 390px）で以下を確認:
   - `.my-gauge-bar` が 2 個（ヘッダーと `#footer_gauge_bar` 内）
   - 下の帯（`footer_gauge_bar`）の下端が `y=590+68=658`、
     メニューバーに接しており重なっていない
   - 針の `left` スタイル・ラベルの文字（`±0`）は上下とも一致
   - **下のゲージをドラッグ**（帯中央から右へ）すると、上下のラベルが
     同時に `+10.3m` へ動いた（`mondayFromClientX` に渡る帯の取り違えなし）
   - メニューを開くと下のゲージがメニューに隠れて見えなくなる
     （スクリーンショットで目視確認）
   - フッターの下までスクロールしても、末尾のカレンダー行が隠れていない
   - 検索モードで `.my-gauge-bar` が 0 個（上下とも出ない）
   - サーバのログ（`server.log`）に例外・トレースバックなし
5. `mondayFromClientX()` への帯の受け渡し（実装者が「捕まえられない」と
   書いた点）は `gauge.js` を確認。pointerdown で
   `event.target.closest(".my-gauge-bar")` した帯を `gaugeBarDragStart.elBar`
   に保持し、pointermove でもそのまま使っている（`gauge.js:466-491`,
   `529-531`）。実測でも下の帯でドラッグして正しく動いたので、
   取り違えは起きていない。

## 見つけた問題

なし。

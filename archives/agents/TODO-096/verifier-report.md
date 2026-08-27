# TODO-096 verifier 報告

## 実施したコマンドと結果

1. `mise run fmt` / `typecheck` / `lint` → すべて通過（ruff format 30 files
   left unchanged、ruff check All checks passed、basedpyright 0 errors、
   mypy no issues found in 27 source files）
2. `uv run pytest -q` → 482 passed（60.95s）
3. `python3 -c "import xml.etree.ElementTree as E; E.parse('src/ytsched/webroot/static/icons/icons.svg')"`
   → ○ 整形式の XML
4. `icons.svg` に `<style>` タグは残っていない。コメント中に「ここに
   `<style>` を」という日本語文言が 1 件あるだけ（実体のタグではない）
5. `my.css` の `.my-icon`（432 行目）に `fill: none` / `stroke: currentColor`
   / `stroke-width: 2` / `stroke-linecap: round` / `stroke-linejoin: round`
   がすべて入っている
6. `.my-icon-9x`（455 行目、`stroke-width: 1`）は `.my-icon`（432 行目）より
   後ろにあり、CSS の前後関係で正しく上書きされる位置関係になっている
7. `src/ytsched/webroot/templates/sde.html` / `edit.html` / `main.html`
   全体で `icons.svg` を参照する `<use>` は 25 箇所あり、いずれも直前の
   `<svg class="my-icon ...">` に `my-icon` クラスが付いている（漏れなし）
8. アプリ起動確認: `uv run ytsched webapp --datadir <一時ディレクトリ>
   --port 18096` をバックグラウンドで起動し、`curl` で確認。
   - `/ytsched/static/css/my.css` → 200
   - `/ytsched/static/icons/icons.svg` → 200
   - 取得した `my.css` の中身は上記 5 の内容と一致
   - 取得した `icons.svg` の中身に `<style` は無し（コメント文言のみ）
   - サーバログに例外・トレースバックは出ていない

   （注: 静的ファイルの URL は `/static/...` ではなく `/ytsched/static/...`
   がベースパスだった。最初 `/static/...` で叩いて 404 になったが、
   `index.html` の実際のリンクを見て気づいた。これはアプリの既存の
   ベースパス設定であり、今回の変更には無関係）

## 判断が要る点

なし。依頼の 7 項目すべて期待どおりの結果。

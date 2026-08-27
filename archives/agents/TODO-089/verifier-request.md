# TODO-089 verifier への依頼

`edit.html` のインライン JavaScript を `static/js/edit-page.js` へ出した。
**挙動は変えていない**という前提を確かめてほしい。

## 変更されたファイル

- `src/ytsched/webroot/static/js/edit-page.js`（新規）
- `src/ytsched/webroot/templates/edit.html`（インライン `<script>` を
  `<script src>` に差し替え）
- `src/README.md` / `src/ytsched/webroot/static/js/spinner.js`
  （コメント・説明の追随。動作には影響しない）

## 確かめること（これだけ。思いついた確認を足さない）

1. **`mise run lint` と `mise run typecheck` が通る。**

2. **`mise run test` が通る。** 件数を報告。
   - 既知の揺れ: `test_browser.py::test_tap_again_stops_auto_page_turn`
     （TODO-084 の自動ページ送り、一覧画面のみ、`setInterval` 依存）が
     タイミングで落ちることがある。落ちたら `test_browser.py` だけを
     単独で再実行し、22 件通ることを確認。**それ以外の失敗は報告する。**

3. **アプリを起動して編集画面を実際に見る。** `run_in_background` で
   `uv run ytsched webapp --datadir <一時ディレクトリ>` を起動
   （既定の url prefix は `/ytsched`）。数秒待ってから:
   - `/ytsched/static/js/edit-page.js` が **200** で返る
   - `/ytsched/static/js/main-page.js` も 200（退行していない）
   - `/ytsched/edit?date=2026-08-28` の HTML を取得し、
     `{{ }}` や `{%` が生で残っていないこと、
     `<script ... src=".../js/edit-page.js...">` が入っていること、
     旧インライン `<script>` の中身（`const wdayList` など）が
     HTML に残っていないこと
   - サーバのログに例外・トレースバックが出ていないこと
   - 終わったら `pgrep -f` で PID を確かめて kill

4. **`edit-page.js` の中身が、元の `edit.html` インライン `<script>` と
   字句レベルで一致している**ことの確認（改名・削除ぶんを除く）。
   `git show HEAD:src/ytsched/webroot/templates/edit.html` で元を取り出し、
   `<script>` の中身と `edit-page.js` を比べる。差分が
   - 先頭コメント
   - `onloadHdr` → `onloadEdit`（定義と `addEventListener` の 2 か所）
   - コメントアウトされた `resize` リスナーの削除
   - `rotationchange` リスナーの削除
   - 全体を 4 スペースのインデント、行末スペースの除去
   だけであること。関数・定数の本体に変更が無いこと。

## 既知の未対応（報告しなくてよい）

- 編集画面のブラウザテストは元から無い（TODO-056）。新規に書かない
- `gauge.js:306` のコメントの `onloadHdr()` は一覧画面の話なので正しい

## 報告

`archives/agents/TODO-089/verifier-report.md` に。返事は 5 行以内。

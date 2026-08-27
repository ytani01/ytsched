# TODO-089 implementer への依頼

`edit.html` のインライン JavaScript を `static/js/edit-page.js` へ出す。
**挙動は変えない。** `main-page.js`（TODO-083）と同じ形に揃える。

## やること

1. **`src/ytsched/webroot/static/js/edit-page.js` を新規作成**し、
   `edit.html` の `<header>` 内 `<script>`（現在 24〜116 行）の中身を
   そっくり移す。先頭は `main-page.js` と同じ形のコメント:

   ```js
   /**
    *   (c) 2026 ytani01
    */

   // edit.html だけで使う関数・リスナー登録 (TODO-089)。
   ```

2. **`edit.html` 側**: インライン `<script>` を削除し、`main-page.js` と
   同じ形の外部読み込みに差し替える。
   **この `<script>` はテンプレートの値（`{{ }}`）を 1 つも使っていない**
   ので、`main.html` のような定数ブロックは要らない。`<script src>` だけ:

   ```html
   <script type="text/javascript"
           src="{{ static_url('js/edit-page.js') }}"></script>
   ```

   `base.html` には入れない（`main-page.js` と同じ理由。`edit.html` が
   自分で読み込む）。

3. **`onloadHdr()` の名前衝突を解く**（プランの 2 点目）。
   `main-page.js` にも `onloadHdr` があり中身が違う。同時には読み込まれ
   ないので実害は無いが、読む側が混乱するので `edit-page.js` 側を
   **`onloadEdit`** に改名する。`window.addEventListener('load', onloadHdr)`
   の登録側も直す。`main-page.js` の `onloadHdr` は触らない。

4. **使われていないものを消す**（プランの 3 点目）:
   - コメントアウトされた `window.addEventListener('resize', ...)`
     （現 101〜105 行）を削除
   - `window.addEventListener('rotationchange', ...)`（現 106〜108 行）を
     削除。`rotationchange` はどのブラウザにも無いイベントで、
     ハンドラは一度も呼ばれていない

5. リスナー登録（`window.addEventListener('load', ...)` 2 つ）は
   `main-page.js` と同じく**ファイル末尾にまとめる**。
   2 つのままでよい（1 つに統合しなくてよい）。挙動を変えない。

## 触ってよいファイル

- `src/ytsched/webroot/static/js/edit-page.js`（新規）
- `src/ytsched/webroot/templates/edit.html`

`src/README.md` の「ブラウザ側のスクリプト」の節に `edit-page.js` を
1 行足すのは可（一覧の並びとファイル名だけ。`.md` が入るので main が
`wording` を回す）。それ以外の文書・コードには手を出さない。

## 範囲外（手を出さない）

- 2 つの `load` リスナーの統合、`changeDetailHeight()` の中身、
  `busyFlag` の扱い、`wdayList` の置き場所
- `edit.html` の `<script>` 以外（HTML 本体、hidden input など）
- TODO-090〜095 の範囲

## 確かめること（自分でも動かす。最終確認は verifier が別に行う）

- `mise run test`（`test_browser.py` 含む。編集画面のブラウザテストは
  無いので、既存が通ればよい）
- `mise run lint` / `mise run typecheck`
- 一時ディレクトリを `--datadir` に指定して `ytsched webapp` を起動し、
  `/edit?date=<日付>` を開いて `edit-page.js` が 200 で返ること、
  ブラウザのコンソールにエラーが出ないこと（可能なら）

## 報告

`archives/agents/TODO-089/implementer-report.md` に。返事は 5 行以内。

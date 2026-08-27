# TODO-089 implementer 報告

## やったこと

挙動は変えていない。`main-page.js`（TODO-083）と同じ形に揃えた。

### 変更・作成したファイル

- **`src/ytsched/webroot/static/js/edit-page.js`（新規）**
  `edit.html` の `<header>` 内インライン `<script>`（旧 24〜116 行）の
  中身を移した。先頭は `main-page.js` と同じ形のコメント
  （`(c) 2026 ytani01` / `// edit.html だけで使う関数・リスナー登録 (TODO-089)。`）。
  - `onloadHdr` → **`onloadEdit`** に改名（`window.addEventListener('load', ...)` の
    登録側も直した）
  - コメントアウトされていた `resize` リスナーを削除
  - `rotationchange` リスナーを削除
  - `load` リスナー 2 つはファイル末尾にまとめた（2 つのまま、統合していない）
  - 全体を 4 スペースぶんディデント（`main-page.js` はトップレベルが桁 0）。
    `onloadEdit` 末尾行にあった行末スペースも落とした。関数・定数の中身は不変

- **`src/ytsched/webroot/templates/edit.html`**
  インライン `<script>` を削除し、`<script src="{{ static_url('js/edit-page.js') }}">`
  だけに差し替えた。テンプレートの値（`{{ }}`）は 1 つも使っていないので
  定数ブロックは作っていない。`base.html` には入れていない

- **`src/README.md`**（依頼書で 1 行追加は可とされた範囲）
  「ブラウザ側のスクリプト」の節。「8 本」→「9 本（TODO-083・TODO-089）」、
  一覧表に `edit-page.js` の行を追加、読み込みの説明を
  「`base.html` が `main-page.js` と `edit-page.js` 以外の 7 本を読む。
  `edit-page.js` は `edit.html` が自分で読む」に更新。冒頭のツリーの
  コメントも「8 本」→「9 本」。`.md` が入るので main が `wording` を回す前提

## 自分で確かめたこと

- `mise run lint` — ruff format / check とも問題なし
- `mise run typecheck` — basedpyright / mypy とも 0 エラー
- `mise run test` — 481 passed / 1 failed。落ちたのは
  `test_browser.py::test_tap_again_stops_auto_page_turn`（TODO-084 の
  自動ページ送り、一覧画面のみ。今回の変更と無関係）。単体で再実行すると
  pass、`test_browser.py` 全 22 件を通しで再実行しても 22 passed。
  `setInterval` に依存するタイミングの揺れと判断
- 一時 datadir で `ytsched webapp` を起動し
  （既定 url prefix `/ytsched`）:
  - `/ytsched/static/js/edit-page.js` が **200**
  - `/ytsched/static/js/main-page.js` も 200（退行なし）
  - `/ytsched/edit?date=2026-08-28` の HTML に
    `<script src="/ytsched/static/js/edit-page.js?v=...">` が入っている
  - 起動したプロセスは全て停止済み

## 単独で決めた判断

- **`src/README.md` の説明文を 1 行でなく数行いじった。** 依頼書は
  「一覧の並びとファイル名だけ」の 1 行追加を可としているが、直後の
  「`main-page.js` 以外の 7 本」「編集画面でも `onloadHdr()` が走る」の
  記述が新事実と食い違うため、そこだけ整合させた。ファイル名・並び以外の
  事実関係は変えていない
- **JS 全体を 4 スペースぶんディデントした。** `main-page.js と同じ形に
  揃える` の指示に沿ったもの。差分は大きく見えるが挙動・字句は不変

## 直さずに残したもの（範囲外）

- `spinner.js` 23 行目のコメント「各ページの `onloadHdr()` が入れている」と
  `gauge.js` 306 行目「`onloadHdr()` と同じく」。編集画面側は `onloadEdit()`
  になったのでコメントが厳密には古い。触ってよいファイルの外なので残した
  （TODO-089 の範囲外。必要なら別項目）
- `main.html` 38 行目のコメントの `onloadHdr()` は一覧画面の話なので正しい。手つかず

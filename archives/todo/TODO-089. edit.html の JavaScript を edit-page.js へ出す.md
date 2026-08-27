# TODO-089. `edit.html` の JavaScript を `edit-page.js` へ出す

|      | main | 担当 |
|------|------|------|
| 見込み | Sonnet 5 / effort medium | implementer + verifier |
| 実施 | Sonnet 5 / effort medium | implementer + verifier |
| 消費 | output 12,627 / cache_creation 202,911 / 概算 $1.3 |
|      | main 56% + implementer 24% + verifier 19%（料金の割合） |

分担の理由と各担当の報告は
[`archives/agents/TODO-089/`](../agents/TODO-089/README.md) にある。

## きっかけ

基本設計のレビュー（2026-08-27）の M。TODO-083 が `main.html` の 120 行を
`main-page.js` へ出したとき、`edit.html` の同種の `<script>`（約 90 行）は
「範囲外」として残していた。`main-page.js` と `edit.html` に `onloadHdr()`
が 1 つずつあり、名前が同じで中身が違った。

## やったこと

**挙動は変えていない。** `main-page.js`（TODO-083）と同じ形に揃えた。

- `src/ytsched/webroot/static/js/edit-page.js` を新規作成し、`edit.html`
  の `<header>` 内インライン `<script>` の中身を移した
  （`wdayList` / `mkInput` / `submitCmd` / `update_wday` / `setElDate` /
  `changeElDate` / `changeDetailHeight` / `onloadEdit`）
- `edit.html` はインライン `<script>` を消し、`<script src>` だけに
  差し替えた。**テンプレートの値（`{{ }}`）を 1 つも使っていない**ので、
  `main.html` のような定数ブロックは要らなかった
- `base.html` には入れていない（`main-page.js` と同じ。入れると編集画面
  以外でも `load` ハンドラが走る）
- `onloadHdr` → `onloadEdit` に改名。`main-page.js` にも同名で中身の
  違う関数があった。同時には読み込まれないので実害は無かったが、
  読む側が混乱するため
- コメントアウトされていた `resize` リスナーと、どのブラウザにも無い
  `rotationchange` イベントのリスナーを削除
- `window.addEventListener('load', ...)` 2 つはファイル末尾にまとめた
  （2 つのまま。登録順は元と同じ）

### 追随した文書・コメント

- `src/README.md` の「ブラウザ側のスクリプト」の節を 8 本 → 9 本にし、
  一覧表と読み込みの説明に `edit-page.js` を加えた
- `spinner.js` の `pageshow` の説明にあった「各ページの `onloadHdr()`」を
  「各ページの `load` ハンドラ（`onloadHdr()` / `onloadEdit()`）」に直した

## テスト

- `mise run lint` / `mise run typecheck` — 問題なし
- `mise run test` — 482 passed（`test_browser.py` の 22 件を含む）。
  verifier が独立に確認
- 一時ディレクトリを `--datadir` にして `ytsched webapp` を起動し、
  `edit-page.js` / `main-page.js` がどちらも 200、`/ytsched/edit` の HTML
  がテンプレート展開済みで旧インライン `<script>` の中身が残っていない、
  サーバのログに例外なし、を確認（verifier）
- 元の `edit.html` の `<script>` の中身と `edit-page.js` を 1 字ずつ
  突き合わせ、差分が先頭コメント・`onloadHdr`→`onloadEdit`・
  `resize`/`rotationchange` の削除・インデントだけであること、
  関数・定数の本体に変更が無いことを確認（verifier）

## 範囲外として残したもの

- 2 つの `load` リスナーの統合、`changeDetailHeight()` の中身、
  `busyFlag` や `wdayList` の置き場所は触っていない
- 編集画面のブラウザテストは元から無い（TODO-056）。新規には書いていない

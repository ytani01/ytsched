# TODO-099 verifier 報告

対象: 未コミットの作業ツリー（develop, origin より 7 commits ahead）。

## 1. fmtjs の冪等性

- `mise run fmtjs` → 終了コード 0。9 ファイルすべて `(unchanged)`。
- 実行後 `git diff --stat src/ytsched/webroot/static/js/` は変化なし
  （9 files, 769 insertions / 733 deletions のまま）。追加差分なし。
- `npx --no-install prettier --check src/ytsched/webroot/static/js` → 終了コード 0
  （`All matched files use Prettier code style!`）。

## 2. lintjs

- `mise run lintjs` → 終了コード 0、出力なし。Prettier 整形後も ESLint と競合なし。

## 3. lint 全体

- `mise run lint` → 終了コード 0。内訳:
  - fmt: ruff format 31 files unchanged / ruff check All checks passed
  - fmtjs: 9 ファイル (unchanged)
  - typecheck: basedpyright 0 errors 0 warnings / mypy Success (28 source files)
  - lintjs: 終了コード 0

## 4. 機械的整形のみか

HEAD 版と作業版を各ファイルごとに
`git show HEAD:<path> | prettier --stdin-filepath <path> --print-width 999` と
`cat <path> | 同上` に通して比較（`--print-width` を 999 にして整形による差を
無くし、意味の違いだけ残す）。

- 9 ファイル中 7 ファイル（edit-page, gauge, keyboard, spinner, state, swipe, week）
  はバイト一致 = 整形のみ。
- main-page.js: 1 か所だけ差。`doPost(url_prefix, { date: ..., search_n: val })` が
  複数行に展開されただけ（Prettier の「元が複数行のオブジェクトリテラルは複数行を保つ」
  挙動）。意味の違いはない。
- nav.js: 同種の差 1 か所。`scrollTo({ left: 0, top: ..., behavior: behavior })` が
  複数行に展開されただけ。意味の違いはない。

個別に見た変更の種類（すべて意味を変えない）:
- インデント 4→2、80 桁での改行位置
- クォート `'`→`"`、末尾カンマ追加、セミコロン
- `! x`→`!x`、`if ( ! x )`→`if (!x)`、`!! (a || b)`→`!!(a || b)`
- `*` と `/` が混在する箇所への明示的なカッコ:
  gauge.js `50.0 * Math.log10(...) / Math.log10(...)` →
  `(50.0 * Math.log10(...)) / Math.log10(...)`、
  gauge.js `abs_xPercent / 50.0 * Math.log10(...)` → `(abs_xPercent / 50.0) * Math.log10(...)`、
  nav.js `d.getTimezoneOffset() / 60 * 3600 * 1000` → `(d.getTimezoneOffset() / 60) * 3600 * 1000`。
  いずれも `*` と `/` は同順位・左結合なので評価順は不変。

ロジック・文字列・条件式が変わった箇所は見つからなかった。

## 5. docs/Developer.md と mise.toml の一致

一致している。
- タスク名 `fmtjs`、コマンド `npx --no-install prettier --write src/ytsched/webroot/static/js`
- `[tasks.lint]` の `depends = ["fmt", "fmtjs", "typecheck", "lintjs"]`、description も同文言
- 技術スタック表に Prettier 行、Node.js の説明を「ESLint・Prettier の実行環境」に更新
- 個別コマンド節に `npx prettier --write src/ytsched/webroot/static/js` 追加

package.json / package-lock.json は prettier 3.9.6 の追加のみ。

## 見つかった問題

なし。

## main の判断が要る点

- 実装者が挙げた `[tasks.fmtjs]` の置き場所（`[tasks.lintjs]` の直前）は好みの範囲。
- `[tasks.fmtjs]` には `wait_for` が無い（`typecheck` は `wait_for = ["fmt"]` 付き）。
  Prettier は `.js` しか触らず ruff format と対象が重ならないので実害は無いが、
  `mise run lint` で fmtjs（書き込み）と lintjs（読み取り）が並列に走る点は認識しておくとよい。
  今回の実行では問題は出なかった。

# TODO-099 implementer 報告

## やったこと

Prettier を導入し、`.js` 9 ファイルを一括整形した。TODO-098（ESLint）の
構成に揃えた。まだコミットしていない。

## 変更ファイル

コミット 1（ツール導入）:

- `package.json` — `devDependencies` に `"prettier": "^3.9.6"` を追加
  （`npm install prettier --save-dev --save-exact=false`）。
- `package-lock.json` — `npm install` の生成物。prettier 3.9.6 の
  エントリが増えただけ。
- `mise.toml` — `[tasks.fmtjs]` を新設（`npx --no-install prettier
  --write src/ytsched/webroot/static/js`、`description = "format
  JavaScript (Prettier)"`）。置き場所は `[tasks.lintjs]` の直前
  （`lintjs` と対にするため。`[tasks.fmt]` と `[tasks.typecheck]` の
  間ではなく、JS 系タスクをまとめた）。`[tasks.lint]` の `depends` を
  `["fmt", "fmtjs", "typecheck", "lintjs"]` に、`description` も
  `"linting (fmt, fmtjs, typecheck, lintjs)"` に更新。
- `docs/Developer.md` — 技術スタックの表に Prettier の行を追加、Node.js
  の説明を「ESLint・Prettier の実行環境」に修正。開発環境の用意の
  「lint（ESLint）には…」を「lint（ESLint）と整形（Prettier）には…」に
  修正。mise のタスク節で `lint` の依存説明に `fmtjs` を追加、タスク
  一覧に `mise run fmtjs` を追加。個別コマンド節に `npx prettier
  --write …` を追加。

コミット 2（一括整形）:

- `src/ytsched/webroot/static/js/` の 9 ファイル全部。
  `git diff --stat` で 9 files changed, 769 insertions(+),
  733 deletions(-)。行数は 1924 → 1960（net +36）。
  中身は機械的差分のみ: 4 スペース → Prettier 既定の 2 スペース
  インデント、80 桁での改行、`! event` → `!event` など。
  ロジックの変更なし（state.js / spinner.js を目視確認、
  他はインデント量の一致で判断）。

## 確認したこと

- `node_modules/.bin/prettier --version` → 3.9.6。
- `mise run fmtjs` → 終了コード 0。2 回目は全ファイル `(unchanged)`
  （冪等）。`npx prettier --check …` も終了コード 0。
- `mise run lintjs`（ESLint）→ 終了コード 0・出力なし。整形後も
  Prettier と ESLint は競合しない（`eslint-config-prettier` 不要を確認）。
- `test` は Python 未変更のため未実行（依頼どおり）。

## 判断が要る点

- `[tasks.fmtjs]` の置き場所を「`[tasks.fmt]` の直後あたり」ではなく
  `[tasks.lintjs]` の直前にした。JS 系タスク（fmtjs / lintjs）を
  隣接させ、「`lintjs` と対になる形」を優先した。問題あれば移動可。

## 残したもの

なし（範囲内で完了）。

# TODO-098. JavaScript のリンター（ESLint）を導入する

|      | main | 担当 |
|------|------|------|
| 見込み | Sonnet 5 / effort medium | implementer + verifier + wording |
| 実施 | Sonnet 5 / effort medium | implementer + verifier + wording |
| 消費 | output 29,454 / cache_creation 236,066 / 概算 $2.0 |
|      | main 73% + implementer 11% + verifier 9% + wording 7%（料金の割合） |

分担の理由と各担当の報告は
[`archives/agents/TODO-098/`](../agents/TODO-098/README.md) にある。

## きっかけ

Python 側は ruff / basedpyright / mypy で見ているのに、`.js`（9 ファイル・
約 1,800 行）は何も見ていなかった。TODO-097 で各ファイルの先頭に
「定義するグローバル / 参照するグローバル」をコメントで書く予定で、
ESLint があれば `/* global */` と `/* exported */` をそのまま解釈し、
`no-undef` と `no-unused-vars` でコメントと実際の依存が食い違ったら
落ちる。TODO-097 より先に入れる（逆だとコメントを確かめる手段が無い）。

## 着手時に決めたこと

`eslint:recommended` を今の 9 ファイルにかけると **159 件**。内訳は
`no-undef` 132、`no-unused-vars` 27 の 2 規則だけで、他の recommended
規則は全部通る。この 159 件は、グローバル関数や `ytState` をファイルを
またいで共有している今の作りそのもの（TODO-083 で ES モジュールに
しないと決めた結果）。

**この 2 規則を `off` にした最小構成で始める。** 有効化は TODO-097 で
`/* global */` / `/* exported */` を入れたあと、別項目で行う。今回は
それ以外の recommended 規則と、`mise run lint` への組み込み・node の
固定を入れるのが目的。

## やったこと

既存の `.js` は 1 行も変えていない。

- `package.json`（新規・ツール専用）: `private` / `type: module` と
  devDependencies（`eslint` / `@eslint/js` / `globals`）。`name` /
  `version` は付けない。
- `package-lock.json`（新規）: `npm install` の生成物。`git check-ignore`
  で `.gitignore` の `*.lock` に当たらないことを確認済み。
- `eslint.config.js`（新規）: `js.configs.recommended` に、`files` を
  `src/ytsched/webroot/static/js/**/*.js` に限定し、`no-undef` /
  `no-unused-vars` を `off` にした設定を足す。`sourceType` は `script`
  （ES モジュールにしていないため）。
- `.gitignore`: `node_modules/` を追加。
- `mise.toml`: `[tools]` 節を新設して `node = "26.8.1"` を固定（今までは
  global の `latest`）。`[tasks.lintjs]`（`npx --no-install eslint …`）を
  追加し、`[tasks.lint]` の `depends` に `lintjs` を足した。
- `docs/Developer.md`: 技術スタックの表に ESLint と Node.js を追加。
  `.js` の lint には `mise install` と `npm install`（CI は `npm ci`）が
  要ることを追記。`lint` の依存の説明と個別コマンドの一覧を更新。

## テスト

verifier が確認（[verifier-report.md](../agents/TODO-098/verifier-report.md)）。

- `npx eslint src/ytsched/webroot/static/js` → 終了コード 0・出力なし
  （9 ファイルが通る）。`git diff --stat` に `static/js/*.js` の変更なし。
- `mise run lintjs` / `mise run lint` → 終了コード 0。ruff /
  basedpyright / mypy の指摘は増えていない。
- `rm -rf node_modules && npm ci` がロックファイルから通り、その後も
  `npx eslint …` が終了コード 0。
- CLI で `--rule '{"no-undef":"error","no-unused-vars":"error"}'` を
  上書きすると 159 件出る（設定が効いている証拠）。
- `node_modules/` は git 管理外、`package-lock.json` は追跡対象。

`mise run test` は、`tests/test_browser.py::test_tap_again_stops_auto_page_turn`
が 3 回中 2 回落ちた（`AssertionError: '2026-09-21' == '2026-09-14'`）。
単独実行は通り、TODO-098 の変更を stash しても揺れたので、自動ページ送りの
タイミング依存テストのフレークと判断した。TODO-098 の変更は
pytest が読むものに触れていない。

# TODO-098 実装依頼（implementer 向け）

JavaScript のリンター（ESLint）を導入する。`TODO.md` の TODO-098 が仕様。
**既存の `.js` は 1 行も直さない。** 設定ファイルとタスクの追加だけ。

## 事前調査の結果（main が実施済み）

- 環境: node v26.8.1 / npm 11.19.0（mise の global `latest`）。ESLint は
  現在の最新 v10.9.1。
- ESLint 10 では `@eslint/js`（`js.configs.recommended` を持つ）が別パッケージ。
  `globals` パッケージも要る。
- 今の 9 ファイルを `eslint:recommended` にかけると **159 件**。内訳は
  `no-undef` 132、`no-unused-vars` 27 の 2 規則だけ。他の recommended 規則は
  全部通る。
- この 159 件は、ファイルをまたいでグローバル関数・`ytState` などを
  共有している今の作りそのもの。`/* global */` と `/* exported */` の
  コメントは TODO-097 で入れる（未着手）。
- **決定（main）: `no-undef` と `no-unused-vars` を `off` にした最小構成で
  始める。** この 2 規則を有効化するのは TODO-097 でコメントを入れたあと、
  別項目で行う。今回はそれ以外の recommended 規則と、lint の仕組み
  （`mise run lint` への組み込み、node の固定）を入れるのが目的。

## やること

### 1. `package.json`（リポジトリ直下・新規）

tooling 専用。最小限にする。

- `"private": true`
- `"type": "module"`（`eslint.config.js` を ESM で書くため）
- `devDependencies` に `eslint` / `@eslint/js` / `globals`（いずれも最新の
  キャレット指定でよい。`npm install --save-dev eslint @eslint/js globals`
  が付ける形のまま）
- `name` / `version` は付けない（`private` なので不要）。`npm init -y` が
  生成する `description` / `main` / `scripts` / `keywords` / `author` /
  `license` などの雛形は消す

### 2. `package-lock.json`（新規）

`npm install` で生成されたものをそのままコミット対象にする
（`.gitignore` の `*.lock` は `*.lock` 末尾のみで `package-lock.json` は
対象外。確認済み）。

### 3. `eslint.config.js`（リポジトリ直下・新規）

```js
import js from "@eslint/js";
import globals from "globals";

export default [
  js.configs.recommended,
  {
    files: ["src/ytsched/webroot/static/js/**/*.js"],
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: "script",
      globals: { ...globals.browser },
    },
    rules: {
      // ファイルをまたぐグローバル共有は今の作り。TODO-097 で
      // /* global */ /* exported */ を入れたあと、別項目でこの 2 つを
      // 有効化する。
      "no-undef": "off",
      "no-unused-vars": "off",
    },
  },
];
```

上のコメント文面はそのまま使わず、`wording` の確認を通す前提で
**普通の言い回し**にすること（「作り」で問題なければそのままでよい）。

### 4. `.gitignore`

`node_modules/` を足す。場所は `.venv/` の近く（"# Virtual environment"
の並び）か、末尾の `## ytsched` 節のどちらか、周りの体裁に合わせて。

### 5. `mise.toml`

- ファイル先頭に `[tools]` 節を新設し、`node = "26.8.1"` を書く
  （今は global の `latest` が使われている。このプロジェクトで固定する）。
- `[tasks.lintjs]` を足す:

  ```toml
  [tasks.lintjs]
  description = "lint JavaScript (ESLint)"
  run = "npx --no-install eslint src/ytsched/webroot/static/js"
  ```

  `--no-install` を付けると、`npm install` していないときに
  「missing packages」で終了コード 1 になる（ネットから取りに行かない）。
- `[tasks.lint]` の `depends` に `"lintjs"` を足す
  （`depends = ["fmt", "typecheck", "lintjs"]`）。

### 6. `docs/Developer.md`

- 「技術スタック」の表に ESLint と node（mise で固定）の行を足す。
- 「開発環境の用意」に、`.js` の lint には別途 `npm install`（または
  `npm ci`）が要ることを書く。node は mise の `[tools]` で入る。
- 「mise のタスク」の節に `mise run lintjs` を足し、`lint` が
  `fmt` / `typecheck` / `lintjs` に依存すると書き換える（今は
  「`fmt` と `typecheck` の両方」とある）。
- 「個別コマンドで実行する場合」に `npx eslint src/ytsched/webroot/static/js`
  を足す。

文面はこのリポジトリの既存の書き方（簡潔・常体）に合わせる。造語を
作らない。

## 確認（実装後、自分で軽く）

- リポジトリ直下で `npx eslint src/ytsched/webroot/static/js` が
  **終了コード 0**（何も出さずに通る）。
- `mise run lintjs` も同じく通る。
- `mise run lint` が通る（`fmt` / `typecheck` も巻き込むが、`.js` 追加は
  Python 側に影響しないはず）。
- `git status` で、新規は `package.json` / `package-lock.json` /
  `eslint.config.js` のみ。`node_modules/` が出ないこと。

## 報告

`archives/agents/TODO-098/implementer-report.md` に書く。返事は5行以内で
「終わったか・報告ファイルのパス・判断が要る点」。

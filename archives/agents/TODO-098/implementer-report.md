# TODO-098 implementer 報告

## 結果

完了。既存の `.js`（9 ファイル）は一切変更していない。設定とタスクの追加のみ。

## 変更・作成したファイル

- `package.json`（新規）: `private` / `type: module` と devDependencies
  （`@eslint/js` `^10.0.1` / `eslint` `^10.9.1` / `globals` `^17.11.0`）。
  `npm install --save-dev` が付けた形のまま。name/version/雛形なし。
- `package-lock.json`（新規）: `npm install` の生成物。先頭に
  `"name": "ytsched"` が入るが npm がディレクトリ名から自動で入れるもので、
  生成物なのでそのままにした。
- `eslint.config.js`（新規）: 依頼書のとおり。`js.configs.recommended` +
  `files` を js ディレクトリに限定、`no-undef` / `no-unused-vars` を `off`。
  コメント文面は「今の構成」「グローバル関数や ytState をファイルをまたいで
  共有」という普通の言い回しにした（wording の確認対象）。
- `.gitignore`: `# Virtual environment` の並びに `node_modules/` を追加。
- `mise.toml`: 先頭に `[tools]` 節を新設し `node = "26.8.1"`。
  `[tasks.lintjs]`（`npx --no-install eslint ...`）を追加。
  `[tasks.lint]` の `description` と `depends` に `lintjs` を追加。
- `docs/Developer.md`:
  - 技術スタックの表に ESLint と Node.js の行を追加。
  - 「開発環境の用意」に `mise install` / `npm install`（CI は `npm ci`）を追記。
  - 「mise のタスク」の説明と一覧に `lintjs` を反映。
  - 「個別コマンドで実行する場合」に `npx eslint src/ytsched/webroot/static/js` を追加。

## 自分で確かめたこと

- `npx eslint src/ytsched/webroot/static/js` → 終了コード 0、出力なし。
- `mise run lintjs` → 終了コード 0。
- `mise run lint` → 終了コード 0（fmt / typecheck も通過。ruff/basedpyright/mypy 変化なし）。
- `git status --short` の新規は `eslint.config.js` / `package.json` /
  `package-lock.json` のみ（と本 archives ディレクトリ）。`node_modules/` は出ない。
  `git check-ignore node_modules` で ignore を確認。

## 単独で決めた判断

- `package-lock.json` の `"name": "ytsched"` はそのまま。npm が生成する値で、
  依頼書は package.json 側の name/version 不要としているだけ。生成物には手を入れない。
- `.gitignore` の追加位置は `.venv/` の直後（"# Virtual environment" の並び）を選んだ。

## 直さず残したもの

- なし（範囲は設定とタスクの追加のみ）。`/* global */` `/* exported */` の
  付与と `no-undef` / `no-unused-vars` の有効化は TODO-097 とその後の別項目の範囲。

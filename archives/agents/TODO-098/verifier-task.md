# TODO-098 確認依頼（verifier 向け）

implementer が ESLint を導入した。実装は
[implementer-report.md](implementer-report.md) を見ること。
**コードは直さない。** 見つけたことは報告するだけ。

## 変更されたもの

- 新規: `package.json` / `package-lock.json` / `eslint.config.js`
- 変更: `.gitignore`（`node_modules/` 追加）/ `mise.toml`（`[tools]` に
  node 固定、`[tasks.lintjs]` 追加、`lint` の `depends` に `lintjs`）/
  `docs/Developer.md`
- 既存の `src/ytsched/webroot/static/js/*.js`（9 ファイル）は無変更のはず

## 確かめること

1. **9 ファイルが通る**: リポジトリ直下で
   `npx eslint src/ytsched/webroot/static/js` が終了コード 0・出力なし。
   `git diff --stat` で `static/js/*.js` に変更が無いことも確認。
2. **`mise run lintjs`** が終了コード 0。
3. **`mise run lint`** が終了コード 0（`fmt` / `typecheck` も巻き込む。
   ruff / basedpyright / mypy の指摘が増えていないこと）。
4. **`mise run test`** が終了コード 0（`lint` → `test` の依存が
   `lintjs` 追加後も通ること。pytest 自体は Python なので影響しないはずだが、
   タスクの依存関係が変わったので 1 回だけ通す）。
5. **`npm ci`** がロックファイルから通ること（`rm -rf node_modules &&
   npm ci` で確認してよい。CI がこの手順を使う）。実行後
   `npx eslint ...` がまだ通ること。
6. **git の混入なし**: `git status --porcelain` の `??` は
   `archives/agents/TODO-098/` と `eslint.config.js` / `package.json` /
   `package-lock.json` のみ。`node_modules/` が出ない
   （`git check-ignore node_modules` で確認）。`package-lock.json` は
   ignore されていない（`git check-ignore package-lock.json` が exit 1）。
7. **`eslint.config.js` の中身**: `no-undef` / `no-unused-vars` が `off`、
   `files` が `src/ytsched/webroot/static/js/**/*.js` に限定されている。
   試しにこの 2 つを一時的に `error` に戻すと 100 件以上出る（＝設定が
   効いている証拠）。確認したら必ず元に戻すこと。

## 報告

`archives/agents/TODO-098/verifier-report.md` に。返事は5行以内で
「終わったか・報告ファイルのパス・判断が要る点」。

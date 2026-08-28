# TODO-099. JavaScript の整形ツール（Prettier）を導入する

|      | main | 担当 |
|------|------|------|
| 見込み | Sonnet 5 / effort medium | implementer + verifier + wording |
| 実施 | Sonnet 5 / effort medium | implementer + verifier + wording |
| 消費 | output 31,595 / cache_creation 188,591 / 概算 $1.7 |
|      | main 65% + implementer 14% + verifier 12% + wording 9%（料金の割合） |

分担の理由と各担当の報告は
[`archives/agents/TODO-099/`](../agents/TODO-099/README.md) にある。

## きっかけ

TODO-098 で ESLint（バグ検出寄り）を入れたが、`.js` の整形は手動の
ままだった。Python 側は `mise run fmt`（ruff format）で自動化済みで、
JavaScript だけ揃っていなかった。

ESLint 10 は整形系ルールを持たない（stylistic は別パッケージに分離）
ので、Prettier とは役割が分かれて競合しない。`eslint-config-prettier`
は要らない。

## 着手時に決めたこと

- 整形タスクは **`fmtjs` として独立**させ、`[tasks.lint]` の `depends`
  に足す（`fmt` は ruff 専用のまま）。`lintjs` と対になる形。既存の
  `lintjs` / `lint` のパターンに揃えた。
- Prettier の設定ファイルは作らない（「オプションを持たない方針」に
  従い既定のまま）。既存 `.js` は 4 スペースインデントだが、Prettier
  既定の 2 スペースに正規化されるのを機械的な差分として許容する。

## やったこと

- `package.json` — `devDependencies` に `"prettier": "^3.9.6"` を追加。
  `package-lock.json` も `npm install` で更新。
- `mise.toml` — `[tasks.fmtjs]`（`npx --no-install prettier --write
  src/ytsched/webroot/static/js`）を新設。JS 系タスクを隣接させるため
  `[tasks.lintjs]` の直前に置いた。`[tasks.lint]` の `depends` を
  `["fmt", "fmtjs", "typecheck", "lintjs"]` に、`description` も
  合わせて更新。`lint` で fmtjs（`.js` に書き込む）と lintjs（読む）が
  並列に走らないよう、`[tasks.lintjs]` に `wait_for = ["fmtjs"]` を
  付けた（`typecheck` の `wait_for = ["fmt"]` と同じ形。verifier の
  指摘による）。
- `src/ytsched/webroot/static/js/` の 9 ファイルを `prettier --write`
  で一括整形（`git diff --stat` で 9 files changed, 769 insertions(+),
  733 deletions(-)。インデント 4→2、80 桁での改行、`! x` → `!x` など
  機械的な差分のみ）。単独コミットにした。
- `docs/Developer.md` — 技術スタックの表に Prettier を追加。Node.js の
  説明を「ESLint・Prettier の実行環境」に修正。`lint` の依存の説明、
  mise のタスク一覧、個別コマンドの一覧を更新。
- `TODO.md` — 直前の TODO-099 を立てたコミット（6b8e706）で
  `## 完了済み` の見出しごと差し替えてしまっていたのを復元。

## テスト

verifier が確認（[verifier-report.md](../agents/TODO-099/verifier-report.md)）。

- `mise run fmtjs` → 終了コード 0、追加の差分なし（冪等）
- `mise run lintjs`（ESLint）→ 終了コード 0・出力なし
- `mise run lint` → 通過（`fmt` / `fmtjs` / `typecheck` / `lintjs`）
- `.js` 9 ファイルの差分が機械的整形のみであることを目視で確認

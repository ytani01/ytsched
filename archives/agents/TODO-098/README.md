# TODO-098 の分担

JavaScript のリンター（ESLint）の導入。設定ファイルの新規追加、`mise.toml`
とドキュメントの変更にまたがるため、実装・確認・文書の 3 工程を分けた。

| 担当 | 役割 | 報告 |
|---|---|---|
| implementer | `package.json` / `eslint.config.js` / `mise.toml` / `docs/Developer.md` の作成・変更 | [implementer-report.md](implementer-report.md) |
| verifier | `mise run lintjs` / `mise run lint` の実行、9 ファイルが通ることの確認 | [verifier-report.md](verifier-report.md) |
| wording | このコミットに入る `.md`（依頼書・報告・`Developer.md`）から前例の無い語を挙げる | [wording-report.md](wording-report.md) |

依頼書は [implementer-task.md](implementer-task.md)。

## 分担の理由

- **implementer を分けた**: 変更が複数ファイル（設定 3 つ・`mise.toml`・
  `Developer.md`）にまたがる。`~/.claude/CLAUDE.md` の「複数のファイルに
  またがる」が目安に当たる。
- **verifier を分けた**: 「9 ファイルが通る設定」という試せる手順がある
  （`~/.claude/CLAUDE.md`「試せる手順があるなら分ける」）。実装者は
  「通るはず」で済ませやすい。
- **wording を入れた**: `.md` が入るコミット（`ytsched/CLAUDE.md` の
  決まり）。

## 着手時に決めたこと

`eslint:recommended` で今の 9 ファイルは 159 件落ちる（`no-undef` 132、
`no-unused-vars` 27 の 2 規則だけ）。この 2 つを `off` にした最小構成で
始める。有効化は TODO-097 で `/* global */` / `/* exported */` を入れた
あと、別項目で行う。

# TODO-099 の分担

## 編成

| 担当 | やったこと | 報告 |
|---|---|---|
| implementer | Prettier の devDependency 追加、`.js` 9 ファイルの一括整形、`mise.toml` の `fmtjs` タスク追加と `lint` への組み込み、`docs/Developer.md` の更新 | [implementer-report.md](implementer-report.md) |
| verifier | `mise run fmtjs` の再現、整形後に差分が出ないこと、`mise run lintjs`（ESLint と競合しないこと）、`mise run lint` の通過を確認 | [verifier-report.md](verifier-report.md) |
| wording | このコミットに入る `.md`（TODO 本文・archives・`docs/Developer.md`・報告ファイル）から、このリポジトリに前例の無い語を挙げる | [wording-report.md](wording-report.md) |

## この分担にした理由

- 複数のファイルにまたがり（`package.json` / `package-lock.json` /
  `mise.toml` / `docs/Developer.md` と `.js` 9 ファイル）、ツール導入・
  タスク定義・文書がまとまって要るので、実装を implementer に分けた。
  直前の TODO-098（ESLint 導入）と構成がほぼ同じで、そのときも
  implementer + verifier + wording だった。
- 整形ツールの導入は「実際に走らせて差分が収束するか」「既存の
  ESLint と競合しないか」を試せる。書式の確認だけでなく再現できる
  手順があるので verifier を分けた（`~/.claude/CLAUDE.md` の基準）。
- `.md` が入るコミットなので wording を立てた（`CLAUDE.md` の決まり）。

# TODO-113. TODO の作業で品質を保ちながらトークンを減らす

|      | main | 担当 |
|------|------|------|
| 見込み | GPT-5.6-sol / effort high | main + verifier |
| 実施 | GPT-5.6-sol / effort high | main + verifier |
| 消費 | 記録不可 | Codex の transcript は `mise run tokens` の対象外 |

## きっかけ

品質を落とさずトークン消費を減らすため、TODO の管理規則へ、依頼・調査・
報告の簡潔な進め方と、担当に応じたモデル選択を加えることにした。

## やったこと

- `~/.claude/CLAUDE.md` に、品質を優先したトークン節約と、担当の難しさに
  応じたモデル選択の規則を加えた
- `wording` は利用者が明示して依頼した場合だけ使うよう、共通規則、
  リポジトリ規則、ワークフロー、skill をそろえた
- Markdown の wording を促す Claude Code と Codex の hook を外し、不要に
  なったスクリプトを削除した
- 確認の分担と結果は
  [archives/agents/TODO-113/README.md](../agents/TODO-113/README.md) を参照

## テスト

- `jq empty .claude/settings.json .codex/hooks.json`
- `rg` で現行規則と矛盾する wording・hook の記述がないことを確認
- verifier が指定した4項目を確認。詳細は
  [verifier-report.md](../agents/TODO-113/verifier-report.md)
- `mise run tokens -- TODO-113` は Codex の transcript を読めず、
  `FileNotFoundError` で集計できなかった

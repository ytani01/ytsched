# TODO-216. Codex 側の担当の定義を Claude 側の 4 担当にそろえる

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort medium | main のみ |
| 実施 | Opus 5.5 / effort medium | main のみ |

| 担当 | モデル | effort | input | output | cache_creation | cache_read | 割合 |
|------|--------|--------|-------|--------|----------------|------------|------|
| main | Opus 5.5 | medium | 10 | 882 | 4,649 | 637,211 | 100% |
| 合計 |  |  | 10 | 882 | 4,649 | 637,211 | 計 642,752 |

- 立てる前の `/claude-api prompt-audit` の分は、範囲の外なので入っていない

## きっかけ

`/claude-api prompt-audit`（2026-10-05）で見つかった。Claude 側の
`runner` / `writer` は TODO-203 で廃止したのに、Codex 側の入口
（TODO-202 で作った）は、存在しない `.claude/agents/runner.md`・
`writer.md` を正本として参照していた。`runner` の手順は
`ruff format`・`ruff check --fix` でファイルを書き換えるもので、
`.claude/agents/verifier.md` の「定型の実行」（書き換えない、TODO-203）
とも食い違っていた。参照先を付け替えず、削除して 4 担当にそろえると
利用者が決めた。

## やったこと

- `.agents/agents/runner.md`・`writer.md` と `.codex/agents/runner.toml`・
  `writer.toml` を削除した
- `.agents/skills/ytsched-workflow/SKILL.md` の検証の節から `runner` を外し、
  verifier の「定型の実行」（ファイルを書き換えない）と動作確認に分けた
- `.agents/agents/implementer.md` の「`grep` で当たりを付けて」を
  `rg -n` に直した

## 確かめたこと

- `rg -n -e runner -e writer AGENTS.md .agents .codex` が何も返さない
  （参照が残っていない）
- `docs/token-usage-analysis.md` の `runner` / `writer` は過去の集計なので
  直していない

# TODO

**残っている項目: TODO-216。** これまでに 215 件を決着させた。
新しく足すときは「完了済み」の上に節を作る。
**番号は `TODO-217` から**。

着手する項目は利用者が指定する。**並び順に優先度の意味は無い。**

---

## TODO-216. Codex 側の担当の定義を Claude 側の 4 担当にそろえる

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort medium | main のみ |

- [ ] `.agents/agents/runner.md`・`writer.md` と `.codex/agents/runner.toml`・
  `writer.toml` を削除する
- [ ] `.agents/skills/ytsched-workflow/SKILL.md` の `runner` の記述を、
  verifier の「定型の実行」に直す
- [ ] `.agents/agents/implementer.md` の「`grep` で当たりを付けて」を
  `rg -n` に直す

`/claude-api prompt-audit`（2026-10-05）で見つかった。Claude 側の
`runner` / `writer` は TODO-203 で廃止したのに、Codex 側の入口
（TODO-202 で作った）は、存在しない `.claude/agents/runner.md`・
`writer.md` を正本として参照している。`runner` の手順は
`ruff format`・`ruff check --fix` でファイルを書き換えるもので、
`.claude/agents/verifier.md` の「定型の実行」（書き換えない、TODO-203）
とも食い違う。参照先を付け替えず、削除して 4 担当にそろえると決めた。

定義ファイルだけを変える項目で、確かめるのは参照が残っていないことと
書式なので、main が確かめる（`rg -n -e runner -e writer AGENTS.md .agents .codex`）。
`docs/token-usage-analysis.md` の `runner` / `writer` は過去の集計なので直さない。

## 完了済み

決着した項目は `archives/todo/` にある（1 項目 1 ファイル）。
一覧は [archives/index.md](archives/index.md)（新しい順）。やらないと決めたものは
ファイル名に（対応しない）が付いていて、理由も書いてある。蒸し返す前に読むこと。

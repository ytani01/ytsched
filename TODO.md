# TODO

**残っている項目: TODO-202。** これまでに 201 件を決着させた。
新しく足すときは「完了済み」の上に節を作る。
**番号は `TODO-203` から**。

着手する項目は利用者が指定する。**並び順に優先度の意味は無い。**

---

## TODO-202. グローバル設定の変更をローカルに反映する

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort medium | main のみ |

- [ ] `.claude/agents/*.md` の 6 ファイルで、返事を「5 行以内」から「短くする」に変える
- [ ] `.claude/agents/reviewer.md` を `model: opus` にする
- [ ] `CLAUDE.md` の「トークン消費量の記録」の料金の段落を、トークン量で書く記述に変える
      （`PRICING` の記述を消し、過去の `$` は直さず互いに比べられることだけ残す）
- [ ] `.agents/agents/*.md` の返事の長さと、`.agents/skills/wording-check` の起動条件
      （利用者 → 管理者（main））を `.claude` 側に揃える

TODO-201（2026-09-27）のあとに `~/.claude` 側で変わった点を反映する。
返事の長さの指定（`~/.claude` の TODO-017）、reviewer のモデル、記録を料金でなく
トークン量で書くこと（`~/.claude` の TODO-015）。`token-usage.py` からは `PRICING` が
消えている。reviewer を opus にすること、`.agents/` も揃えることは利用者と決めた。

文書と定義ファイルだけを変え、確かめるのは書式と記述が揃っているかだけなので
main のみ。定義を直したら Claude Code の再起動が要る（利用者が行う）。
`~/.claude/bin/check-agent-reply.py` は使い捨てのディレクトリで動くため、
ytsched の定義は確かめられない。

---

## 完了済み

決着した項目は `archives/todo/` にある（1 項目 1 ファイル）。
一覧は [archives/index.md](archives/index.md)（新しい順）。やらないと決めたものは
ファイル名に（対応しない）が付いていて、理由も書いてある。蒸し返す前に読むこと。

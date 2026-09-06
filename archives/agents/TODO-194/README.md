# TODO-194 の分担

| 担当 | モデル / effort | 何をさせたか |
|------|-----------------|--------------|
| main | Opus 5 / high | `~/.claude/skills/todo-close/SKILL.md` を書き、そのスキルを使って TODO-194 自身を決着させた |
| verifier | Sonnet 5 / medium | スキルの各手順が書いたとおりに再現できるか、書式が `todo-workflow` に合っているかを確かめた |

## この分担にした理由

書く中身は main がいつもやっている決着の手順そのもので、writer に渡すには
結局その手順を全部書いて渡すことになる（見込みは writer + verifier だったが、
着手時に変えた）。

verifier は外さなかった。完了条件に「実際に使い、手順どおりに進むか確かめる」が
あり、`token-usage.py` や `grep -c` のように**書いたとおりに叩けるコマンド**が
手順に入っているため。書いた本人は「動くはず」で済ませてしまう。

- 報告: [`verifier-report.md`](verifier-report.md)
- 項目: [`../../todo/TODO-194. 項目の決着処理を todo-close スキルにまとめる.md`](../../todo/TODO-194.%20項目の決着処理を%20todo-close%20スキルにまとめる.md)

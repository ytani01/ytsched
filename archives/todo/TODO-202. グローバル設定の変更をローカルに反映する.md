# TODO-202. グローバル設定の変更をローカルに反映する

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort medium | main のみ |
| 実施 | Opus 5.5 / effort medium | main のみ |

| 担当 | モデル | effort | input | output | cache_creation | cache_read | 割合 |
|------|--------|--------|-------|--------|----------------|------------|------|
| main | Opus 5.5 | medium | 20 | 2,804 | 10,805 | 724,011 | 100% |
| 合計 |  |  | 20 | 2,804 | 10,805 | 724,011 | 計 737,640 |

## きっかけ

TODO-201（2026-09-27）のあとに `~/.claude` 側で次の点が変わり、ローカルの設定と
食い違っていた。

- 担当の返事の長さを「5 行以内」から「短くする」に変えた（`~/.claude` の TODO-017）
- reviewer の定義を opus にした
- 記録を料金でなくトークン量で書くようにし、`token-usage.py` から `PRICING` を消した
  （`~/.claude` の TODO-015）
- wording を起動する条件を「利用者」から「管理者（main）」が明示して依頼した場合に変えた

reviewer を opus にすることと、`.agents/` も揃えることは、利用者と相談して決めた。

## やったこと

- `.claude/agents/*.md`（6 ファイル）: 「**返事は 5 行以内**にして」を「**返事は短くして**」に変えた
- `.claude/agents/reviewer.md`: `model: sonnet` を `model: opus` に変えた
- `CLAUDE.md` の「トークン消費量の記録」: `PRICING` と Sonnet 5 の単価の段落を、
  「記録はトークン量で書く。過去の `$` は直さず、互いに比べられる」という記述に変えた
- `.agents/agents/*.md`（6 ファイル）: 返事の長さを `.claude` 側に揃えた。項目を並べて
  いなかった runner・wording・writer には、返事に書く項目を足した
- `.agents/skills/wording-check/SKILL.md`・`ytsched-workflow/SKILL.md`: 起動条件を
  「管理者（main）が明示して依頼した場合」に変えた

## 確かめたこと

- `rg -e '5 行' -e '利用者が明示' .claude .agents` で、該当する箇所が残っていないことを確かめた
- `~/.claude/bin/check-agent-reply.py` は使い捨てのディレクトリで動くので、ytsched の
  定義は確かめられない。定義の読み直しには Claude Code の再起動が要る

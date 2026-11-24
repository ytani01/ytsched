# TODO-236. 担当の定義に、TODO-214 のあとに全体へ足された決まりを入れる

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort medium | main のみ |
| 実施 | Opus 5.5 / effort medium | main のみ |

| 担当 | モデル | effort | input | output | cache_creation | cache_read | 割合 |
|------|--------|--------|-------|--------|----------------|------------|------|
| main | Opus 5.5 | medium | 16 | 2,941 | 9,466 | 570,909 | 100% |
| 合計 |  |  | 16 | 2,941 | 9,466 | 570,909 | 計 583,332 |

- `check-agent-reply.py` が別プロセスで起動した `claude -p`（reviewer の 1 回）は、この集計に入っていない

## きっかけ

利用者から「全体ルールに合わせて、ローカルルールを調整して」と頼まれた。
`.claude/global-rules-seen` は今の版（105）と同じで、未確認の全体ルールの
変更は無かった。ただ、ytsched の `.claude/agents/` は `~/.claude/agents/` を
全文で置き換えるので、TODO-214 のあとに全体の定義と `~/.claude/CLAUDE.md` に
足された決まりが届いていなかった。取り込む範囲は利用者が 4 点を選んだ。

## やったこと

- `reviewer.md`: 「見るもの」に文書との整合を足した。「報告に書くこと」に、
  「挙動を変えない」項目では変わった点をすべて要修正にすること、境界線上の
  判断をせず「実害は未確認」と添えて報告することを足した
- `implementer.md`: 規約や依頼で答えが決まる点を「判断が要る点」に入れず、
  どの規約によるかを書いて進めるようにした
- `verifier.md`: 境界線上の判断をしないことを足した
- 4 つすべて: SendMessage が道具に無ければ呼ばず、終わったときの返事で伝える

変えなかったもの: verifier の「原因の切り分けをしない」と wording の役割
（TODO-214 で残すと決めた）。

## 確かめたこと

- `git diff --stat` で、変わったのが `.claude/agents/` の 4 ファイルだけ、
  frontmatter には触れていないこと
- `~/.claude/bin/check-agent-reply.py --agent reviewer --project .` が「合格」（返事は 1 行）
- 定義は Claude Code の再起動まで、このセッションには効かない（再起動は利用者）

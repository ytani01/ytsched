# TODO-203 の分担

| 担当 | モデル | 担当したこと |
|------|--------|--------------|
| main | Opus 5.5 / high | 定義の統合（implementer・verifier・`CLAUDE.md`、runner・writer の削除） |
| reviewer | Opus 5.5 / high | 変更後の定義が `~/.claude/CLAUDE.md` と `todo-workflow` skill に食い違っていないか |

変わるのは定義ファイルと `CLAUDE.md` の文言だけで、書いたとおりに試せる手順は無い。
`~/.claude/bin/check-agent-reply.py` は使い捨てのディレクトリで動くので、ytsched の
定義は測れない（TODO-202）。そのため verifier は立てず、reviewer だけを付けた
（利用者が決めた）。

- [reviewer-report.md](reviewer-report.md)

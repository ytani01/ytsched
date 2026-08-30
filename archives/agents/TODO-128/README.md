# TODO-128 の分担

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort medium | main + verifier |
| 実施 | Opus 5 / effort medium | main + verifier |

## なぜこの分担にしたか

文書の書き分けそのものは、README・`docs/` 全体の見通しを持っている
main がやったほうが早い（implementer に渡すと、どこへ何を移すかを
書き写す手間のほうが大きい）。一方、書いた内容が実装と合っているか、
リンクが切れていないか、移した内容に抜けが無いかは、書いた本人では
「合っているはず」で済ませてしまうので verifier に分けた。

## 報告

- [verifier-report.md](verifier-report.md)

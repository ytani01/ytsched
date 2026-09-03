# TODO-180 の分担

| 担当 | 受け持ち | 報告 |
|------|----------|------|
| main | 調査（症状の再現と境界の実測）・`gauge.js` の実装・テストの追加 | — |
| verifier | lint / pytest の実行、playwright での実測 | [verifier-report.md](verifier-report.md) |

依頼の内容は [verifier-request.md](verifier-request.md)。

## この分担にした理由

触るのは `gauge.js` 1 ファイルとテストだけで、実装を分けるほどの量では
ない（`~/.claude/CLAUDE.md` の「複数のファイルにまたがる」に当たらない）。
一方、直したかどうかは**ブラウザで動かさないと分からない**種類なので、
確認は分けた。TODO-179 で「実装した本人がテストの通過だけを見て渡し、
直り切っていなかった」ことが起きたばかりでもある。

reviewer は入れていない。分岐そのものは減る方向の変更で、挙動の変わる
経路も playwright で全部たどれるため。

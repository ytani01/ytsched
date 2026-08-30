# TODO-126 の分担

| 担当 | 依頼 | 報告 |
| --- | --- | --- |
| implementer | [implementer-request.md](implementer-request.md) | [implementer-report.md](implementer-report.md) |
| verifier | [verifier-request.md](verifier-request.md) | [verifier-report.md](verifier-report.md) |

## この分担にした理由

新しいモジュール・新しい CLI サブコマンド・テスト・テストデータ・文書が
まとまって要る項目なので、実装を `implementer` に分けた。

確認を `verifier` に分けたのは、**実際に叩かないと分からないことが多い**
ため。CP932 の CSV が読めるか、`--dry-run` で本当にファイルが増えないか、
2 回走らせても二重に登録されないか、本物のネットからの取得が動くかは、
テストが通ることを見ても分からない。実装した本人は「動くはず」で済ませて
しまう。

`reviewer` は入れなかった。既存のコードを一切触らず、追加だけの項目で、
挙動や分岐が変わるところが無いため。

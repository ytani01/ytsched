# TODO-027 の分担

項目は
[TODO-027. 不正な入力で 500 になるのをやめる](../../todo/TODO-027.%20不正な入力で%20500%20になるのをやめる.md)。

## 誰に何を担当させたか

実装 → 確認 → レビューを 4 回まわした。

| 回 | implementer | verifier | reviewer |
|---|---|---|---|
| 1 | [依頼](implementer-request.md) / [報告](implementer-report.md) | [依頼](verifier-request.md) / [報告](verifier-report.md) | [依頼](reviewer-request.md) / [報告](reviewer-report.md) |
| 2 | [依頼](implementer-request2.md) / [報告](implementer-report2.md) | [依頼](verifier-request2.md) / [報告](verifier-report2.md) | [依頼](reviewer-request2.md) / [報告](reviewer-report2.md) |
| 3 | [依頼](implementer-request3.md) / [報告](implementer-report3.md) | [依頼](verifier-request3.md) / [報告](verifier-report3.md) | [依頼](reviewer-request3.md) / [報告](reviewer-report3.md) |
| 4 | [依頼](implementer-request4.md) / [報告](implementer-report4.md) | [依頼](verifier-request4.md) / [報告](verifier-report4.md) | 入れていない |

## その分担にした理由

- **reviewer を入れたのは、挙動と分岐がまとめて変わるから。**
  TODO-017 で決めた基準どおり。3 回とも実質的な指摘を出した
- **4 回目に reviewer を入れなかったのは、3 回目の reviewer 自身が
  推した案をそのまま実装したから**（利用者の判断）。verifier が 400・
  データ不変・正しい操作の 3 つを確かめている
- **verifier は毎回分けた。** curl で実際に叩く手順があるので、
  「書式の確認だけなら main」には当たらない

## この項目で分かったこと

- **`git checkout -- src` の事故。** 3 回目の implementer が未コミットの
  実装を一度消した。以降の依頼書には「作業ツリーを戻すコマンドは
  絶対に使わない」と明記し、4 回目の reviewer には「1・2 回目の実装が
  欠けていないか」まで確かめさせた（欠けていなかった）
- **verifier が、担当した項目の外の不具合を報告してきた。**
  3 回目の確認で「`pytest` が 1 件も実行できない」。これが
  [TODO-033](../../todo/TODO-033.%20URL_PREFIX%20の改名に追随できていない箇所を直す.md)
  になった
- **判断を早く聞けば往復が減った。** 「読めない日付を 400 にするか、
  今日へ寄せるか」は、項目を立てる時点で聞ける種類の判断だった

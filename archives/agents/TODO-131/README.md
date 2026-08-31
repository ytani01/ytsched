# TODO-131 の分担

| 担当 | 範囲 | 報告 |
|---|---|---|
| main | CSS の 2 箇所（`.my-mini-cal-dot` / `.my-mini-cal-sq`）、試作の撮影 | — |
| verifier | 差分の確認、セルへの収まり、背景色の回り込み、lint / test | [verifier-report.md](verifier-report.md) |

CSS の値を直すだけなので、実装は main で足りると判断した。見た目は
試作を撮って利用者が選んだので、verifier には目視を頼まず、差分と
数値の確認・lint / test に絞った。挙動や分岐は変わらないため
reviewer は入れていない。

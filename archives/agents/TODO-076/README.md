# TODO-076 の分担

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort medium | verifier + wording |
| 実施 | Opus 5 / effort medium | verifier + wording |
| 消費 | output 11,327 / cache_creation 108,982 / 概算 $1.4 |
|      | main 81% + verifier 13% + wording 6%（料金の割合） |

## なぜこの分担にしたか

置換そのものは `sed` 1 回で、判断が要らない。実装まで分けると依頼書を
書く手間のほうが大きいので、**実装は main**。

一方、機械置換は「直し漏れ」と「片側だけ直って壊れる」（CSS クラスと
HTML、Jinja 変数とテンプレート、JS の id 参照）が起きやすく、書いた本人
には見えにくい。項目の規模によらず確認は分ける決まりでもあるので、
**verifier** を立てて lint・テスト・起動確認と、両側の突き合わせを
任せた。

`.md` が入るコミットなので **wording** も立てた。

## 報告

- [verifier-report.md](verifier-report.md) — 不具合なし
- [wording-report.md](wording-report.md) — 前例の無い語 3 語、いずれも
  造語ではないと判断

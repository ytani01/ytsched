# TODO-080 の分担

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort high | implementer + verifier + reviewer |
| 実施 | Opus 5 / effort high | implementer + verifier + reviewer |
| 消費 | output 13,307 / cache_creation 203,060 / 概算 $5.1 |
|      | main 69% + verifier 13% + reviewer 8% + implementer 7% + wording 4%（料金の割合） |

## なぜこの分担にしたか

キャッシュの返し方が変わる＝**挙動が変わる**項目なので reviewer を
立てた（`CLAUDE.md` の基準）。`ytsched.py` とテストにまたがるので
実装も分けた。

verifier には、**サーバを動かしたまま外からファイルを書き換える**
という、テストでは書きにくい手順を任せた。この項目の元の動機
（`ytsched migrate` のあと再起動しないと見えない）もそこで確かめている。

## 報告

- [implementer-report.md](implementer-report.md) — 実装。
  末尾に main の追記あり（報告と実際のコードが違うところ）
- [verifier-report.md](verifier-report.md) — 6 項目すべて不具合なし
- [reviewer-report.md](reviewer-report.md) — 指摘 1 件。
  **足したテストが狙った退行を捕まえられない**（見るのが遅く、
  `save()` 直後の 1 回目の読み直しを見逃していた）。
  main が書き直し、実装を戻すと落ちることを実際に確かめた

## main が実装から変えたところ

- `DEF_CACHE_SIZE` を 1500 → **2000**。実装者は `LoadMonths` の上限
  （1450 日）を根拠にしたが、検索モードは 1 件も当たらないと最大
  1825 日ぶん開きうる。実装者自身が「範囲外の話」として書いていたので、
  大きいほうに合わせた

# TODO-054 の分担

項目は [TODO-054. 左右のスワイプで週を送る](../../todo/TODO-054.%20左右のスワイプで週を送る.md)。

## 誰に何を担当させたか

| 担当 | 何を | 報告 |
|------|------|------|
| main | 実装（`my.js` と `main.html`）、変更の前後のキャプチャ | — |
| verifier | 決まった手順、playwright での操作確認 | [verifier-report.md](verifier-report.md) |
| reviewer | 判定の条件と状態の持ち方、既存のコードとの整合 | [reviewer-report.md](reviewer-report.md) |
| wording | このコミットに入る `.md` 全部の語 | [wording-report2.md](wording-report2.md) |

依頼書は [request-verifier.md](request-verifier.md)、
[request-reviewer.md](request-reviewer.md)、
[request-wording.md](request-wording.md)。

`.md` の語の確認は 2 回立てた。[wording-report.md](wording-report.md) が
項目を立てたときの分、[wording-report2.md](wording-report2.md) が
着手して済ませたときの分。

## なぜこの分担にしたか

- **実装は main のみ。** 触るのは `my.js` の末尾と `main.html` の
  登録の 2 か所で、複数のファイルにまたがる設計の判断が要らない。
  実装の担当を分ける目安（複数のファイル、実装とテストと文書が
  まとまって要る）に当たらない
- **verifier は分けた。** タッチのスワイプは手で押して確かめられず、
  CDP でイベントを組み立てる手順がある。「試せる手順があるなら分ける」
  に当たる（TODO-017）。実際、ピンチでブラウザ自体がズームすることは
  main の確認では出ていなかった
- **reviewer も入れた。** 判定の条件（距離・比・時間・画面端）を
  新しく決める項目で、挙動が変わる。「挙動や分岐が変わる項目には
  入れる」に当たる（TODO-017）

## 出てきたもの

- **verifier**: 決まった手順はすべて通過。依頼した確認はすべて OK。
  判断が要る点として「ピンチでブラウザ自体がズームする」を報告
  → **止めないと決めた**（このアプリはピンチでの拡大を意図して
  許してある。TODO-039）
- **reviewer**: 確信度の高い指摘は無し。中程度の指摘 1 件
  （`touchMoveHdr` の説明が `touchStartHdr` の動きを書いている）
  → **直した**。確信度の低い指摘 2 件（`SWIPE_MAX_MSEC` と
  `SWIPE_EDGE_PX` の値）→ **今は変えない**（理由は項目のファイル）
- **wording**: 前例の無い語が 9 語。**どれもそのままにした**。
  「ピンチズーム」「バブリング」「フルナビゲーション」「防御コード」は
  一般に通用する専門用語で、このリポジトリで初出なだけ。「払う」
  （スワイプの意味）「収束」「縦優勢」は普通の日本語。「二重の確認」と
  「二重チェック」の揺れは、報告ファイルの中に留まっている

# TODO-029 の分担

項目そのものは
[`archives/todo/TODO-029. コードレビューで見つかった 3 件を直す.md`](../../todo/TODO-029.%20コードレビューで見つかった%203%20件を直す.md)。

見込み: main = Opus 5 / effort high、担当 = implementer + verifier + reviewer
実施: main = Sonnet 5 → Opus 5（途中で切り替え）/ effort high、担当 = implementer + verifier + reviewer

## この分担にした理由

- **implementer を分けた。** `src/` の 4 ファイル、テンプレート 1 つ、
  文書 2 つ、テスト 3 ファイルにまたがる。「複数のファイルにまたがる、
  実装とテストと文書がまとまって要る」の目安に当てはまる
- **verifier を分けた。** 試せる手順（一時ディレクトリでサーバを起動して
  `migrate` と編集画面と検索を動かす）があるので、書式の確認だけでは
  済まない
- **reviewer を入れた。** 3 件とも挙動が変わる（`\r` を落とす位置、
  `orig_date` の決め方、`Conf.cgi` へ保存する値）。「挙動や分岐が変わる
  項目には入れる」に当てはまる

## 各担当の報告

| ファイル | 中身 |
| --- | --- |
| [`implementer-request.md`](implementer-request.md) | main から implementer への依頼書 |
| [`implementer-report.md`](implementer-report.md) | 変更したファイルと、判断したところ 3 点 |
| [`verifier-report.md`](verifier-report.md) | テスト 402 件・lint・型チェックと、実地での再現 |
| [`reviewer-report.md`](reviewer-report.md) | 判断 2 点の見立てと、テスト・文書への指摘 3 件 |

## 依頼書と実装の食い違い（行の途中の `\r`）

[`implementer-request.md`](implementer-request.md) は
「旧コードは `\r` を**全部**消していた（行末だけではない）。同じにする」と
書いているが、**実装は行末だけ**を落としている。

原因は main の側にある。着手時に依頼書を書き直したつもりで、
**コミット済みの依頼書を短縮版で上書きしてしまい**、implementer が
受け取ったのは「各行の最後のフィールドに `\r` が残らないように」という
行末だけの指示だった（依頼書はその後もとに戻した）。

**結果としては、行末だけでよいと判断した。** reviewer の見立てのとおり、
行の途中に `\r` が残るのは「detail に単独の CR が入っている」場合だけで、
そのとき旧実装（テキストモードの `readlines()`）では**その `\r` で行が
割れていた**ので、全部消してもどのみち旧形式とは結果が違う。

## この項目で分かったこと

**reviewer の指摘 1 が効いた。**
`assert all("\r" not in json.dumps(d) for d in data)` は、`json.dumps()` が
CR を `\r` の 2 文字へエスケープするので**常に通る**。implementer が
「実装を戻すと落ちることを確認済み」と書いていた（落ちていたのは 1 つ上の
`detail ==` の assert）ので、**テストが通ることを見ても出てこない種類の
指摘**。同じ理由で、implementer の「`od -c` で `\r` が無いことを確認」も
確認になっていなかった。

verifier は不具合を見つけなかったが、implementer が挙げた 3 点を独立に
再現しており、reviewer とは別の役目を果たしている。

指摘 3 件はすべて main が直した（テスト 2 か所と `src/README.md` 1 か所）。

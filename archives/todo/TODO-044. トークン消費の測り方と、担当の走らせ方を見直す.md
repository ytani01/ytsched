# TODO-044. トークン消費の測り方と、担当の走らせ方を見直す

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort medium | implementer + verifier + reviewer + wording |
| 実施 | Opus 5 / effort medium | implementer + verifier + reviewer + wording |
| 消費 | output 25,459 / cache_creation 344,334 / 概算 $4.5 |
|      | main 77% + implementer 8% + reviewer 6% + wording 4% + verifier 4%（料金の割合） |

分担の理由と各担当の報告は
[archives/agents/TODO-044/](../agents/TODO-044/README.md) にある。

## きっかけ

アーカイブ済み 13 件の消費の行を transcript から取り直したところ、**消費の行が
測っているものと、実際に多く使っているものがずれていた。**

料金で見ると `cache_read` が 6〜7 割を占める（TODO-038 で 72%、TODO-042 で
59%、TODO-043 で 67%）。`cache_read` は「リクエスト数 × そのときのコンテキスト
長」で決まる。TODO-038 の implementer は 244 リクエストで 1 回あたり平均
222,000 トークン、verifier は 320 リクエストで平均 99,000 だった。

担当ごとの割合も、消費の行と料金で食い違っていた。TODO-038 の reviewer は
消費の行では 6%、料金では 1%。wording は 5% に対して 1%。担当を減らす方向では
減らず、減るのは 1 担当あたりのリクエスト数と、1 回に読ませるファイルの
量を絞ったとき。

集計そのものにも取りこぼしがあった。サブエージェントの transcript には同じ
リクエストの usage が途中経過と最終値の両方で記録されていて、`collect()` は
先に出会った行（途中経過）を採っていた。

## やったこと

### `tools/token-usage.py`（implementer）

- **同じ `(requestId, message.id)` の行は、各項目の最大値を採る**ように
  直した。行の並びが最終値を後に置くとは限らないので、上書きではなく最大値で
- **概算料金を出すようにした。** 単価（$/1M トークン）を `PRICING` に持たせ、
  `message.model` の前方一致で引く。cache write は input の 1.25 倍、
  cache read は 0.1 倍。表に無いモデルは警告を出して Opus 5 の単価で数える
- **担当ごとの割合と並び順を、トークン数から料金に変えた。** 表に `$` の列を
  足し、`消費:` の行を 2 行に分けた

単価は Opus 5 が $5/$25、Sonnet 5 が $2/$10、Haiku 4.5 が $1/$5。
**Sonnet 5 の $2/$10 は 2026-08-31 までの導入価格**で、そのあとは $3/$15 に
なる。期限はコードのコメントに書いてある。

### 担当の定義（main）

`~/.claude/CLAUDE.md` の消費の行を 2 行の形にし、`cache_read` はトークン数
としては書かないが料金には入れることを書いた。

- `.claude/agents/verifier.md` — 「依頼に書かれた確認だけをやる」を足し、
  確認の型は「依頼が指定していないときだけ、多くて 2〜3 個」に変えた。
  報告は 60 行以内、通ったときの出力は貼らない。ファイルは `grep` で
  当たりを付けてから範囲を切って読む
- `.claude/agents/implementer.md` — 同じ読み方に加え、`fmt` / `lint` /
  `test` は一通り直してからまとめて 1 回、報告に diff やファイルの中身を
  貼らない

### reviewer の指摘で直したところ（main）

- `Usage.cache_read` / `input` の docstring が「(参考)」のままで、料金の
  計算に使うようになった実態とずれていた
- `price_for()` の前方一致が `PRICING` の書いた順に依存していた。
  **いちばん長く一致したものを採る**ようにした

reviewer の指摘は 2 件とも「実害は無い」付きだったが、どちらも直した。

`collect()` の直しで増えた分は、立てたときの読みより小さかった。TODO-043 の
verifier の `output` は 654 → 1,176 で、2,000〜3,000 を見込んでいた。同じ
項目の `cache_creation` 193,102 に対しては、どちらにしても誤差の範囲。

## テスト

- `mise run lint`（`ruff format` / `ruff check` / `basedpyright` / `mypy`）
  と `mise run test`（418 件）が通ることを verifier が確認した
- TODO-043 と TODO-038 で実際に集計し、消費の行の形、割合の合計、料金順の
  並び、`--list` を確認した。TODO-043 の verifier の 1 レコードについて、
  料金を手計算して突き合わせた
- 表に無いモデル名（実データに `<synthetic>` があった）で、警告が出て
  Opus 5 の単価で数えられることを確認した

## やらなかったこと

- **担当のモデルを下げる案。** すでに全部 Sonnet か Haiku で、下げても
  トークン数は変わらず単価しか動かない
- **main の effort を見込みどおりから始める件。** 運用で気をつける話で、
  ファイルを変える話ではない
- **`CLAUDE.md` に測った結果そのものを残すこと。** この項目ではやらないと
  決めていた

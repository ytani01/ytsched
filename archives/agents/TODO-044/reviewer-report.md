# TODO-044 reviewer 報告

対象は `tools/token-usage.py` の diff（依頼書に挙げられた 5 点）。

実データ（`~/.claude/projects/-home-ytani-work-ytsched/` の transcript）を
使って、依頼書の懸念点を実測で確かめた。

## 確信度の高い指摘

無し。依頼書の 5 点はすべて妥当だった。確かめた内容は次のとおり。

### 1. `collect()` の最大値集計

サブエージェントの transcript（2026-08-20 以降、200 ファイル）を集計すると、
同じ `(requestId, message.id)` の行が 1425 組あり、うち 94 組で値が変化
していた。変化するのは常に `output` だけで（例:
`req_011CeMJmUsUv1MHnWQWwkjW4` は `2 → 220 → 220`）、`cache_creation` /
`cache_read` / `input` は同じ key 内で一定だった。`output` は途中経過から
最終値へ単調に増えるとは限る保証が無い前提で `max()` を取る実装は理にかない、
今回の実データでも矛盾は無かった。`messages` を 1 のままにする扱いも、
変更前から「重複した行を 1 件として数える」という前提と揃っている。

`(requestId, message.id)` が `(None, None)` になって別リクエストを
まとめてしまわないか、についても確かめた。親セッションの transcript
（2026-08-01 以降、usage を持つ行 2,152 件）では、`requestId` が欠けている
行が 4 件あったが、いずれも `message.id` は存在し、両方 `None` になる行は
0 件だった。理論上はあり得る懸念だが、実データでは起きていない
（下の「確信度が低い指摘」にも書く）。

### 2. 料金の計算

`record_cost()` は `output×output_price + input×input_price +
cache_creation×input_price×1.25 + cache_read×input_price×0.1` を
1,000,000 で割っている。依頼書の 4 点（1.25 倍・0.1 倍・input を数える・
output に出力単価）をすべて満たしている。verifier 報告にある手計算
（TODO-043 verifier の最終レコード）でも一致が確認されており、
自分でも同じ式で再計算し一致を確認した。

### 3. `price_for()` の前方一致

`PRICING` の現在のキー（`claude-opus-5` / `claude-sonnet-5` /
`claude-haiku-4-5`）は互いに前方一致しないので、今のところ誤って
別モデルの単価を引くことは無い。実データ（TODO-038）に出てきた
`<synthetic>` という未知モデルも、フォールバック（Opus 5 の単価 +
警告 1 回）どおりに動いていた。

### 4. `fmt_shares()` / `sum_by()` の料金基準化

`fmt_shares()` は `total.cost <= 0` でガードしており、料金が 0 のときに
ゼロ割で落ちることは無い。`sum_by()` のソートキーも `cost` に変わっており、
表・割合とも料金の多い順になっている。

### 5. 既存の書き方との整合

`Usage.add()` に `cost` の合算を足しているが、`Usage` の他フィールドと
同じパターンで書かれている。ログは `_log.warning()` を使っており
`docs/Developer.md` の方針（`mylog.py` のラッパ）どおり。`main_total` の
削除後、他のファイル（`.py` / `.md`）に参照が残っていないことも
`grep -rn "main_total"` で確認した。

## 確信度が低い指摘

- **`Usage.input` / `Usage.cache_read` の docstring が「(参考)」のまま。**
  `tools/token-usage.py:275-276`（`input`）と `272-273`（`cache_read`）。
  この変更前は `main_total`（`output + cache_creation`）だけが主指標で、
  `input` / `cache_read` は表示上の参考値だった。今回の変更で両方とも
  `cost` の計算に組み込まれ、`cost` が新しい主指標として割合・並び順に
  使われるようになった。「参考」というラベルは、値そのものが今も
  補助的な表示（`output` / `cache_creation` のように単独では出さない）
  という意味では間違っていないが、「集計に使われない」という含みが
  あるなら実態とずれている。実害は無い記述上の点
- **`price_for()` の前方一致は、キーの挿入順に依存する設計。**
  `tools/token-usage.py:317-319`。現在の 3 キーは互いに前方一致しない
  ので今は問題ないが、将来 `PRICING` に前方が重なるキー（例:
  `claude-opus-4` と `claude-opus-4-5`）を足すと、辞書の挿入順で先に
  当たったほうが勝つ。挿入順を意識せずに追記すると誤って引く余地がある。
  今回の変更範囲では実害は無い

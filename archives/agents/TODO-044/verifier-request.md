# TODO-044 verifier への依頼

`TODO.md` の TODO-044 の節と、
`archives/agents/TODO-044/implementer-report.md` を読んでから始めること。

対象は `tools/token-usage.py` の変更だけ。**下の 4 つだけを確かめる。**
思いついた確認を足さない（足りないと思ったら、やらずに報告へ書く）。

## 1. 一通り通るか

`mise run lint` と `mise run test` を **1 回ずつ**走らせる
（`mise run upgradeproject` は走らせない）。件数と結果を報告する。

## 2. 集計が過去の項目で動くか

`uv run python tools/token-usage.py` を **TODO-043 と TODO-038 の
2 件**で走らせ、出力をそのまま報告に貼る（この 2 件だけは全文でよい）。
見るのは:

- 「消費:」が 2 行になっていて、1 行目に `output` / `cache_creation` /
  `概算 $…`、2 行目に `担当 NN% + …（料金の割合）` が出ているか
- 担当ごとの割合の合計が 100%（四捨五入の分だけずれるのは可）
- 表に `$` の列が出ていて、担当の表・モデルの表とも料金の多い順に
  並んでいるか
- **料金の桁が妥当か。** 表の各行について、`(input + cache_creation ×
  1.25 + cache_read × 0.1) × 入力単価 + output × 出力単価` を 1M
  トークンあたりで手計算し、`$` の列と合うことを 1 行だけ確かめる
  （どの行を選んだかを書く）

単価は Opus 5 が $5/$25、Sonnet 5 が $2/$10、Haiku 4.5 が $1/$5
（$/1M トークン）。

## 3. 未知のモデル名

`PRICING` に無いモデル名に当たったとき、警告が出て Opus 5 の単価で
数えられるか。`python -c` で `price_for()` を直接呼んで確かめてよい。

## 4. `--list`

`uv run python tools/token-usage.py --list` が動くか。1 行で報告。

## 決まりごと

- **コードを直さない。** 見つけたことは報告に書く
- 報告は `archives/agents/TODO-044/verifier-report.md`。
  **60 行以内**（2 の出力 2 件はこの数に含めない）。返事は 5 行以内

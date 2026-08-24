# TODO-044 verifier 報告

対象は `tools/token-usage.py` のみ。依頼書の 4 項目だけ確認した。

## 1. 一通り通るか

- `mise run lint` … `ruff format`（23 ファイル変更なし）、`ruff check`
  「All checks passed!」、`basedpyright` 0 errors/warnings/notes、
  `mypy` 「Success: no issues found in 20 source files」 ○
- `mise run test` … 418 件 pass ○

## 2. 過去 2 件での集計

出力は別途貼付（TODO-043・TODO-038、全文）。

- 「消費:」が 2 行 ○。1 行目に `output` / `cache_creation` / `概算 $…`、
  2 行目に `担当 NN% + …（料金の割合）` が出ている ○
- 割合の合計: TODO-043 は 71+25+3+0=99%（四捨五入によるずれ、許容範囲）、
  TODO-038 は 43+37+18+1+1=100% ○
- 表に `$` 列があり、TODO-043・TODO-038 とも「担当」表・「モデル」表の
  両方で料金の多い順に並んでいる ○
- 手計算で桁を確認した行: TODO-043 verifier の最後のレコード
  （`input=2, cache_creation=92116, cache_read=7767, output=1`、
  `claude-sonnet-5` = $2/$10）。
  `(2 + 92116×1.25 + 7767×0.1) × 2/1e6 + 1×10/1e6`
  `= 115923.7 × 2/1e6 + 0.00001 = 0.231857…`
  → スクリプトの内部値 `0.2319` と一致 ○
  （このレコードの `input`/`cache_creation`/`cache_read`/`output`/`cost`
  は `collect()` を直接呼んで取得した）

TODO-038 は「立てる」コミットが無く（`TODO-037・038・039` を一括で
`docs(todo): add TODO-037,038,039` に足していた）、`find_start` が
見つけられず終了コード 1 になった。`--since '2026-08-23 21:25:24'`
（その一括コミットの日時）を指定してやり直し、正常に出力された。
これは仕様どおりの挙動（依頼で想定されていた「立ててから着手まで空いた
項目」のケース）であり、`token-usage.py` の不具合ではない。

TODO-038 の実行では実データに `<synthetic>` という未知モデル名が出て
おり、`price_for()` の警告・フォールバックが実データでも動くことを
併せて確認できた（下記 3 とも符合）。

## 3. 未知のモデル名

`price_for('claude-mystery-9')` を同一プロセス内で 3 回呼んだところ、
戻り値は 3 回とも Opus 5 の単価 `(5.0, 25.0)` で、警告ログは 1 回だけ
出力された ○。プロセスを分けて呼ぶと警告は毎回出る（`_warned_models`
がプロセス内の状態のため。依頼書に厳密な指定は無く、実装報告にも
同じ説明があった）。

## 4. `--list`

`uv run python tools/token-usage.py --list` は正常に一覧を出力した
（TODO-044〜TODO-025 まで、始点・終点の日時が並ぶ）○。1 行で報告終わり。

## 見つかったこと

不具合ではないが、TODO-038 は始点コミットが無いため `--since` 指定が
必須（依頼書どおりの想定内の挙動）。

---

## 付録: 出力全文（60 行の対象外）

### TODO-043

```
TODO-043 の範囲
  始点 2026-08-24 18:00:56  5c7d18f docs(todo): ゲージの針と基準線を図形で描き直す件を TODO-043 として立てる
  終点 2026-08-24 18:29:15  3403798 feat(webapp): ゲージの針と基準線を SVG で描く（TODO-043）

担当             output  cache_creation    (cache_read)   msgs          $
main             32,875          53,893       5,213,266     33       $3.8
verifier          1,176         193,102       4,242,581     71       $1.3
wording              53          31,869         308,979     11       $0.1
runner                7          16,734          30,035      3       $0.0
合計             34,111         295,598       9,794,861    118       $5.3

モデル                        output  cache_creation    (cache_read)   msgs          $
claude-opus-5                 32,875          53,893       5,213,266     33       $3.8
claude-sonnet-5                1,229         224,971       4,551,560     82       $1.5
claude-haiku-4-5-20251001          7          16,734          30,035      3       $0.0
合計                          34,111         295,598       9,794,861    118       $5.3

消費: output 34,111 / cache_creation 295,598 / 概算 $5.3
      main 71% + verifier 25% + wording 3% + runner 0%（料金の割合）
（参考: cache_read 9,794,861、メッセージ 118 件）
```

### TODO-038（`--since '2026-08-23 21:25:24'`）

```
08/24 19:01:30 ⚠️ WARNING token-usage.py:323 price_for()> <synthetic>: 単価表に無いモデル .. claude-opus-5 の単価で概算
TODO-038 の範囲
  始点 2026-08-23 21:25:24  --since
  終点 2026-08-24 06:13:36  1a6a4fd feat(webapp): HTML・CSS のリファクタリング（TODO-038）

担当             output  cache_creation    (cache_read)   msgs          $
main            126,053         487,210      21,858,397    167      $17.1
implementer      11,457         538,625      22,574,089    275      $14.9
verifier          4,303         285,275      32,162,615    334       $7.2
wording           1,260         135,817       1,255,060     34       $0.6
reviewer            124          79,635       1,088,931     22       $0.4
合計            143,197       1,526,562      78,939,092    832      $40.3

モデル              output  cache_creation    (cache_read)   msgs          $
claude-opus-5      137,510       1,025,835      44,432,486    438      $32.1
claude-sonnet-5      5,687         500,727      34,506,606    390       $8.2
<synthetic>              0               0               0      4       $0.0
合計               143,197       1,526,562      78,939,092    832      $40.3

消費: output 143,197 / cache_creation 1,526,562 / 概算 $40.3
      main 43% + implementer 37% + verifier 18% + wording 1% + reviewer 1%（料金の割合）
（参考: cache_read 78,939,092、メッセージ 832 件）
```

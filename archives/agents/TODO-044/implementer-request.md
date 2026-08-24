# TODO-044 implementer への依頼

`TODO.md` の「## TODO-044. トークン消費の測り方と、担当の走らせ方を見直す」を
先に読むこと。

担当するのは **`tools/token-usage.py` だけ**。`.claude/agents/*.md` と
`~/.claude/CLAUDE.md` は main が別に直すので、触らない。

## やること

### 1. 同じリクエストの usage を、最終値で数える

`collect()` は `(requestId, message.id)` が同じ行を「先に出会ったほう」で
数えている。サブエージェントの transcript には同じリクエストの usage が
途中経過と最終値の両方で記録されていて、いま採っているのは途中経過。

**同じ key の行は、各項目（`output` / `cache_creation` / `cache_read` /
`input`）ごとに最大値を採る**ように直す。行の並びが最終値を後に置くとは
限らないので、上書きではなく最大値で。`messages` は 1 のまま
（リクエスト 1 件として数える）。

確かめ方の目安: TODO-043 の verifier は、いまの集計では `output` が 654。
直したあとは 2,000〜3,000 程度になるはず。

### 2. 概算料金を出す

単価（$/1M トークン）を `tools/token-usage.py` に持たせる。

| モデル | input | output |
|--------|-------|--------|
| `claude-opus-5` | $5.00 | $25.00 |
| `claude-sonnet-5` | $2.00 | $10.00 |
| `claude-haiku-4-5` | $1.00 | $5.00 |

- **cache write（`cache_creation`）は input の 1.25 倍、cache read
  （`cache_read`）は input の 0.1 倍**で概算する
- **Sonnet 5 の $2 / $10 は 2026-08-31 までの導入価格**。そのあとは
  $3 / $15 になる。**この期限をコメントに明記する**（書き換えが要ると
  分かるように）
- transcript の `message.model` は `claude-haiku-4-5-20251001` のように
  日付が付くことがある。**前方一致で引く**
- 表に無いモデル名に当たったら、警告を出して Opus 5 の単価で数える
  （多めに見積もる側に倒す）。どの名前が当たらなかったかを分かるように

料金は `Record` ごとに、そのモデルの単価で計算して足し込む。担当ごとの
合計にも料金を持たせる（1 人の担当が複数のモデルを使うことは無いはずだが、
モデル別に計算してから足す形にしておく）。

### 3. 出力を変える

`print_summary()` が出す「消費:」を、この形にする。

```
消費: output 33,589 / cache_creation 295,598 / 概算 $5.3
      main 71% + verifier 25% + wording 3%（料金の割合）
```

- **概算料金は全体の合計**（`output` + `input` + `cache_creation` +
  `cache_read` を、それぞれの単価で計算した合計）。ドル、小数第 1 位まで
- **担当ごとの割合は料金で出す**（いまは `output + cache_creation` の
  割合）。`fmt_shares()` を料金で計算するように直す
- `（参考: cache_read …）` の行はそのまま残す
- `print_table()` の表にも料金の列を足す（`$` の列）。担当ごと・モデル
  ごとに、何にいくらかかっているかが画面で見えるように
- 表の並び順（多い順）も料金で並べる

## 決まりごと

- **`~/ytsched/data` を触らない。** 動かして確かめるときは transcript を
  読むだけなので、書き込みは起きないはず
- `mise run fmt` / `typecheck` / `lint` / `test` は叩いてよい。
  **`mise run upgradeproject` は走らせない**
- 実際に `uv run python tools/token-usage.py TODO-043` などを走らせて、
  直す前と後で数字がどう変わったかを報告に書く
- 報告は `archives/agents/TODO-044/implementer-report.md`。
  返事は 5 行以内

# TODO-059 の分担

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort medium | main のみ + verifier |
| 実施 | Opus 5 / effort medium | main + verifier ×2 + wording |

## なぜこの分担にしたか

**実装は main が持った。** 触るのは 2 つのファイルの 1 関数ずつと、
目盛りの一覧という小さい範囲で、Python と JavaScript を同じ式に
そろえるところが要点だったため、分けても受け渡しの手間のほうが大きい。

**確認は verifier に分けた。** コードを変える項目では規模によらず
分けると決めてある（`~/.claude/CLAUDE.md`）。この項目では特に、
**Python と JavaScript が本当に同じ値を返すか**という、実装した本人が
「同じ式を書いたのだから同じはず」で済ませてしまう種類の確認があった。

## verifier を 2 回立てた理由

1 回目のあとに、利用者から目盛りを増やす話（`±6m`・`±10y`）と、
`DAYS_GAGE_K` を 10 にする話が続けて出て、**確かめた対象と最終形が
別物になった**。1 回目の報告は式そのものの確認としては生きているが、
そのまま最終形の確認にはできないので、依頼書を書き直して立て直した。

- [1 回目の依頼と報告](request-verifier.md) → [verifier-report.md](verifier-report.md)
  （依頼書は 2 回目で上書きしてある）
- 2 回目の報告 → [verifier-report2.md](verifier-report2.md)

## wording

`.md` が入るコミットなので立てた（TODO-025・TODO-026）。
報告は [wording-report.md](wording-report.md)。

`wording` は 4 語（相乗平均・発散・割る数・浮動小数）を挙げた。
**4 語とも言い換えた**（main の判断）。

- 「1 と 12 の相乗平均 √12」→「1 と 12 を掛けて平方根を取った値 √12」
- 「対数が発散しないように足していた値」→「日数が 0 のときに対数が
  計算できなくなるのを避けるために足していた値」
- 「割る数 `DAYS_GAGE_K`」→「日数を割る `DAYS_GAGE_K`」
- 「浮動小数」→「浮動小数点数」（省略形だったため）

挙げた語そのものは `wording-report.md` と `request-wording.md` に残る。

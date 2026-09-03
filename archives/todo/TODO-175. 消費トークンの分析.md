# TODO-175. 消費トークンの分析

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort high | main + verifier |
| 実施 | Opus 5 / effort high | main + verifier |
| 消費 | output 82,853 / cache_creation 392,926 / 概算 $6.0 |
|      | main 92% + verifier 8%（料金の割合） |

分担の理由と各担当の報告は
[archives/agents/TODO-175/](../agents/TODO-175/README.md) にある。

**消費は `--since '2026-09-03 20:50:10'` で測った。** 「立てる」コミット
（`docs(todo):`）を、分析そのものをやり終えたあとに作業の記録として
作ったため、コミット時刻を始点にすると、分析の大半（このコミットより
前にやった集計・文書化・verifier とのやり取り）が範囲から漏れる。
セッションの開始時刻を始点にして測り直した。

## きっかけ

`archives/todo/` の各項目に「消費」の行を残す運用（TODO-035・TODO-044）を
続けてきたが、まとめて見返したことは無かった。何にいちばん払っているか、
節約が効くところ・効かないところをはっきりさせたいということで立てた。

## やったこと

`archives/todo/` の 173 件のうち、概算料金が記録されている 99 件
（TODO-044 以降）と、Claude Code の transcript（`tools/token-usage.py` が
読む全体）を集計し、`docs/token-usage-analysis.md` にまとめた。

要点は次のとおり。

- **料金の 3 分の 2 は `cache_read`。** 同じ会話を読み直すぶんに払って
  いて、書いた量（`output`）は 14% しかない
- **main が 73%。** 確認の担当（verifier・reviewer・wording）を合わせても
  1 割強で、担当を削る節約には伸びしろが無い
- **main が自分で実装した項目は、変更量あたりで 1.6 倍かかる。** 特に
  main の会話が 100 回を超えた項目（全体の 1 割）が、main の料金の 4 割を
  占める
- 効かない節約として、**定型作業の自動化より `/clear` のほうが 3 倍効く**
  ことが TODO-052 の記録から裏付けられた
- 「どうすべきか」として、会話を切るタイミング（`/clear`）、main に実装を
  抱えさせない判断、見た目の調整の進め方など 5 点をまとめた

### verifier が見つけたバグ

verifier に数字の突き合わせを頼んだところ、**行数を集計する使い捨て
スクリプトにバグがあった。** `git show --numstat` は、ファイル名に
日本語が入ると `"archives/todo/TODO-063. ...\343..."` のように二重引用符
付きで返すため、`path.startswith("archives/")` による除外がすり抜け、
**アーカイブ済みファイル自身の行数が本文の変更量に紛れ込んでいた**
（TODO-063 は 13 行のはずが 90 行、TODO-059 は 38 行のはずが 148 行など）。
「変更量あたりの料金」を扱っていたすべての数字を、`-z` でファイル名を
クォートしない集計に直して数え直した。

ほかに、本文と表が矛盾していた箇所（「上位 5 件はどれも main が
87% 以上」に対し、表では 2 件が 87% 未満だった）、項目の題名の省略、
測るたびに増える性質（この分析をしている会話自身も transcript に
記録され続けるため）も見つかり、文書に反映・注記した。詳細は
[archives/agents/TODO-175/verifier-report.md](../agents/TODO-175/verifier-report.md)。

### 再現できるようにした

集計に使ったスクリプトを
[archives/agents/TODO-175/measure.py](../agents/TODO-175/measure.py) として
残した。`uv run python archives/agents/TODO-175/measure.py` で、
`docs/token-usage-analysis.md` の主な数字を出し直せる。

## テスト

分析と文書だけの項目で、コードは変えていない。`archives/agents/TODO-175/
measure.py` は `mise run lint`（`ruff format` / `ruff check` /
`basedpyright`）を通した。

verifier による数字の突き合わせは、上記の「見つけたバグ」のとおり。

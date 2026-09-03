# TODO-175 の分担

`docs/token-usage-analysis.md` を書くために、`archives/todo/` の記録と
transcript を集計した。**着手時の見込みどおり main + verifier。**

## 誰に何を頼んだか

- **main** — 集計、文書の下書き、指摘の反映
- **verifier** — 文書に載せた数字が、実際の記録と合うかを確かめる。
  依頼は [`verifier-request.md`](verifier-request.md)、報告は
  [`verifier-report.md`](verifier-report.md)

## verifier が見つけたこと、直したこと

1. **行数の集計にバグがあった（実質的な不一致）。** main が使った
   使い捨てスクリプトは、`git show --numstat` の出力から `archives/`
   配下を除いていたが、**ファイル名に日本語が入ると git が
   `"archives/todo/TODO-063. ...\343..."` のように二重引用符付きで
   返す**ため、`path.startswith("archives/")` がすり抜けていた。
   結果、**アーカイブ済みファイル自身の行数が本文の変更に紛れ込んで
   いた**（TODO-063 は 13 行のはずが 90 行、TODO-059 は 38 行のはずが
   148 行など）。「変更量でならすと」「効いているか」の 100 行あたりの
   数字と、TODO-063・TODO-059 の例をすべて数え直した
2. **本文と表の矛盾。** 「高額な上位 5 件は、どれも main の割合が
   87% 以上」に対し、表では TODO-047 が 60%、TODO-049 が 46% だった。
   実際は 5 件中 3 件が 87% 以上、残り 2 件は implementer が多めに
   動いていた、と直した
3. **項目の題名の省略・読点の欠落。** TODO-069 の題名が後半ごと
   落ちていた（「…DOM に持つ」→「…DOM に持ち、週移動でページを
   読み直さない」）。TODO-047・TODO-048 の「やめて、」の読点も戻した
4. **「見込みから外れたら」の判定方法が再現できなかった。** 元の
   計算はセッション内の使い捨てコードにしかなく、verifier が
   独自に再現したところ件数・中央値が少しずれた。判定方法
   （見込み・実施それぞれの担当の顔ぶれを比べる。回数や
   「main のみ」は無視）を文書に注記し、再現できるスクリプトを
   [`measure.py`](measure.py) として残した
5. **「何を数えたか」の合計が測るたびに増える件。** transcript には
   この分析をしている会話自身も記録され続けるので、後で数え直すと
   増える。文書に注記を足した

1（バグ）と 4（再現性）は、修正のうえ `measure.py` の
docstring・コメントに残した。2・3・5 も文書を直した。

## 再現するには

```
uv run python archives/agents/TODO-175/measure.py
```

`docs/token-usage-analysis.md` の数字（「何を数えたか」の transcript
全体の合計を除く）はこれで出る。transcript 全体の合計・担当別・
会話の長さ別は `tools/token-usage.py` の `collect()` / `total_of()` /
`sum_by()` を使う（`archives/agents/TODO-175/verifier-request.md` に
使い方の一例がある）。

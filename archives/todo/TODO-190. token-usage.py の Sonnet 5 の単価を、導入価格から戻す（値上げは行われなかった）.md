# TODO-190. `token-usage.py` の Sonnet 5 の単価を、導入価格から戻す（値上げは行われなかった）

|      | main | 担当 |
|------|------|------|
| 見込み | Sonnet 5 / effort medium | main + verifier |
| 実施 | Opus 5 / effort high | main + verifier |

| 担当 | モデル | effort | output | cache_creation | 料金の割合 |
|------|--------|--------|--------|----------------|-----------|
| main | Opus 5 | high | 9,801 | 100,591 | 93% |
| verifier | Sonnet 5 | medium | 3,234 | 31,122 | 7% |
| 合計 |  |  | 13,035 | 131,713 | 概算 $2.0 |

- verifier は定義（`.claude/agents/verifier.md`）のまま。モデルは `sonnet`、
  `effort: medium` の行があり、Sonnet 5 なので効いている
- main は見込みでは Sonnet 5 を想定していたが、実際には Opus 5 で動かした
- 集計はコミット前に取ったので、このファイルを書いてコミットするまでの分は
  入っていない

## きっかけ

`CLAUDE.md` に「Sonnet 5 の $2/$10 は 2026-08-31 までの導入価格なので、
そのあとは $3/$15 に書き換える」と書いてあるのに、期限を過ぎた 2026-09-07
現在も `~/.claude/bin/token-usage.py` の `PRICING` が
`"claude-sonnet-5": (2.00, 10.00)` のままだった（`/doctor` で気づいた）。
このままだと Sonnet 5 を使った項目の概算料金が安く出る、という見立てだった。

## やったこと

### 値上げは行われていなかった

公式のドキュメント（`platform.claude.com/docs/en/about-claude/pricing`、
2026-09-07 に取得）に、次の注記があった。

> The $2/$10 per million input/output token pricing for Claude Sonnet 5,
> announced at launch as introductory pricing through August 31, 2026,
> is now the standard price. The previously scheduled increase to $3/$15
> per million input/output tokens on September 1, 2026 will not occur.

導入価格がそのまま正規の単価になり、$3/$15 への値上げは行われない。
**`PRICING` は最初から正しく、直す必要が無かった。**

`token-usage.py` には、2026-09-06 に一度 $3/$15 へ直したのを、セッション
末尾の `cost-state` 行（`modelUsage[*].costUSD`）と突き合わせて誤りと
突き止め、戻した経緯がコメントに残っていた。その検算の結論を、翌日に公式の
ドキュメントが裏付けた形になる。

**`archives/todo/` の概算料金も直していない。** 単価は一度も変わっていない
ので、過去の項目どうしをそのまま比べられる。TODO を立てたときは「単価が
変わった日を `CLAUDE.md` に残し、その前後の項目を比べられないことが分かる
ようにする」つもりだったが、変わらなかったので不要になった。

### 直したのは記述だけ

残っていた問題は、`CLAUDE.md` が「そのあとは $3/$15 に書き換える」と
指示し続けていたこと。放っておくと、次のセッションがまた `PRICING` を
壊す。

- `CLAUDE.md`（ytsched）… 「Sonnet 5 は $2/$10。導入価格として告知されたが、
  2026-09-01 に予定されていた値上げは行われず、そのまま正規の単価になった」
  に差し替えた。単価が一度も変わっていないことも書いた
- `~/.claude/bin/token-usage.py` … `PRICING` の上のコメントに、2026-09-07 に
  公式のドキュメントで確定した旨を足した。もとのコメントは `cost-state` との
  検算の話だけで、「導入価格の期限」の話が宙に浮いていた

## テスト

- 公式のドキュメントを main と verifier がそれぞれ独立に引き、Sonnet 5
  $2/$10・Opus 5 $5/$25・Haiku 4.5 $1/$5 が `PRICING` と一致することを
  確かめた（verifier は WebFetch ではなく `curl` で取得した）
- `~/.claude/bin/token-usage.py --list` がエラーなく動くことを確かめた
  （コメントを足しただけだが念のため）
- `archives/` を除いたリポジトリに「$3/$15 に書き換える」の類いの
  古い指示が残っていないことを grep で確かめた

## 分担の振り返り

分担の理由と報告は [`archives/agents/TODO-190/`](../agents/TODO-190/README.md) にある。

- **verifier が見つけたこと。** 単価そのものは 3 モデルとも公式と一致していて、
  数値の誤りは無かった。代わりに、`CLAUDE.md`（2026-09-07 に公式で確認）と
  `token-usage.py` のコメント（2026-09-06 に検算）の日付が 1 日ずれて見える、
  という読みにくさを挙げてきた。矛盾ではなく別々の出来事だが、読んだ人が
  一度つまずいた事実なので、コメントに「その翌日」と足して時系列が分かる
  ようにした
- **見込みと食い違ったのはなぜか。** 「単価が上がっているはずだから直す」
  という前提で立てた項目だったが、調べたら値上げ自体が行われておらず、
  コードの変更はゼロになった。見込みの担当（main + verifier）は変えていない
- **次に同じ規模の項目をやるなら。** 「外部の事実を確かめてから直す」種類の
  項目は、**確認を先に 1 回だけ**やれば済む。今回 main が公式のドキュメントを
  引いた時点で結論は出ていて、そのあと verifier に同じことをさせた分は
  重複だった。ただし単価は全項目の概算料金に響くので、二重に引く価値はある。
  次も同じ形でよい。減らすなら main 側で、`claude-api` skill を丸ごと読み込んだ
  分（skill の単価表は 2026-06-24 時点のキャッシュで、決め手にはならなかった）を
  省き、最初から公式のドキュメントを引く

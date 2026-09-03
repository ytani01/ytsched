# TODO-175 verifier への依頼

## 目的

`docs/token-usage-analysis.md` に載せた数字が、実際の記録と合うかを確かめる。
**文書は直さない。** 食い違いを見つけたら報告するだけ。

## 対象範囲

`docs/token-usage-analysis.md` の表と本文に出てくる数字すべて。出どころは 2 つ。

1. `archives/todo/*.md` の「消費」の行（99 件に概算料金がある）
2. Claude Code の transcript（`~/.claude/projects/-home-ytani-work-ytsched/`）。
   `tools/token-usage.py` の `collect()` / `parse_line()` / `record_cost()` /
   `sum_by()` を使い捨てのスクリプトから呼んで数える

main が使った集計スクリプトは以下に置いてある。**そのまま信用せず、
中身を読んでから使うこと**（読み取りの誤りがあれば、それも報告対象）。

- `/tmp/claude-649/-home-ytani-work-ytsched/ab1fde34-d888-4338-81b5-07b9df9c7b4d/scratchpad/parse.py` … archives の消費行と見込み・実施の行を JSON にする
- `/tmp/claude-649/-home-ytani-work-ytsched/ab1fde34-d888-4338-81b5-07b9df9c7b4d/scratchpad/total.py` … transcript 全体の合計と担当別の集計
- `/tmp/claude-649/-home-ytani-work-ytsched/ab1fde34-d888-4338-81b5-07b9df9c7b4d/scratchpad/curve2.py` … main の会話を長さ別にまとめる

## 完了条件

次を確かめて、合否と実測値を報告する。

1. **「何を数えたか」** — 期間 2026-08-23〜2026-09-03、リクエスト 20,161、
   概算 $852、記録のある項目 99 件、合計 $508 / 平均 $5.13 / 中央値 $3.30
2. **「内訳は cache_read が 3 分の 2」** の 3 行（料金と割合）
3. **「担当別では main が 73%」** の表（リクエスト数・コンテキスト長・料金・割合）
4. **「会話は進むほど高くなる」** の 2 つの表
5. **「高くつく項目の特徴」** — 上位 5 件の料金と main の割合、TODO-077 の
   $43.8・89%・533 メッセージ、100 行あたりの 3 つの数字、
   TODO-063 と TODO-059 の行数と料金
6. **「効かない節約」** — verifier $0.44 / reviewer $0.60 / wording $0.18。
   TODO-052 から引いた $2.6 → $1.0 / $2.6 → $0.3 が、
   `archives/todo/TODO-052. …` の記述と合っているか
7. **「見込みから外れたら」** — 68 件 $2.65 / 31 件 $5.20
8. **「効いているか」** の表（番号帯ごとの件数・料金の中央値・100 行あたり）
9. 項目の題名（TODO-047/048/049/069/077/059/063）が
   `archives/todo/` のファイル名と合っているか
10. `TODO.md` の TODO-175 の節に見込みの行が入り、書式が他の項目と揃っているか

## 検証方法

- 1〜8 は自分で数え直して、文書の数字と突き合わせる。**四捨五入の
  範囲（表示桁で一致）なら合格**、それを超える差は不一致として報告する
- `uv run python <スクリプト>` で走らせてよい。
  `mise run upgradeproject` は走らせない
- コードは変更していないので、テスト・lint は走らせなくてよい

## 報告

`archives/agents/TODO-175/verifier-report.md` に書く。返事は 5 行以内で、
終わったか・報告ファイルのパス・判断が要る点だけ。

# TODO-044 wording への依頼（着手後の分）

TODO-044 を実施したときのコミットに入る `.md` を見て、**このリポジトリに
前例の無い語**を挙げてほしい。

項目を立てたときの分は
[wording-report.md](wording-report.md) に済んでいる。**今回はその後に
書いた分**を見る（前回挙がった語が本文に残っていれば、それも挙げてよい）。

## 対象

- `TODO.md`（TODO-044 の節を削り、完了済みへ移した差分）
- `CLAUDE.md`（「トークン消費量の記録」の節に単価の注記を足した）
- `archives/todo/TODO-044. トークン消費の測り方と、担当の走らせ方を見直す.md`
- `archives/agents/TODO-044/` の全ファイル
  （`README.md`、`*-request.md`、`*-report.md`。**担当の報告も含める**）
- `.claude/agents/verifier.md` と `.claude/agents/implementer.md`
  （main が書き換えた）

`~/.claude/CLAUDE.md`（利用者全体の指示）も同じ項目で書き換えたが、
このリポジトリの外なので対象外。

## やること

- **前例の有無は `git grep -cF <語> HEAD -- '*.md'` で確かめる。**
  HEAD には今回の変更がまだ入っていない
- 候補は**十数語に絞る**。件数が少ない順に並べ、箇所と見立てを添える
- **決めるのは main。** 直さない
- 特に見てほしい語: 「概算料金」「単価」「導入価格」「料金の割合」
  「最大値集計」「途中経過」「読み方」「当たりを付ける」

## 決まりごと

- 報告は `archives/agents/TODO-044/wording-report2.md`。返事は 5 行以内

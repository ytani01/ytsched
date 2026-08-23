# TODO-027 reviewer への依頼（2 回目）

あなたが 1 回目に出した指摘 1・2・4（変換に成功したあとの値の範囲を
誰も見ていない）と、ついでの 3・5・6・7・8 に対応した実装が終わった。
**直り方を見てほしい。コードは直さないこと。**

## 読むもの

- 自分の `archives/agents/TODO-027/reviewer-report.md`
- `archives/agents/TODO-027/implementer-request2.md`
- `archives/agents/TODO-027/implementer-report2.md`
- 変更そのものは `git diff`

## 特に見てほしいところ

1. **指摘 1・2・4 が本当に直っているか。** 「入り口で範囲を見る」形に
   まとめたと書いてあるが、**まだ範囲を見ていない経路が残っていないか**。
   実装者自身が「POST 側の `modified_date` は範囲を見ていない」と
   申告している。ほかにもあるか
2. **範囲の決め方（`date.min + margin` 〜 `date.max - margin`、
   `margin = max(self._days, SEARCH_MODE_MAX_DAYS)`）が正しいか。**
   off-by-one は無いか。`load_sched()` / `load_todo()` の実際の
   足し引きより本当に広いか。`--days` を極端に大きくしたときはどうか
3. **`todo_days` の範囲を `-1..36500`（`TODO_DAYS` の選択肢の幅）に
   した判断。** 実装者は「`todo_days=-5` が off ではなく既定値へ落ちる
   ようになった」と副作用を申告している。ほかに変わるものが無いか
4. **`ymd2date()` が `year/month/day` を `/` で繋いで
   `convert_value()` に渡す形**になった。`split()` の unpack で
   `ValueError` を狙っているが、**思わぬ入力（`year=1/2` のように
   `/` を含む値）で変な通り方をしないか**
5. 警告メッセージの形が 1 回目から変わっている
   （`year='2021', month='13'...` → `year/month/day='2021/13/1'...`）。
   読んで分かる形か
6. **足したテスト 13 件が挙動を固定するものになっているか。**
   実装者は「範囲を見る条件を潰すと 9 件落ちる」と書いている。
   境界のテスト（使える範囲の上端・下端）が、範囲の根拠を
   押さえられているか
7. 1 回目の指摘 3・5・6・7・8 の対応が十分か。特に **`TestConfArgs` の
   docstring** が、TODO-028 で `empty_is_given` を揃えるときに
   読んで役に立つ形になっているか

## 決まりごと

- コードは直さない
- 報告は `archives/agents/TODO-027/reviewer-report2.md` に書く。
  重要度の順に並べる。**直っているものは「直っている」と明記する**
- 返事は 5 行以内

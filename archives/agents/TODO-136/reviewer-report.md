# TODO-136 reviewer 報告（再確認）

対象: `src/ytsched/webroot/static/js/week.js`・`swipe.js`・`nav.js`、
`tests/test_browser.py`（すべて未コミットの `git diff HEAD`）。

前回（1 回目）の報告は本ファイルの末尾「前回の指摘（1 回目、参考）」に
残す。ここでは、その指摘が直っているかどうかを再確認した結果を書く。

## 結論

前回の確信度の高い指摘 2 件は、どちらも直っている。新たな確信度の高い
指摘は無し。

## 確認したこと

### 1. `moveActiveMonth()`/`mondayDaysInMonth()`（week.js）の新しい実装

「``activeMonday`` がその月の何番目の月曜か（``idx``）を求め、ずらした
先の月でも同じ番目の月曜へ移る（無ければ最後の月曜に留める）」という
設計で、`target = new Date(targetYear, targetMonth, targetDay)` の
`targetDay` は必ず `mondayDaysInMonth(targetYear, targetMonth)` が返した
値（＝その月に実在する月曜の日）なので、**結果の月が `targetMonth` から
外れることは構造上あり得ない**（`mondayOf()` のような後段の丸めが無い
ため、前回のような「丸めで月境界を越えて戻る」経路が無くなっている）。

念のため、この JS のロジックをそのまま Node に切り出し、**2000〜2040 年の
全ての月・その月に含まれる全ての月曜・両方向（direction = ±1）を
網羅**して検算した（4,280 通り）。

- 結果の年月が「ずらした先の月」と一致しないケース: 0 件
- 結果が月曜でないケース: 0 件

うるう年の 2 月（月曜 4 個の年・5 個の年の両方）、4 週の月 → 5 週の月・
その逆をまたぐケース、年をまたぐケース（12 月 ⇄ 1 月）もすべて含めて
確認済み。`total`/`targetYear`/`targetMonth` の負数を挟んだ剰余の扱い
（`((total % 12) + 12) % 12`）も含め、境界での誤りは見つからなかった。

`new Date(ytsched.ytState.activeMonday)`（ISO 形式の日付文字列を
`new Date()` に直接渡す書き方）は、`mondayOf()` の呼び出し元
（261 行目・276 行目）など、このファイルの既存コードにも同じ書き方が
あり、今回新しく持ち込まれたものではない。UTC/ローカルタイムのずれの
可能性はあるが、**今回の変更で新たに生じた問題ではない**ため対象外と
判断した。

### 2. `tests/test_browser.py` の書き換え

`_add_month_round_monday()`（実装の内部ロジックをそのまま Python で
再実装していた関数）は削除されている。代わりの `_expected_month()` は
「``monday`` の年月から ``direction`` ヶ月分だけ動いた年月」だけを計算し、
`moveActiveMonth()` が内部で使っている「月の中で何番目の月曜か」という
計算には触れていない。`_assert_moved_to_month()` も、URL の `date` を
読んで年月と曜日（月曜）だけを確かめており、日そのものは検証していない
（要件は「1 ヶ月進む/戻る」「移動先の曜日が月曜」の 2 点であり、日の
値そのものは要件ではないので、この範囲の絞り方は妥当）。実装の内部
ロジックをなぞる書き方には戻っていない。

### 3. `mise run lint` / `uv run pytest tests`

- `mise run lint`: fmt（ruff format/check）・typecheck（basedpyright/
  mypy）・fmtjs（prettier）・lintjs（eslint）すべて通過
- `uv run pytest tests`: 560 件全て pass（137.98s）

## 前回の指摘（1 回目、参考）

1. `moveActiveMonth()` が `Date.setMonth()` で月をずらしたあと
   `mondayOf()` で週の月曜へ丸める設計だったため、丸めが月境界を越えて
   元の月（時に 2 ヶ月前）へ戻ってしまうケースがあった（2021〜2030 年の
   月初の月曜だけでも前進 42 件・後退 71 件で発生）。→ **直っている**
   （上記 1.）。
2. `tests/test_browser.py` の `_add_month_round_monday()` が実装と同じ
   （同じ欠陥を持つ）計算をそのまま再実装していたため、このバグを
   テストが検出できなかった。→ **直っている**（上記 2.）。
3. ヘッダコメントの粒度（低優先、確信度低）: `week.js` の
   `getLocaltimeDateString() / getLocaltimeString() / shiftDays()`
   をまとめて列挙し、呼び出し元をまとめて並べる書き方について、
   `moveActiveMonth()` は実際には `getLocaltimeDateString()` しか
   呼んでいない、という指摘。今回の再確認でも同じ状態のままだが、
   これは変更前から使われている既存の書式（1 対 1 対応を厳密に示す
   表ではない）であり、今回のバグ修正の範囲外と判断し、再度は挙げない。

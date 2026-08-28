# TODO-103 reviewer 報告

依頼書（`archives/agents/TODO-103/reviewer-request.md`）どおり、
`implementer-request.md` / `implementer-report.md` を読んだうえで
`git diff` を見た。コードは直していない。

## 確信度の高い指摘

### 1. `sdf_exists()` だけで判定するため、全予定を削除した日にもドットが残る

- `src/ytsched/sched_load.py` の `load_month_cal()`（`has_sched=self._sd.sdf_exists(date1)`）
- `src/ytsched/ytsched.py` の `SchedDataFile.save()`（635 行目付近）は、
  その日の予定が 0 件になっても **空のファイルを書く**（`.bak` を空で
  上書きしないための仕様、コメントにもその通り書いてある）。
  `sdf_exists()`（810 行目）は `pathname.is_file()` を見るだけなので、
  中身が空でも `True` を返す
- 結果として、**その日の予定を全部削除しても、ミニカレンダーのドット
  は消えない**（次にその日へ実際にデータが書かれて上書きされるまで
  残り続ける）。依頼書どおりの実装ではあるが、実際にどう見えるかの
  確認として報告する

既存の `load_week()`（`sched_load.py` 352 行目）も `sdf_exists()` を
先に見ているが、そちらは「開くかどうか」の最適化に使っているだけで、
実際に開いて中身（0 件）を表示に反映している。ミニカレンダーは
**開かずに「予定あり」の印にしてしまう**ので、性質が違う。

## 確信度が低い指摘（気になった程度）

- `tests/test_web.py` の `test_out_of_month_day_is_not_clickable` は、
  docstring で「4 月分の最初の週には 3 月分の埋めセルがある」ことを
  確かめるように書いてあるが、実際にマッチしているのは **4 月最後の週
  にある 5 月 1 日の埋めセル**（2021-04-30 が金曜なので、最後の週が
  5/1・5/2 まで伸びる）。テスト自体は「埋めセルに `onmousedown` が付か
  ない」ことを正しく確認できているので機能的な問題ではないが、
  docstring の説明と実際に一致した箇所がずれている
- `MonthCalDay.in_month` を `date1.year == year and date1.month == month`
  にした判断（年もチェック）について、報告書は「年をまたぐ 12 月/1 月
  の埋めセルでも誤判定しないよう」としているが、埋めセルは月初/月末の
  週から前後最大 6 日しか伸びないため、月をまたいでも月番号が目的の月と
  一致することはなく、年を見なくても実際には誤判定しない（`month` だけ
  の比較でも壊れない）。実害は無いので直す必要はないが、コメントの
  理由付けは正確ではない

## 見たが問題なしと判断したところ

- `load_month_cal()` の境界（月初・月末の曜日、月曜始まり、うるう年、
  年またぎ）はロジック・テストとも問題なし
- キャッシュ（`_month_cal_cache`）は `SchedLoader` がリクエストごとに
  生成される（`MainHandler.initialize()`）ので、古い内容を返す道は無い
- テンプレートの `datetime.timedelta(6)` は Tornado のテンプレート名前
  空間に標準で入っている（`tornado/template.py` の
  `namespace["datetime"] = datetime`）ので動く。他のテンプレートに
  前例は無いが、初出の使い方として問題は無い
- `onmousedown="scrollToDate(...)"` の付け方、日付フォーマット
  （`str(date)` → `YYYY-MM-DD`）は既存の日付セル・`nav.js` の
  `date-${date}` id と揃っている
- CSS は末尾に `.my-mini-cal-*` として追加されており、既存クラス
  （`.my-btn`、`.my-date-block-today` の枠色）との詳細度の衝突は無い
- 週パネルごとに 2 ヶ月分のテーブルが増える点は、`SchedLoader` の
  月ごとキャッシュで実際の `sdf_exists()` 呼び出し数は抑えられており、
  懸念するほどではないと判断した

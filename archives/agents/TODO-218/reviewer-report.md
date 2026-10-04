# TODO-218 reviewer の報告

対象: 未コミットの差分（`sched_load.py`、`mini_cal.html`、
`tests/test_web.py`、`tests/test_main_handler.py`）。

## 要修正

無し。

## 検討

### 1. `has_important` を `dot_sde_list` に絞った部分を見るテストが無い

- 場所: `src/ytsched/sched_load.py` 409-411 行、
  `tests/test_main_handler.py` の `test_holiday_only_day_has_no_dot`
- `has_important` だけを元の `sde_list` に戻しても、`MonthCal` /
  `MiniCal` のテスト 26 本はすべて通った（実測。HEAD の `src` を
  scratch に展開し、今の `sched_load.py` の該当 1 行だけ戻して
  `pytest -k "MonthCal or MiniCal"`）
- 問題になる状態: 同じ日に「重要の接頭辞が付いた休日」と「重要でない
  普通の予定」があるとき。戻すと、ドットが重要の色で出る。
  `mini_cal.html` は `has_sched` が偽ならドット自体を出さないので、
  休日だけの日には影響しない
- 実害は小さい（重要の接頭辞付きの休日を登録することがあるかは未確認）。
  テストを足すなら、`mixed` の日の休日のタイトルを重要の接頭辞付きにして
  `has_important` が偽であることを見れば 1 行で済む

## 問題なしの点

- 呼び出し元: `has_sched` / `has_important` / `in_month` を読むのは
  `mini_cal.html` だけ。JS はこれらのクラス（`my-mini-cal-day-out` /
  `-sat` / `-holiday`）を参照していない。`in_month` は `-out` の付与に
  引き続き使われている
- `is_holiday` は `sde_list`（ToDo 以外すべて）から判定したままで、
  背景色の判定は変わっていない
- CSS: `.my-mini-cal-day-out` は文字色（`#999`）だけで背景を持たないので、
  曜日・休日のクラスの背景と衝突しない。1541 行のコメント
  （祝日・日曜 > 土曜 > 白）も今の挙動と合っている。今日・表示中の週の
  枠は `box-shadow` なので背景色と独立
- 月間表示（`month.html`）も同じ `mini_cal.html` を使うので、前後の月の日が
  色付きになる。TODO の方針どおり
- テストの強さ: HEAD の `src` に今のテストを当てると、
  `test_out_of_month_day_is_clickable` / `test_out_of_month_holiday_is_colored` /
  `test_holiday_only_day_has_no_dot` の 3 本が落ちる（実測）。今の `src` では
  通る
- 文書: `src/README.md` 300 行あたりの `load_month_cal` の説明、
  `docs/User.md` の 4 章、`tests/README.md` に、今回の変更で古くなった
  記述は無い

## 作り込みすぎ

なし。Lean already. Ship.

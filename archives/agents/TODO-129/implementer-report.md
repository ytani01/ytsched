# TODO-129 implementer 報告

## 変更したファイル

- `src/ytsched/sched_load.py`
  - `MonthCalDay` に `has_important` / `is_holiday` / `has_todo` を追加
  - `SchedLoader.__init__` に `_todo_dates`（ToDo 締切日の集合、初回だけ
    `self._sd.get_sdf(None).sde` から作る）を追加。`_get_todo_dates()` を新設
  - `load_month_cal()` を `self._sd.sdf_has_sde(date1)`（ファイルの大きさだけ）
    から `self._sd.get_sdf(date1).sde` を読んで判定する形に変更。通常の予定
    （`not sde.is_todo()`）だけを見て `has_sched` / `has_important`
    （`is_important()`）/ `is_holiday`（`is_holiday()`）を判定し、`has_todo`
    は `_get_todo_dates()` を引くだけ。docstring の「ファイルを開かないので
    軽い」も直した
- `src/ytsched/webroot/templates/main.html`
  - `<td>` に `my-mini-cal-day-holiday`（`d.is_holiday` または日曜）/
    `my-mini-cal-day-sat`（土曜）を、`d.in_month` のときだけ足す（前後の月の
    埋めセルには曜日の色を付けない仕様のため）
  - `.my-mini-cal-daynum` の下に `.my-mini-cal-marks` を作り、`has_sched` なら
    ドット（`has_important` なら `my-mini-cal-dot-important` を追加）、
    `has_todo` なら四角を、丸→四角の順で並べる
- `src/ytsched/webroot/static/css/my.css`
  - 背景色を優先度順（祝日・日曜 ＞ 土曜 ＞ 表示中の週 ＞ それ以外）で記述順に
    並べ直した。既定 `#F0F0F0`、表示中の週 `#FFF`（黄色 `#FFF6C0` から変更）、
    土曜 `#FFEEEE`、祝日・日曜 `#FFCCCC`
  - `.my-mini-cal-dot-important`（`#E33`）、`.my-mini-cal-sq`（4px 角、
    `#28F`）、`.my-mini-cal-marks`（丸と四角を横に並べる flex）を追加
- `tests/test_main_handler.py`
  - `TestMonthCal` に 5 件追加: `has_important` の判定、取り消し済みは
    `has_important` にならない、`is_holiday` の判定、ToDo 締切で `has_todo`
    は真・`has_sched` は偽、ToDo ファイルが無くても例外にならない
  - 既存の `test_has_sched_reflects_existing_files` の docstring を、実装が
    ファイルを開くようになったことに合わせて直した

対象範囲外（`week.js` や他のテンプレート・週表示側）は変更していない。

## 確認したこと

- `mise run fmt` / `typecheck` / `lint` すべて通過（`upgradeproject` は
  走らせていない）
- `mise run test` — 552 件全て pass（`126.39s`）
- `uv run ytsched webapp --datadir <一時ディレクトリ>` を起動し、`curl` で
  `/` が 200 を返すこと、レスポンスに `my-mini-cal-day` が含まれることを
  確認（見た目のキャプチャは撮っていない。verifier に任せる）

## 判断したこと

- 色・大きさの具体値は TODO.md の指示表にそのまま従った（着手時に決める
  としていた「薄いグレーの具体値」等は、依頼メッセージ側で既に
  `#F0F0F0` 等に確定していたのでそれを採用）
- `_todo_dates` を `SchedLoader` インスタンスの属性として持たせ、
  `load_month_cal()` を複数回呼んでも ToDo ファイルは 1 回しか読まない
  ようにした（依頼の指示どおり）
- `.my-mini-cal-day-cur-week` の適用条件（`d.in_month` を見ずに
  `w.monday` の範囲だけで判定）は既存のまま変えていない。前後の月の埋め
  セルが表示中の週に重なると背景が白になる可能性があるが、これは
  TODO-129 より前からの挙動で、依頼が「背景色の値」に限っていたため
  触っていない

## 残る懸念

- 見た目の実際の色・大きさのバランスはキャプチャで確認していない
  （verifier に依頼）

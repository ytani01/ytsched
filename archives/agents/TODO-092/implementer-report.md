# TODO-092 implementer 報告

I〜L を実装。挙動は変えていない。CSS / JS / docs は未変更。

## 変更ファイル

### src/ytsched/webroot/templates/base.html
- 2 行目 `{% set now = ... %}` を削除（K。どこからも参照なし）。

### src/ytsched/webroot/templates/sde.html
- 1 行目直後に Tornado コメント `{# ... #}` を追加（I）。J・K 後の状態で、
  `main.html` から宣言なしで使う 5 個（`sde` / `sched_date` / `today_flag` /
  `today` / `url_prefix`）と、名前空間共有のため `{% set %}` の位置を動かすと
  壊れる旨を記載。
- 3 行目 `{% set sde_count = sde_count + 1 %}` を削除（K）。
- ToDo の色分け判定（旧 13〜20 行）を `sde.todo_urgency(today)` を使う形に
  置換（J）。`_urgency` が空なら `my-sde-todo`、それ以外は
  `my-sde-todo-<urgency>`。
- `doGet(...)` から `cur_date` / `date_from` / `date_to` の 3 行を削除（K）。

### src/ytsched/webroot/templates/main.html
- `<!-- hidden params -->` の `id` 無し `cur_day` と `#search_n` を削除（K）。
  `#sde_align` / `#date_from` は残す。`form_search` / `form_filter` 内の
  `cur_day` も残す。
- `{% set sde_count = 0 %}` を削除（K）。`{% set year=0 %}` は 162 行で使うので残す。
- 【判断あり】検索バーの `{% set days = date_to - date_from + delta_day1 %}` を
  `+ date.resolution` に変更（下記）。

### src/ytsched/ytsched.py
- `SchedDataEnt` に `TODO_NEAR_DAYS = 7`（`TYPE_PREFIX_TODO` の隣）と
  `todo_urgency(self, today) -> str` を追加（J）。`over` / `near` / `""` を返す。
  `is_todo()` の判定はしない。

### src/ytsched/main_handler.py
- `DELTA_DAY1` 定数と `render()` の `delta_day1=` 引数を削除（J）。
- `get_date()` の `year`+`month`+`day` ブロックと docstring の記述を削除（L）。
- メソッド `str2ymd_date` / `ymd2date` を削除（L）。`check_int_range` /
  `check_date` は他が使うので残す（参照が壊れていないこと確認済み）。

### tests/test_ytsched.py
- `test_todo_urgency` を追加（parametrize 7 ケース: -7→over, -1→over, 0→near,
  6→near, 7→near, 8→'', 30→''）。`TODAY0` 固定、日付は `set_date()` で設定。

### tests/test_main_handler.py
- `test_year_month_day_beats_date` / `test_incomplete_year_month_day_is_ignored`
  / `test_year_month_day_beats_modified_date` を削除（L）。
- `TestDateOrder` の docstring から `year`+`month`+`day` を除去。

### tests/test_web.py
- 依頼リストの ymd 経路テスト 12 個を削除（L）。
- セクションコメント `# date / cur_day / year+month+day` →`# date / cur_day`。
- `# 数字・日付にはなるが…` コメントと `capture_log`（test_web.py 内で定義・
  他で使用）は残す。

## 単独で決めた判断

- **`delta_day1` に生きた参照が 1 つあった。** 依頼は「他に参照が無いことを
  grep で確かめてから消す」だったが、`main.html` の検索バー
  `{% set days = date_to - date_from + delta_day1 %}`（`(in N日)` 表示）で
  使われていた。同じブロックの 2 行上が既に `date.resolution`
  （＝`timedelta(days=1)`）を使っているので、それに合わせて
  `+ date.resolution` へ置換した。値は `datetime.timedelta(1)` と同一で
  表示は変わらない。これにより `DELTA_DAY1` / `delta_day1` は依頼どおり
  全廃できた。main の確認を仰ぎたい点。

## 自分で確かめたこと

- `mise run fmt` / `typecheck` / `lint`: すべて pass（ruff・basedpyright・mypy 問題なし）。
- `mise run test`: 474 passed（着手前は 482。差 -8 ＝ test_todo_urgency +7、
  ymd テスト削除 -15）。着手前の stash 実行では別テストが 1 件 flaky で落ちたが
  本変更とは無関係。
- `uv run ytsched webapp --datadir <一時dir>` を起動し
  `GET /ytsched/` → HTTP 200。出力に未展開の `{{` / `{%` なし。
  死んだ属性（`search_n` hidden / `cur_date` / `delta_day1`）の生き残りなし
  （`name="cur_day"` は `form_search` / `form_filter` の生きた 2 個のみ）。

## 残したもの（範囲外）

- なし。

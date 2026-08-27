# TODO-088 reviewer 報告

`git show HEAD:src/ytsched/main_handler.py` の分割前 `load_sched()` /
`load_todo()` / `mk_todo_by_date()` / `filter_match()` / `search_match()` /
`get()` を、`src/ytsched/sched_load.py` の `SchedLoader` / `main_handler.py`
の `get()` / `mk_weeks()` と 1 行ずつ突き合わせた。

## 依頼書の 9 点について

1. **検索の打ち切り** — `search()` の `if search_count > 0:` の中身
   （`search_n` 判定 → `date_from1` 判定の順、どちらも
   `date_from = date1; break`）は、分割前の `while` の同じ位置の分岐と
   完全に同じ構造。`date_from` の初期値
   （`date - timedelta(handler_util.SEARCH_MODE_MAX_DAYS)`）、
   1 件も当たらなかったときにその初期値のまま残る点も一致。
   `search_count` は `_load_day()` が返す `hit_count`（ファイルの
   `sdf.sde` を数えた分だけ）で、ToDo は数えていない
2. **1 件も当たらない日** — `_load_day()` の `out_sde` は「ファイル →
   `todo_by_date`（`todo_days_value >= 0` のときだけ）→ `extra_sde`」の
   順に足してから返す。`search()` は `_load_day()` に `extra_sde` を
   渡さないので、`todo_today_sde` は混ざらない。`if not day["sde"]:
   continue` は `todo_by_date` を足したあとの判定なので、ToDo だけ
   当たった日は検索でも残る（分割前の「ToDo を足したあとに
   `if not out_sde`」と同じ）
3. **並び順** — `load_week()` は月曜から日曜へ昇順に積むだけ、`search()`
   は分割前と同じく新しい日から古い日へ積んでから `sched[::-1]` で
   反転。1 日の中の `sde` の並びも「ファイル → `todo_by_date` →
   `extra_sde` を足してからソート」の順で分割前と一致
4. **`todo_today_sde`** — `load_week()` が `date1 == today` のときだけ
   `extra_sde` として渡し、しかも `_load_day()` 内で
   `todo_days_value >= 0` の分岐の内側でしか足さない（分割前も
   `if todo_days_value >= 0:` の内側で `if not search_mode and date1 ==
   today:` を見ていたのと同じ）
5. `todo_days_value < 0` のとき ToDo を混ぜない条件も上記のとおり保たれている
6. `sdf_exists()` によるファイルを開かない分岐は `_load_day()` に
   1 か所だけ残り、`load_week()`・`search()` の両方から通る
7. `SchedLoadCond` から外した `search_re`・`search_n`・`todo_sde` は、
   `grep` で確認したかぎり `main_handler.py` / `tests/test_main_handler.py`
   のどこからも参照されていない。分割前の `load_sched()` /
   `filter_match()` / `search_match()` / `MainHandler.SEARCH_MODE_DAYS` も
   `main_handler.py` に残っていない
8. `main.html` の変更は `data-monday` の行 1 行だけ。検索モードでも
   `mk_weeks()` が実在する月曜（`date - timedelta(date.weekday())`）を
   `monday` に入れるようにした上で、テンプレート側の条件を
   `{% if not search_mode %}` に変えているので、出力される HTML は
   分割前後で変わらない（通常モードは常に真の値で必ず出力、検索モードは
   常に出力されない）
9. `mk_weeks()` の通常モード分岐は、分割前の `get()` にあった
   `for offset in range(-weeks_n, weeks_n + 1)` をそのまま private
   メソッドへ移しただけで、範囲・`monday` の計算・`offset == 0` の
   ときだけ既に計算済みの `sched` を使う分岐も同一

いずれも確信度は高い。

## その他

テストの書き換え（`tests/test_main_handler.py`）も、`SchedLoadCond` /
`SchedLoader` / `SchedSearchCond` への差し替えのみで期待値は変えておらず、
`call_load_sched()` が `search_re` の有無で `search()`/`load_week()` を
呼び分ける形も依頼どおり。

指摘は無し。

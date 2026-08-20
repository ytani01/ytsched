# TODO-021 implementer(1) の報告 — 現状の挙動を押さえるテスト

## 結果

- **`src/` は 1 バイトも変えていない**（`git status` で確認）
- テストは **290 → 330（+40 件）**、全部通る
- `ruff format` / `ruff check --fix --extend-select I` / `basedpyright` /
  `mypy` / `pytest` すべて通っている

## 変更・作成したファイル

| ファイル | 内容 |
| --- | --- |
| `tests/test_main_handler.py`（新規） | `MainHandler` の現状の挙動を押さえるテスト 39 件 |
| `tests/test_handler.py`（追記のみ） | `test_settings_are_read` を 1 件足した。既存のテストは書き換えていない |

新しいファイルにしたのは、`tests/test_web.py` が既に 761 行あり、
「TODO-021 の足場」という位置づけをファイル単位で分けたほうが、
リファクタリング後に読み返しやすいと判断したため。`WebTestBase` /
`mk_dataline` / `DATE1` は `test_web.py` から import して使い回している
（`test_web.py` 側を書き換えたくなかったので、`helpers.py` へ移す案は
採らなかった）。

## 足したテストの一覧

日付の観測には、テンプレート `main.html` が 1 日につき 1 回だけ出す
`id="date-YYYY-MM-DD"` を使っている（検索モードでは、1 件も当たらな
かった日は欄ごと出ないので、この印が「その日が出たか」になる）。

### 1. 設定値の取り出し 4 か所の食い違い — `TestConfArgs`（9 件）

| テスト | 押さえていること |
| --- | --- |
| `test_empty_search_str_is_saved` | 空の `search_str` は「渡された」扱いで `SearchStr\t\n` が保存される |
| `test_empty_filter_str_is_not_saved` | 空の `filter_str` は「渡されていない」扱いで、`Conf.cgi` すら作られない |
| `test_empty_search_str_clears_saved_search_str` | 空の `search_str` は保存済みの検索語を消し、検索モードから抜ける |
| `test_empty_filter_str_keeps_saved_filter_str` | 空の `filter_str` では保存済みの絞り込みが**消えず、効き続ける** |
| `test_empty_search_n_is_an_error` | 空の `search_n` は `int("")` で **500**。ただし `SearchN\t\n` の保存だけは先に済んでいる |
| `test_empty_search_n_does_not_break_next_request` | 空で保存された `SearchN` は、次の表示では truthy でないので `DEF_SEARCH_N` に戻る |
| `test_empty_todo_days_is_ignored` | 空の `todo_days` は「渡されていない」扱いで、エラーにならず既定値になる |
| `test_search_str_is_saved_as_is_and_shown_lowered` | `Conf.cgi` には `ABC` のまま、画面には `abc`（小文字化は `set_conf()` のあと） |
| `test_filter_str_is_saved_as_is_and_shown_lowered` | 同上（`filter_str`） |

`search_str` / `search_n`（`is not None`）と
`todo_days` / `filter_str`（truthy）の差が、
**「`Conf.cgi` が作られるか」「保存済みの値が消えるか」「500 になるか」**
という形で外から見えるようにした。4 か所を 1 つにまとめるときは、
この 9 件が通るかどうかで差が残っているか分かる。

### 2. 検索モードの打ち切り条件 — `TestSearchModeRange`（8 件）

`DAYS = MainHandler.DEF_DAYS`(45)、基準日は `2021-03-15` 固定。

| テスト | 押さえていること |
| --- | --- |
| `test_normal_mode_range_is_days_before_and_after` | 検索しないときの範囲は `[date - 45, date + 44]`（境界の 4 日を確認） |
| `test_search_mode_stops_365_days_after_first_hit` | 1 件目のあとは、`SEARCH_MODE_DAYS` ちょうどの日は見て、その 1 日前は見ない |
| `test_search_mode_goes_beyond_365_days_until_first_hit` | 1 件も無いうちは 365 日を超えてさかのぼる（400 日前のものが出る） |
| `test_search_mode_max_days_when_nothing_is_found` | 1 件も無いときの `date_from` は 1825 日前（`SEARCH_MODE_MAX_DAYS`） |
| `test_search_n_stops_at_the_day_of_the_nth_hit` | `search_n=1` なら、1 件目の日で止まる（その日は出る） |
| `test_search_count_counts_sde_not_days` | 打ち切りは「日数」でなく「件数」（1 日に 3 件で `search_n=2` を超える） |
| `test_search_mode_does_not_show_days_after_date` | 検索モードでは `date` より先の日は見ない（`date_to = date`） |
| `test_search_mode_skips_days_without_hit` | 当たらなかった日の欄は出ない |

### 3. `exec_update()` の ToDo 完了時の補正 — `TestExecUpdateDeadline`（6 件）

| テスト | 押さえていること |
| --- | --- |
| `test_deadline_fixes_date_and_time_start` | `date` は今日、`time_start` は**秒・マイクロ秒が 0**、`time_end` は `None` |
| `test_deadline_prepends_a_line_to_detail` | `detail` の先頭が `〆2021/03/05 10:00-11:00\n`（`-` が `/` になる） |
| `test_deadline_without_times_keeps_the_space` | 時刻が両方空だと `〆2021/03/05 \n`（**末尾に空白が残る**） |
| `test_deadline_with_only_start_time` | 終了時刻が空なら `-` も付かない |
| `test_deadline_is_not_applied_to_todo_type` | `sde_type` が ToDo のままなら補正されず、`ToDo.jsonl` へ入る |
| `test_no_deadline_is_not_applied` | `deadline_date` が無ければ補正されない |

**`freezegun` などの外部依存は足していない。** 補正後の `time_start` は
`HH:MM` で保存されるので「秒が落ちている」ことがファイルからは見えない。
そこで `MainHandler.cmd_add` を `mock.patch.object` で包んで（元の実装は
そのまま呼ぶ）、渡ってきた `datetime.time` の `second` / `microsecond` が
0 であることを直接見ている。時刻そのものは、POST の前後で取った
`datetime.now()` のどちらかの `HH:MM` と一致すること、で確かめている
（分をまたいでも、日付をまたいでも落ちない書き方にした）。

### 4. 日付の決定順 — `TestDateOrder`（8 件）

| テスト | 押さえていること |
| --- | --- |
| `test_cur_day_is_used_when_date_is_missing` | `date` が無ければ `cur_day` |
| `test_empty_date_falls_back_to_cur_day` | `date=`（空）は「無し」扱い |
| `test_date_beats_cur_day` | `date` は `cur_day` より強い |
| `test_year_month_day_beats_date` | `year`+`month`+`day` は `date` より強い |
| `test_incomplete_year_month_day_is_ignored` | 3 つのうち 1 つでも欠けると無視（3 通りとも確認） |
| `test_no_argument_is_today` | どれも無ければ今日 |
| `test_modified_date_beats_date_argument` | ToDo 完了で `modified_date` が今日になり、`date` 引数を上書きする |
| `test_year_month_day_beats_modified_date` | `year`+`month`+`day` は `modified_date` より強い（データは `date` 引数の日に書かれ、表示だけ動く） |
| `test_todo_add_moves_to_the_deadline_date` | ToDo を足すと `exec_update()` は `None` を返すが、`get()` が `sde.date`（期限）で入れ直す |

### 5. ToDo の表示条件 — `TestTodoDisplay`（7 件）

| テスト | 押さえていること |
| --- | --- |
| `test_todo_days_off_hides_todo_completely` | `todo_days` が負なら、期限の日にも ToDo は出ない（ブロックごと飛ぶ） |
| `test_todo_is_shown_on_its_deadline` | `todo_days=0` でも、期限の日には出る |
| `test_todo_days_boundary_is_inclusive` | 期限が `today + todo_days` ちょうどなら今日の欄に出る（`>` であって `>=` でない） |
| `test_todo_one_day_over_the_boundary_is_not_shown` | 1 日先だと出ない |
| `test_todo_due_today_is_shown_once` | 期限が今日の ToDo は 1 回だけ（`sde.date == today` の `continue` があるので二重にならない） |
| `test_overdue_todo_is_shown_on_today` | 期限切れの ToDo は今日の欄に出る |
| `test_todo_today_is_not_merged_in_search_mode` | 検索モードでは `todo_today_sde` を混ぜない（同じ ToDo が、検索しなければ出て、検索すると出ない） |

### `handler.py`（`tests/test_handler.py` に 1 件追記）

- `test_settings_are_read` — `HandlerBase.__init__` が `app.settings` から
  読む 8 つ（`_title` `_author` `_version` `_url_prefix` `_datadir`
  `_days` `_sd` `_conf_file`）。TODO-021 の D「`app.settings.get()` の
  繰り返し」をまとめても、この 8 つは変わらないはず

## 自分で確かめたこと

1. **`uv run pytest tests` = 330 passed**（ベースライン 290 + 40）
2. **`src/` が変わっていないこと** を `git status --porcelain src` で確認
3. **足したテストが本当に効くか**を、`src/` を一時的に書き換えて
   （実行後に必ず元へ戻した）確かめた。**16 通り試して、すべて
   新しいテストのどれかが落ちた**。書き換えた条件と、落ちたテスト:

   | 書き換え | 落ちたテスト（新規分） |
   | --- | --- |
   | `search_str is not None` → truthy | `test_empty_search_str_is_saved` 他 |
   | `search_n_str is not None` → truthy | `test_empty_search_n_is_an_error` |
   | `if filter_str:` → `is not None` | `test_empty_filter_str_is_not_saved` 他 |
   | `if todo_days_str:` → `is not None` | `test_empty_todo_days_is_ignored` |
   | `date1 <= date_from1` → `<` | `test_search_mode_stops_365_days_after_first_hit` |
   | `search_count >= search_n` → `>` | `test_search_n_stops_at_the_day_of_the_nth_hit` |
   | `search_mode and search_count > 0` → `search_mode` | `test_search_mode_goes_beyond_365_days_until_first_hit` 他 |
   | `SEARCH_MODE_MAX_DAYS` を 2 倍 | `test_search_mode_max_days_when_nothing_is_found` |
   | `date + (self._days - 1)` → `self._days` | `test_normal_mode_range_is_days_before_and_after` |
   | `sde.date > today + …` → `>=` | `test_todo_days_boundary_is_inclusive` |
   | `todo_days_value >= 0` → `> 0` | `test_todo_is_shown_on_its_deadline` 他 |
   | `sde.date == today: continue` を外す | `test_todo_due_today_is_shown_once` |
   | `not search_mode and …` → `…` | `test_todo_today_is_not_merged_in_search_mode` |
   | `deadline_date_str and not type_is_todo(...)` → `deadline_date_str` | `test_deadline_is_not_applied_to_todo_type` |
   | `strftime("%H:%M")` → `"%H:%M:%S"` | `test_deadline_fixes_date_and_time_start` |
   | `year and month and day` → `or` | `test_incomplete_year_month_day_is_ignored` |

   最後に `git status --porcelain src` が空であることを確認済み。

## 単独で決めた判断

1. **新しいファイル `tests/test_main_handler.py` を作った。**
   `test_web.py` は既に 761 行あり、「TODO-021 の足場」という位置づけを
   ファイル単位で分けたほうが、リファクタリング後に読み返しやすい。
   既存ファイルは 1 行も書き換えていない（`test_handler.py` は追記のみ）
2. **`test_web.py` から `WebTestBase` などを import した。**
   `helpers.py` へ移すには `test_web.py` を書き換える必要があり、
   依頼の「既存テストは書き換えない」に反するため
3. **`freezegun` は足さなかった。** `cmd_add()` を `mock.patch.object` で
   包んで引数を見る形にすれば、`second == 0` を直接確かめられた
4. **`ytsched.py`（TODO-021 の C）には何も足していない。**
   `is_important()` / `is_canceled()` / `is_todo()` / `type_is_todo()` /
   `get_timestr()` / `load()` は `tests/test_ytsched.py` に既に
   パラメタライズ済みのテストがあり（空文字・全角括弧・時刻 4 通り・
   壊れた行の書き戻しまで）、足すと重複になる。**リファクタリングの
   足場としては既存分で足りる**と判断した
5. **`else: pass` と空の `DataFileApp.end()`（TODO-021 の E）にも
   何も足していない。** 消しても挙動が変わらないもの＝
   テストで押さえる中身が無いため

## 気づいたが、直さずに残したもの

**どれも「挙動を変えない」TODO-021 の範囲外**なので、そのままにして
現状の挙動をテストに書き留めてある。直すなら別項目。

1. **`search_n=`（空）で 500 になる。**（TODO-021 の A の範囲）
   `search_n` は `is not None` で分岐するので、空文字がそのまま
   `int("")` へ渡って `ValueError` → 500。しかも
   `set_conf(SearchN, "")` は**先に済んでいる**ので、`Conf.cgi` には
   空の `SearchN` が残る。次のリクエストでは空文字が truthy でないので
   既定値へ落ち、画面は直る。`todo_days` は truthy 分岐なので同じことは
   起きない。→ `test_empty_search_n_is_an_error` /
   `test_empty_search_n_does_not_break_next_request`
2. **空の `filter_str` では、保存済みの絞り込みを消せない。**
   （同 A の範囲）`search_str` は空で送ると消えるのに、`filter_str` は
   `Conf.cgi` の値へ落ちて効き続ける。画面から絞り込みを解除する手段が
   `search_str` と揃っていない。→ `test_empty_filter_str_keeps_saved_filter_str`
3. **`detail` の `〆` 行に、余分な空白が残ることがある。**（同 B の範囲）
   `deadline_time_start` も `deadline_time_end` も空だと
   `"〆2021/03/05 \n…"` になり、末尾に空白が 1 つ付く。
   → `test_deadline_without_times_keeps_the_space`
4. **`Conf.cgi` には元の大文字小文字が残り、画面は小文字になる。**
   （同 A の範囲）`set_conf()` が `lower()` の前にあるため。
   `ABC` と入力して再読み込みすると、入力欄が `abc` に変わる。
   → `test_search_str_is_saved_as_is_and_shown_lowered`
5. **検索モードで 1 件も当たらないと、1825 日ぶんスキャンする。**
   365 日の打ち切りは `search_count > 0` の中にあるので、1 件目が
   見つかるまで効かない。1825 回ぶんファイルを開きにいく。
   （速度の話で、挙動としては正しい）
   → `test_search_mode_goes_beyond_365_days_until_first_hit`
6. **`year` `month` `day` に数字でない値を渡すと 500。**（同 A の範囲）
   `datetime.date(int(year), …)` に検証が無い。`day=0` でも 500。
   テストにはしていない（現状の挙動を押さえる用途としては、上の 1 で
   同じ性質を押さえてあるため）

## うまくいかなかったところ

特に無い。押さえられなかった挙動も無い（依頼の 5 項目はすべて
テストにした）。

一点だけ書いておくと、**補正後の `time_start` を「ファイルの中身だけ」で
確かめることはできない**（保存が `HH:MM` なので秒は元から出ない）。
`cmd_add()` を包む形にしたのはそのため。リファクタリングで
`exec_update()` を分割するとき、`cmd_add()` の**引数の並び**
（`sde_id, date, time_start, time_end, sde_type, title, place, detail` の
位置引数 8 つ）を変えると `test_deadline_fixes_date_and_time_start` が
落ちる。挙動は変わっていないので、そのときは**テストの側を直してよい**。

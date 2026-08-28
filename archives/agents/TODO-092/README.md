# TODO-092 の分担

|      | main | 担当 |
|------|------|------|
| 見込み | Sonnet 5 / effort medium | implementer + verifier |

## なぜこの分担か

`base.html` / `main.html` / `sde.html` / `main_handler.py` / `ytsched.py` と、
`tests/test_ytsched.py` / `tests/test_main_handler.py` / `tests/test_web.py`
にまたがる。テンプレートの変数の流れ、ハンドラのメソッド削除、テストの
削除がまとまって要るので、実装は `implementer` に分ける。挙動は変えない
（I はコメントの追加、J は判定の置き場所を移すだけ、K・L は死んだコードの
削除）ので、TODO-017 の基準では `reviewer` は入れない。確認は
`~/.claude/CLAUDE.md` の決まりどおり `verifier` を別に立てる。

## main が決めたこと（着手前）

- **I のコメントは、J・K を反映した後の状態を書く。** `main.html` から
  `sde.html` へ渡っているのは、掃除後は `sde` / `sched_date` /
  `today_flag` / `today` / `url_prefix` の 5 個。掃除前の 10 個
  （`delta_day1` / `date` / `date_from` / `date_to` / `sde_count`）は
  この項目で消える。
- **J の移し先は `SchedDataEnt.todo_urgency(today)`。** 戻り値は
  `"over"`（期限を過ぎた）/ `"near"`（1 週間以内）/ `""`（それ以外）。
  「1 週間」は `TODO_NEAR_DAYS = 7` をクラス定数にする。テンプレート側は
  `"" ` のとき `my-sde-todo`、それ以外は `my-sde-todo-<戻り値>`。CSS は
  触らない（`my-sde-todo-normal` は作らない）。`main_handler.py` の
  `DELTA_DAY1` は J のあと参照されなくなるので一緒に消す。
- **K で消すのは死んでいるものだけ。** `#sde_align` / `#date_from` は
  `main-page.js` が読むので残す。`form_search` / `form_filter` の中の
  `cur_day` も POST で送るので残す。消すのは `<!-- hidden params -->` の
  中の `id` の無い `cur_day` と、`#search_n`（読む JS が無い）。
- **L は「テストごと消す」。** `year`+`month`+`day` の経路と
  `ymd2date()` / `str2ymd_date()` を消し、それだけを見ているテストも
  消す。`check_int_range()` / `check_date()` は他が使うので残す。

## 報告

- [implementer-report.md](implementer-report.md)
- [verifier-report.md](verifier-report.md)
- [wording-report.md](wording-report.md)

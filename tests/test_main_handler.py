#
# (c) 2026 ytani01
#
"""``MainHandler`` の現状の挙動を押さえるテスト（TODO-021）

TODO-021 のリファクタリングは「挙動を一切変えない」のが前提。
ここに書いてあるのは「こうあるべき」ではなく「**いまこう動く**」で、
**リファクタリングでここが壊れたら、それは挙動が変わった印**。

``tests/test_web.py`` の表示・更新のテストと重ならないよう、これから
分割・整理される次の 5 か所に絞ってある。

1. 設定値の取り出し 4 か所（``search_str`` / ``todo_days`` /
   ``filter_str`` / ``search_n``）の、条件の食い違い
2. 検索モードの打ち切り条件
3. ``exec_update()`` の ToDo 完了時の補正
4. 日付の決定順
5. ToDo の表示条件

6 番目の「ファイルが無い日を開かない」（TODO-028）だけは、挙動を
**変えない**ための確認なので、押さえ方が他と違う（変更前と同じ結果に
なるかを、その場で突き合わせる）。

日付は ``id="date-YYYY-MM-DD"`` で見る（1 日につき 1 回だけ出る）。
検索モードでは、1 件も見つからなかった日は出ないので、この印が
「その日が出たかどうか」になる。
"""

import datetime
import json
import re
from typing import Any, cast
from unittest import mock
from urllib.parse import urlencode

from helpers import URL_PREFIX, app_sd, make_app, make_handler
from test_web import (
    DATE1,
    DATE1_STR,
    WebTestBase,
    date_id,
    day_block,
    mk_dataline,
    week_panel,
)

from ytsched import handler_util
from ytsched.main_binder import MainBinder
from ytsched.main_handler import MainHandler
from ytsched.sched_load import SchedLoadCond, SchedLoader, SchedSearchCond
from ytsched.sched_update import SchedUpdater
from ytsched.ytsched import SchedData

CONF_FNAME = "conf.json"


def test_cookie_todo_days_is_removed():
    """使われていない ``COOKIE_TODO_DAYS`` は消した（TODO-028）。

    どこからも参照されていない定数だった。同じものを足し直さない
    ための覚え書き。
    """
    assert not hasattr(MainHandler, "COOKIE_TODO_DAYS")


def test_binder_update_conf_args_returns_and_saves_all_four(tmp_path):
    """``MainBinder.update_conf_args()`` が 4 つの値を ``ConfArgs`` にまとめて
    返し、``conf.json`` へも反映する（C・TODO-090）。
    """
    datadir = tmp_path / "data"
    datadir.mkdir()
    app = make_app(datadir)

    handler = make_handler(
        app,
        MainHandler,
        uri=(
            URL_PREFIX
            + "/?"
            + urlencode(
                {
                    "search_str": "ABC",
                    "filter_str": "DEF",
                    "todo_days": "3",
                    "search_n": "9",
                }
            )
        ),
    )

    conf_args = MainBinder(cast(Any, handler)).update_conf_args()

    assert conf_args.search_str == "abc"
    assert conf_args.filter_str == "def"
    assert conf_args.todo_days_value == 3
    assert conf_args.search_n == 9

    handler.on_finish()

    conf_data = json.loads((datadir / CONF_FNAME).read_text(encoding="utf-8"))
    assert conf_data == {
        "SearchStr": "abc",
        "FilterStr": "def",
        "ToDo_Days": "3",
        "SearchN": "9",
    }


#
# 1. 設定値の取り出し 4 か所の、条件の食い違い
#
class TestConfArgs(WebTestBase):
    """設定値の取り出し 4 か所の、空文字の扱い。

    ``search_str``/``filter_str``/``search_n`` は ``is not None`` で、
    ``todo_days`` だけ truthy で分岐する（``empty_is_given``）。
    差が出るのは空文字を渡したときだけなので、``conf.json`` の中身と
    画面で押さえる。

    ``filter_str`` は TODO-028 で ``search_str`` と揃えた。空文字を
    送れば絞り込みが解除される。

    ``search_n`` の ``convert`` は ``int``、``todo_days`` の
    ``convert`` は ``str2todo_days()``（中で ``int()`` を呼ぶ）で、
    どちらも ``int('')`` が必ず失敗して「渡されていない」のと同じ
    扱いになる（TODO-027）ため、この 2 か所は空文字が分岐に入っても
    入らなくても結果が変わらない。
    """

    def conf_data(self):
        """``conf.json`` の中身。ファイルが無ければ ``None``。"""
        path = self.datadir / CONF_FNAME
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    def test_empty_search_str_is_saved(self):
        """空の ``search_str`` は「渡された」扱いで、保存される。"""
        self.get_body(URL_PREFIX + "/", date=DATE1_STR, search_str="")

        assert self.conf_data() == {"SearchStr": ""}

    def test_empty_filter_str_is_saved(self):
        """空の ``filter_str`` は「渡された」扱いで、保存される。

        TODO-028 で ``search_str`` と揃えた。
        """
        self.get_body(URL_PREFIX + "/", date=DATE1_STR, filter_str="")

        assert self.conf_data() == {"FilterStr": ""}

    def test_empty_search_str_clears_saved_search_str(self):
        """空の ``search_str`` は、保存済みの検索語を消す。"""
        self.write_data(DATE1, [mk_dataline(), mk_dataline(sde_id="id-2")])
        self.get_body(URL_PREFIX + "/", date=DATE1_STR, search_str="会議室")

        body = self.get_body(URL_PREFIX + "/", date=DATE1_STR, search_str="")

        assert self.conf_data() == {"SearchStr": ""}
        # 検索モードから抜けるので、検索期間・件数のバーは出ない
        assert "目標件数" not in body

    def test_empty_filter_str_clears_saved_filter_str(self):
        """空の ``filter_str`` は、保存済みの絞り込みを解除する。

        TODO-028 の前は「渡されていない」扱いで ``conf.json`` の値へ
        落ちてしまい、**絞り込みを解除できなかった**。
        """
        self.write_data(
            DATE1,
            [
                mk_dataline(),
                mk_dataline(sde_id="id-2", title="歯医者", place="病院"),
            ],
        )
        self.get_body(URL_PREFIX + "/", date=DATE1_STR, filter_str="病院")

        body = self.get_body(URL_PREFIX + "/", date=DATE1_STR, filter_str="")

        assert self.conf_data() == {"FilterStr": ""}
        assert "歯医者" in body
        assert "定例ミーティング" in body

    def test_empty_search_n_is_not_saved(self):
        """空の ``search_n`` は ``int('')`` にならず、保存もされない。

        ``is not None`` で分岐するので空文字がそのまま ``int()`` へ
        渡るが、数字として読めないので「渡されていない」のと同じ扱いに
        なる（TODO-027）。**以前はここで 500 になり、空のまま
        ``conf.json`` に残っていた**。
        """
        res = self.fetch(
            URL_PREFIX + "/?" + urlencode({"date": DATE1_STR, "search_n": ""})
        )

        assert res.code == 200
        assert self.conf_data() is None

    def test_empty_search_n_does_not_break_next_request(self):
        """空の ``search_n`` のあとも、次の表示は既定値のまま。"""
        self.fetch(
            URL_PREFIX + "/?" + urlencode({"date": DATE1_STR, "search_n": ""})
        )

        body = self.get_body(
            URL_PREFIX + "/", date=DATE1_STR, search_str="会議"
        )

        assert f'value="{MainHandler.DEF_SEARCH_N}" selected' in body

    def test_empty_todo_days_is_ignored(self):
        """空の ``todo_days`` は「渡されていない」扱いで、既定値になる。

        ``search_n`` と違って ``int('')`` を試すところまで行かない。
        """
        self.get_body(URL_PREFIX + "/", date=DATE1_STR, todo_days="")

        assert self.conf_data() is None

    def test_search_str_is_saved_normalized(self):
        """``search_str`` は、保存も表示も ``normalize()`` 後（TODO-029）。

        TODO-029 の前は ``conf.json`` へ元のまま入り、小文字化は
        ``set_conf()`` の**あと**だった。
        """
        body = self.get_body(
            URL_PREFIX + "/", date=DATE1_STR, search_str="ABC"
        )

        assert self.conf_data() == {"SearchStr": "abc"}
        assert 'value="abc"' in body

    def test_search_str_zenkaku_paren_is_normalized(self):
        """全角括弧は半角になる（TODO-029）。"""
        body = self.get_body(
            URL_PREFIX + "/", date=DATE1_STR, search_str="（重要）"
        )

        assert self.conf_data() == {"SearchStr": "(重要)"}
        assert 'value="(重要)"' in body

    def test_filter_str_is_saved_normalized(self):
        """``filter_str`` は、保存も表示も ``normalize()`` 後。

        小文字にするのは TODO-028、全角括弧の半角化は TODO-029。
        """
        body = self.get_body(
            URL_PREFIX + "/", date=DATE1_STR, filter_str="ABC（重要）"
        )

        assert self.conf_data() == {"FilterStr": "abc(重要)"}
        assert 'value="abc(重要)"' in body

    def test_saved_filter_str_is_not_rewritten_when_unchanged(self):
        """同じ ``filter_str`` を送り直しても、小文字のまま。"""
        self.get_body(URL_PREFIX + "/", date=DATE1_STR, filter_str="ABC")
        self.get_body(URL_PREFIX + "/", date=DATE1_STR, filter_str="abc")

        assert self.conf_data() == {"FilterStr": "abc"}


#
# 2. 検索モードの打ち切り条件
#
class TestSearchModeRange(WebTestBase):
    """検索モードで、どこまでさかのぼるか。

    ``SEARCH_ENOUGH_DAYS``（365）の境界をまたぐ位置にデータを置いて
    確かめる。``BASE`` は月曜（TODO-049）。
    """

    BASE = datetime.date(2021, 3, 15)
    KEYWORD = "けんさく"

    def write_hits(self, date, n=1):
        """``KEYWORD`` に当たる予定を ``n`` 件、その日付に書く。"""
        lines = [
            mk_dataline(
                sde_id=f"id-{date}-{i}",
                date=date.isoformat(),
                place=self.KEYWORD,
            )
            for i in range(n)
        ]
        self.write_data(date, lines)

    def search(self, search_n, date=None):
        """検索モードで表示して、本文を返す。"""
        return self.get_body(
            URL_PREFIX + "/",
            date=(date or self.BASE).isoformat(),
            search_str=self.KEYWORD,
            search_n=str(search_n),
        )

    def test_normal_mode_range_is_the_week_of_date(self):
        """検索しないときの範囲は、``date`` を含む週の月曜〜日曜
        （TODO-049）。

        検索モードでないので、予定が無い日も欄が出る。``BASE`` は月曜。
        """
        body = self.get_body(URL_PREFIX + "/", date=self.BASE.isoformat())
        # 前後の週も DOM にあるので、いま見ている週の中だけを見る
        # (TODO-069)
        panel = week_panel(body)

        day = datetime.timedelta(1)
        assert date_id(self.BASE - day) not in panel
        assert date_id(self.BASE) in panel
        assert date_id(self.BASE + day * 6) in panel
        assert date_id(self.BASE + day * 7) not in panel

    def test_normal_mode_range_starts_at_monday_when_date_is_monday(self):
        """月曜を指定したとき、その日が ``date_from`` になる（TODO-049）。"""
        body = self.get_body(URL_PREFIX + "/", date=self.BASE.isoformat())

        assert f'data-monday="{self.BASE}"' in body

    def test_normal_mode_range_goes_back_to_monday_when_date_is_sunday(self):
        """日曜を指定したとき、その週の月曜まで戻る
        （``date_from`` が 6 日前。TODO-049）。
        """
        sunday = self.BASE + datetime.timedelta(6)
        body = self.get_body(URL_PREFIX + "/", date=sunday.isoformat())

        assert f'data-monday="{self.BASE}"' in body

    def test_normal_mode_range_is_seven_days_across_year_boundary(self):
        """年をまたぐ週でも 7 日ちょうど（TODO-049）。"""
        monday = datetime.date(2025, 12, 29)
        sunday = datetime.date(2026, 1, 4)

        body = self.get_body(URL_PREFIX + "/", date=monday.isoformat())
        panel = week_panel(body)

        assert f'data-monday="{monday}"' in body
        assert date_id(monday) in panel
        assert date_id(sunday) in panel
        assert date_id(sunday - datetime.timedelta(1)) in panel
        assert date_id(monday - datetime.timedelta(1)) not in panel
        assert date_id(sunday + datetime.timedelta(1)) not in panel

    def test_search_mode_stops_365_days_after_first_hit(self):
        """1 件目が見つかったあとは、365 日前まででやめる。

        ``SEARCH_ENOUGH_DAYS`` ちょうどの日は見るが、その 1 日前は
        見ない。
        """
        day = datetime.timedelta(1)
        limit = day * SchedLoader.SEARCH_ENOUGH_DAYS

        self.write_hits(self.BASE)
        self.write_hits(self.BASE - limit)
        self.write_hits(self.BASE - limit - day)

        body = self.search(search_n=10)

        assert date_id(self.BASE) in body
        assert date_id(self.BASE - limit) in body
        assert date_id(self.BASE - limit - day) not in body

    def test_search_mode_goes_beyond_365_days_until_first_hit(self):
        """1 件も見つかっていないうちは、365 日を超えてさかのぼる。

        打ち切りの判定は ``search_count > 0`` の中にあるので、
        1 件目までは ``SEARCH_HARD_LIMIT_DAYS`` まで探し続ける。
        """
        old = self.BASE - datetime.timedelta(400)
        self.write_hits(old)

        body = self.search(search_n=10)

        assert date_id(old) in body

    def test_search_mode_max_days_when_nothing_is_found(self):
        """1 件も無いときは ``SEARCH_HARD_LIMIT_DAYS`` までさかのぼる。

        ``date_from`` が縮まないので、``#week_wrap`` の ``data-monday`` が
        1825 日前のままになる。
        """
        body = self.search(search_n=10)

        date_from = self.BASE - datetime.timedelta(
            handler_util.SEARCH_HARD_LIMIT_DAYS
        )
        assert f'data-monday="{date_from}"' in body

    def test_search_n_stops_at_the_day_of_the_nth_hit(self):
        """``search_n`` 件見つかった日でやめる（その日は出る）。"""
        day = datetime.timedelta(1)
        self.write_hits(self.BASE)
        self.write_hits(self.BASE - day)

        body = self.search(search_n=1)

        assert date_id(self.BASE) in body
        assert date_id(self.BASE - day) not in body

    def test_search_count_counts_sde_not_days(self):
        """打ち切りの数は「日数」ではなく「件数」で数える。

        1 日に 3 件あれば、その 1 日で ``search_n=2`` を超える。
        """
        day = datetime.timedelta(1)
        self.write_hits(self.BASE - day, n=3)
        self.write_hits(self.BASE - day * 2)

        body = self.search(search_n=2)

        assert date_id(self.BASE - day) in body
        assert date_id(self.BASE - day * 2) not in body

    def test_search_mode_does_not_show_days_after_date(self):
        """検索モードでは ``date`` より先の日は見ない。"""
        day = datetime.timedelta(1)
        self.write_hits(self.BASE)
        self.write_hits(self.BASE + day)

        body = self.search(search_n=10)

        assert date_id(self.BASE) in body
        assert date_id(self.BASE + day) not in body

    def test_search_mode_skips_days_without_hit(self):
        """検索モードでは、当たらなかった日の欄は出ない。"""
        day = datetime.timedelta(1)
        self.write_hits(self.BASE)

        body = self.search(search_n=10)

        assert date_id(self.BASE) in body
        assert date_id(self.BASE - day) not in body


#
# 3. exec_update() の ToDo 完了時の補正
#
class TestExecUpdateDeadline(WebTestBase):
    """``deadline_date`` が渡されたときの補正

    ``deadline_date`` があり、かつ ``sde_type`` が ToDo **でない**
    ときだけ、``date`` が今日・``time_start`` が現在時刻になり、
    ``detail`` の先頭へ ``〆…`` の 1 行が足される。
    """

    def read_json(self, date):
        """その日のデータファイルの 1 行目を dict で返す。"""
        line = (
            self.data_path(date).read_text(encoding="utf-8").splitlines()[0]
        )
        return json.loads(line)

    def post_done(self, **override):
        """ToDo 完了の POST（引数は上書きできる）。"""
        args = {
            "cmd": "add",
            "sde_id": "",
            "date": DATE1_STR,
            "time_start": "09:05",
            "time_end": "10:30",
            "sde_type": "会議",
            "title": "ノートを買う",
            "place": "",
            "detail": "詳細",
            "deadline_date": "2021-03-05",
            "deadline_time_start": "10:00",
            "deadline_time_end": "11:00",
        }
        args.update(override)
        return self.post_body(URL_PREFIX + "/", **args)

    def spy_cmd_add(self):
        """``cmd_add()`` に渡る引数を覚えるパッチ。

        補正後の ``time_start`` は ``HH:MM`` で保存されるので、
        「秒以下が落ちている」ことはファイルからは見えない。
        ``cmd_add()`` の引数で見る。
        """
        calls = []
        orig = SchedUpdater.cmd_add

        def spy(updater, *args):
            calls.append(args)
            return orig(updater, *args)

        return calls, mock.patch.object(SchedUpdater, "cmd_add", spy)

    def test_deadline_fixes_date_and_time_start(self):
        """``date`` は今日、``time_start`` は秒以下を落とした現在時刻。

        ``time_end`` は捨てられて ``None`` になる。
        """
        calls, patch = self.spy_cmd_add()
        before = datetime.datetime.now()
        with patch:
            self.post_done()
        after = datetime.datetime.now()

        (_sde_id, date, time_start, time_end, *_rest) = calls[0]

        assert date == datetime.date.today()
        assert time_start.second == 0
        assert time_start.microsecond == 0
        # 分をまたいだ場合もあるので、前後どちらかと一致すればよい
        assert time_start.strftime("%H:%M") in (
            before.strftime("%H:%M"),
            after.strftime("%H:%M"),
        )
        assert time_end is None

    def test_deadline_prepends_a_line_to_detail(self):
        """``detail`` の先頭へ ``〆{日付} {開始}-{終了}`` が足される。

        日付の区切りは ``-`` から ``/`` に変わる。
        """
        self.post_done()

        data = self.read_json(datetime.date.today())
        assert data["detail"] == "〆2021/03/05 10:00-11:00\n詳細"

    def test_deadline_without_times_has_no_trailing_space(self):
        """時刻が空なら、区切りの空白も付かない（TODO-028）。"""
        self.post_done(deadline_time_start="", deadline_time_end="")

        data = self.read_json(datetime.date.today())
        assert data["detail"] == "〆2021/03/05\n詳細"

    def test_deadline_with_only_end_time(self):
        """開始時刻だけが空なら、空白は付いたままになる。

        ``-11:00`` と時刻の部分が空でないため。
        """
        self.post_done(deadline_time_start="")

        data = self.read_json(datetime.date.today())
        assert data["detail"] == "〆2021/03/05 -11:00\n詳細"

    def test_deadline_with_only_start_time(self):
        """終了時刻が空のときは ``-`` も付かない。"""
        self.post_done(deadline_time_end="")

        data = self.read_json(datetime.date.today())
        assert data["detail"] == "〆2021/03/05 10:00\n詳細"

    def test_deadline_is_not_applied_to_todo_type(self):
        """``sde_type`` が ToDo のままなら、補正されない。

        ToDo として ``ToDo.jsonl`` へ入り、``date`` も ``detail`` も
        ``time_end`` もそのまま。
        """
        self.post_done(sde_type="□買い物")

        assert not self.data_path(datetime.date.today()).exists()

        line = (
            (self.datadir / "ToDo.jsonl")
            .read_text(encoding="utf-8")
            .rstrip("\n")
        )
        data = json.loads(line)
        assert data["date"] == DATE1_STR
        assert data["time_start"] == "09:05"
        assert data["time_end"] == "10:30"
        assert data["detail"] == "詳細"

    def test_no_deadline_is_not_applied(self):
        """``deadline_date`` が無ければ、補正されない。"""
        self.post_done(
            deadline_date="",
            deadline_time_start="",
            deadline_time_end="",
        )

        data = self.read_json(DATE1)
        assert data["date"] == DATE1_STR
        assert data["time_start"] == "09:05"
        assert data["time_end"] == "10:30"
        assert data["detail"] == "詳細"


#
# 4. 日付の決定順
#
class TestDateOrder(WebTestBase):
    """``get()`` の「set Date」ブロックで、どれが勝つか。

    ``cur_day`` → ``date`` → ``modified_date`` の順に上書きされる
    （後のものが勝つ）。
    ``DAYS`` は 1 なので、出る日は ``date`` とその前日だけ。
    """

    def test_cur_day_is_used_when_date_is_missing(self):
        """``date`` が無ければ ``cur_day``。"""
        body = self.get_body(URL_PREFIX + "/", cur_day="2020-01-15")

        assert date_id(datetime.date(2020, 1, 15)) in body

    def test_empty_date_falls_back_to_cur_day(self):
        """``date=``（空）は「無し」扱いで、``cur_day`` になる。"""
        body = self.get_body(URL_PREFIX + "/", date="", cur_day="2020-01-15")

        assert date_id(datetime.date(2020, 1, 15)) in body

    def test_date_beats_cur_day(self):
        """``date`` は ``cur_day`` より強い。"""
        body = self.get_body(
            URL_PREFIX + "/", date=DATE1_STR, cur_day="2020-01-15"
        )

        assert date_id(DATE1) in body
        assert date_id(datetime.date(2020, 1, 15)) not in body

    def test_no_argument_is_today(self):
        """どれも無ければ今日。"""
        body = self.get_body(URL_PREFIX + "/")

        assert date_id(datetime.date.today()) in body

    def test_modified_date_beats_date_argument(self):
        """``modified_date`` は ``date`` 引数を上書きする。

        ToDo 完了（``deadline_date`` あり・種別は ToDo でない）だと、
        ``date`` 引数が ``2021-03-01`` でも、表示は今日に移る。
        """
        body = self.post_body(
            URL_PREFIX + "/",
            cmd="add",
            sde_id="",
            date=DATE1_STR,
            sde_type="会議",
            title="ノートを買う",
            place="",
            detail="",
            deadline_date="2021-03-05",
        )

        assert date_id(datetime.date.today()) in body
        assert date_id(DATE1) not in body

    def test_todo_add_moves_to_the_deadline_date(self):
        """ToDo を足すと、その期限の日付が表示される。

        ``exec_update()`` は ToDo だと ``None`` を返すが、
        ``get()`` が ``sde.date``（期限）で入れ直す。
        """
        body = self.post_body(
            URL_PREFIX + "/",
            cmd="add",
            sde_id="",
            date=DATE1_STR,
            sde_type="□買い物",
            title="ノートを買う",
            place="",
            detail="",
        )

        assert date_id(DATE1) in body


#
# 5. ToDo の表示条件
#
class TestTodoDisplay(WebTestBase):
    """ToDo が「今日の欄」に出る条件

    ``todo_days_value >= 0`` のときだけ ToDo を混ぜる。
    期限が ``today + todo_days_value`` より先のものと、期限が
    ちょうど今日のものは ``todo_today_sde`` に入らない。
    検索モードでは ``todo_today_sde`` を混ぜない。
    """

    TITLE = "ノートを買う"

    def write_todo(self, deadline):
        """期限 ``deadline`` の ToDo を 1 件書く。"""
        line = mk_dataline(
            sde_id="id-t",
            date=deadline.isoformat(),
            time_start=None,
            time_end=None,
            type="□買い物",
            title=self.TITLE,
            place="",
            detail="",
        )
        (self.datadir / "ToDo.jsonl").write_text(
            line + "\n", encoding="utf-8"
        )

    def test_todo_days_off_hides_todo_completely(self):
        """``todo_days`` が負なら、期限の日にも ToDo は出ない。

        ``todo_days_value >= 0`` のブロックごと飛ばされる。
        """
        self.write_todo(DATE1)

        body = self.get_body(URL_PREFIX + "/", date=DATE1_STR, todo_days="-1")

        assert self.TITLE not in body

    def test_todo_is_shown_on_its_deadline(self):
        """``todo_days`` が 0 以上なら、期限の日に出る。"""
        self.write_todo(DATE1)

        body = self.get_body(URL_PREFIX + "/", date=DATE1_STR, todo_days="0")

        assert self.TITLE in body

    def test_todo_days_boundary_is_inclusive(self):
        """期限が ``today + todo_days`` ちょうどなら、今日の欄に出る。

        期限の日そのものが週表示の範囲に入っていると、今日の欄への
        合流が壊れていても「その日の欄」に出て通ってしまうので、
        ``test_todo_one_day_over_the_boundary_is_not_shown`` と対に
        なるよう、``day_block()`` で今日の欄だけを見る (TODO-049)。
        """
        self.write_todo(datetime.date.today() + datetime.timedelta(3))

        body = self.get_body(URL_PREFIX + "/", todo_days="3")

        assert self.TITLE in day_block(body, datetime.date.today())

    def test_todo_one_day_over_the_boundary_is_not_shown(self):
        """1 日でも先なら、今日の欄には出ない。

        期限の日が週表示の範囲に入っていれば、その日の欄には出る
        （``todo_days`` を見ずに期限の日へ置く。TODO-049）ので、
        今日の欄だけを見て確かめる。曜日によって期限の日が週の外へ
        出ても（``day_block()`` に何も無ければ）真になり得るので、
        単独では「週の外だから出ない」との区別が付かない。
        ``test_todo_days_boundary_is_inclusive``（``today + 3``。
        今日の欄に出る）と対にして、``todo_days`` の境目ちょうどで
        今日の欄への合流が切り替わることを見る (TODO-049)。
        """
        self.write_todo(datetime.date.today() + datetime.timedelta(4))

        body = self.get_body(URL_PREFIX + "/", todo_days="3")

        assert self.TITLE not in day_block(body, datetime.date.today())

    def test_todo_due_today_is_shown_once(self):
        """期限が今日の ToDo は、1 回だけ出る。

        ``todo_today_sde`` には入らないが、期限の日として出るので、
        二重には出ない。
        """
        self.write_todo(datetime.date.today())

        body = self.get_body(URL_PREFIX + "/", todo_days="7")

        assert body.count(self.TITLE) == 1

    def test_overdue_todo_is_shown_on_today(self):
        """期限が過ぎた ToDo は、今日の欄に出る。

        期限の日が週表示の範囲に入っていれば、その日の欄にも出る
        （TODO-049）。ここでは「今日の欄に出る」ことだけを見る。
        """
        self.write_todo(datetime.date.today() - datetime.timedelta(3))

        body = self.get_body(URL_PREFIX + "/", todo_days="0")

        assert self.TITLE in day_block(body, datetime.date.today())

    def test_todo_today_is_not_merged_in_search_mode(self):
        """検索モードでは、今日の欄に ToDo を混ぜない。

        期限が先の ToDo は、検索モードでは ``date`` より先の日を
        見ないので、どこにも出なくなる。
        """
        self.write_todo(datetime.date.today() + datetime.timedelta(3))

        body = self.get_body(URL_PREFIX + "/", todo_days="7")
        assert self.TITLE in body

        body = self.get_body(
            URL_PREFIX + "/", todo_days="7", search_str="買い物"
        )
        assert self.TITLE not in body


#
# 6. ファイルが無い日を開かないこと（TODO-028）
#
class TestLoadSchedScan(WebTestBase):
    """データファイルが無い日は ``get_sdf()`` を呼ばない（TODO-028）。

    検索モードは最大 1825 日さかのぼるので、無い日まで開くと、その
    日数ぶんの空の ``SchedDataFile`` がキャッシュに積まれる。開かなく
    しても**結果が 1 件も変わらない**ことを、「全部開く」ようにした
    ときの結果と突き合わせて確かめる。
    """

    BASE = datetime.date(2021, 3, 15)  # 月曜
    KEYWORD = "けんさく"
    TODO_TITLE = "ノートを買う"

    def write_mixed_data(self):
        """ファイルがある日・無い日・ToDo が当たる日を混ぜて置く。

        - ``BASE``: 当たる予定が 1 件
        - ``BASE - 1``: 休日（検索には当たらない）
        - ``BASE - 2``: ファイル無し。期限がその日の ToDo だけがある
        - ``BASE - 300``: 当たる予定（検索モードでしか見えない日）
        - それ以外: ファイル無し

        ``BASE - 1``/``BASE - 2`` は、通常モードでは前の週になる
        （``BASE`` は月曜）。それらを見るテストは、``call_load_sched()``
        に ``date=BASE - 1`` を渡して、その週を表示させる (TODO-049)。
        """
        self.write_data(
            self.BASE,
            [
                mk_dataline(
                    sde_id="id-base",
                    date=self.BASE.isoformat(),
                    place=self.KEYWORD,
                )
            ],
        )
        self.write_data(
            self.BASE - datetime.timedelta(1),
            [
                mk_dataline(
                    sde_id="id-holiday",
                    date=(self.BASE - datetime.timedelta(1)).isoformat(),
                    type="休日",
                    title="祝日",
                )
            ],
        )
        old = self.BASE - datetime.timedelta(300)
        self.write_data(
            old,
            [
                mk_dataline(
                    sde_id="id-old", date=old.isoformat(), place=self.KEYWORD
                )
            ],
        )

        todo_date = self.BASE - datetime.timedelta(2)
        (self.datadir / "ToDo.jsonl").write_text(
            mk_dataline(
                sde_id="id-todo",
                date=todo_date.isoformat(),
                time_start=None,
                time_end=None,
                type="□買い物",
                title=self.TODO_TITLE,
                place="",
                detail="",
            )
            + "\n",
            encoding="utf-8",
        )

    def call_load_sched(
        self, handler, search_str="", todo_days_value=365, date=None
    ):
        """``load_todo()`` → ``load_week()``/``search()`` を、``get()``
        と同じ順で。

        ``date`` を省くと ``BASE``（TODO-049）。
        """
        loader = SchedLoader(handler._sd)
        search_re = re.compile(search_str) if search_str else None
        todo_sde, todo_today_sde = loader.load_todo(
            None, False, search_re, todo_days_value
        )
        cond = SchedLoadCond(
            filter_re=None,
            filter_neg=False,
            todo_days_value=todo_days_value,
            todo_today_sde=todo_today_sde,
            todo_by_date=loader.mk_todo_by_date(todo_days_value, todo_sde),
        )
        if search_re is not None:
            return loader.search(
                date or self.BASE, cond, SchedSearchCond(search_re, 5)
            )
        return loader.load_week(date or self.BASE, cond)

    def open_every_day(self):
        """変更前と同じく「どの日も開きに行く」ようにするパッチ。"""
        return mock.patch.object(
            SchedData, "sdf_exists", lambda _self, _date=None: True
        )

    def assert_same_as_opening_every_day(self, **kwargs):
        """飛ばしたときと、全部開いたときで、結果が同じか。"""
        handler = make_handler(self._app, MainHandler)

        skipped = self.call_load_sched(handler, **kwargs)
        with self.open_every_day():
            opened = self.call_load_sched(handler, **kwargs)

        assert skipped == opened
        return skipped

    def test_search_mode_sched_is_same_as_opening_every_day(self):
        """検索モードで、``sched``・``date_from``・``date_to`` が同じ。"""
        self.write_mixed_data()

        sched, date_from, date_to = self.assert_same_as_opening_every_day(
            search_str=self.KEYWORD
        )

        # 当たった 2 日だけが、古い順に並ぶ
        assert [s.date for s in sched] == [
            self.BASE - datetime.timedelta(300),
            self.BASE,
        ]
        # 1 件目が見つかったので、365 日前で打ち切られる
        assert date_from == self.BASE - datetime.timedelta(
            SchedLoader.SEARCH_ENOUGH_DAYS
        )
        assert date_to == self.BASE

    def test_normal_mode_sched_is_same_as_opening_every_day(self):
        """検索しないときも同じ。ファイルが無い日の欄も出る。

        範囲は ``BASE`` を含む週（月曜〜日曜。TODO-049）。
        """
        self.write_mixed_data()

        sched, date_from, date_to = self.assert_same_as_opening_every_day()

        day = datetime.timedelta(1)
        assert [s.date for s in sched] == [
            self.BASE + day * i for i in range(7)
        ]
        assert date_from == self.BASE
        assert date_to == self.BASE + day * 6

    def test_is_holiday_is_kept(self):
        """休日の印は、ファイルがある日だけに付く。

        ``BASE - 1`` は前の週になるので、その週を表示させる
        （``date=BASE - 1``。TODO-049）。
        """
        self.write_mixed_data()

        sched, _date_from, _date_to = self.assert_same_as_opening_every_day(
            date=self.BASE - datetime.timedelta(1)
        )

        holiday = {s.date for s in sched if s.is_holiday}
        assert holiday == {self.BASE - datetime.timedelta(1)}

    def test_todo_is_shown_on_a_day_without_data_file(self):
        """ファイルが無い日でも、期限が来ている ToDo は出る。

        ``BASE - 2`` は前の週になるので、その週を表示させる
        （``date=BASE - 1``。TODO-049）。
        """
        self.write_mixed_data()

        sched, _date_from, _date_to = self.assert_same_as_opening_every_day(
            date=self.BASE - datetime.timedelta(1)
        )

        todo_date = self.BASE - datetime.timedelta(2)
        assert not self.data_path(todo_date).exists()
        day = next(s for s in sched if s.date == todo_date)
        assert [sde.title for sde in day.sde] == [self.TODO_TITLE]

    def test_days_without_file_are_not_opened(self):
        """1825 日さかのぼっても、キャッシュに積まれるのは実在する分だけ。

        変更前は、当たらなかった日まで ``SchedDataFile`` を作って
        キャッシュへ積んでいた（1 件も当たらなければ 1825 日ぶん）。
        """
        sd = app_sd(self._app)
        assert sd.get_cache_size() == 0

        self.get_body(
            URL_PREFIX + "/",
            date=self.BASE.isoformat(),
            search_str=self.KEYWORD,
        )

        # ToDo（``date`` が None）の 1 つだけ
        assert sd.get_cache_size() == 1

    def test_existing_days_are_opened(self):
        """ファイルがある日は、今までどおり開く。"""
        self.write_mixed_data()
        sd = app_sd(self._app)

        self.get_body(
            URL_PREFIX + "/",
            date=self.BASE.isoformat(),
            search_str=self.KEYWORD,
        )

        # ToDo と、ファイルがある 3 日ぶん（``BASE - 1`` は検索に
        # 当たらないが、ファイルはあるので開く）
        assert sd.get_cache_size() == 4

    def test_mk_todo_by_date_is_called_once_per_request(self):
        """``mk_todo_by_date()`` は週の数だけ呼び直さない（TODO-079）。

        通常モードでは前後の週ぶん ``load_week()`` が繰り返し呼ばれる
        （TODO-069）が、``todo_by_date`` の集計は ``get()`` の中で
        1 回だけ作って使い回す。
        """
        self.write_mixed_data()

        orig = SchedLoader.mk_todo_by_date
        calls = []

        def spy(self, *args, **kwargs):
            calls.append(1)
            return orig(self, *args, **kwargs)

        with mock.patch.object(SchedLoader, "mk_todo_by_date", spy):
            self.get_body(URL_PREFIX + "/", date=self.BASE.isoformat())

        assert len(calls) == 1


class TestMonthCal(WebTestBase):
    """``SchedLoader.load_month_cal()`` の単体テスト（TODO-103）。"""

    def loader(self):
        handler = make_handler(self._app, MainHandler)
        return SchedLoader(handler._sd)

    def test_weeks_start_monday_and_cover_the_month(self):
        """月曜始まりで、月の最初と最後の日を含む週まで並ぶ。

        2021-03-01 は月曜、2021-03-31 は水曜。
        """
        month_cal = self.loader().load_month_cal(2021, 3)

        assert month_cal.year == 2021
        assert month_cal.month == 3
        for week in month_cal.weeks:
            assert len(week) == 7
            assert week[0].date.weekday() == 0  # 月曜始まり

        first_day = month_cal.weeks[0][0].date
        last_day = month_cal.weeks[-1][-1].date
        assert first_day <= datetime.date(2021, 3, 1)
        assert last_day >= datetime.date(2021, 3, 31)

    def test_in_month_flag(self):
        """前後の月の埋めセルは ``in_month`` が偽になる。"""
        month_cal = self.loader().load_month_cal(2021, 3)

        for week in month_cal.weeks:
            for day in week:
                expected = day.date.year == 2021 and day.date.month == 3
                assert day.in_month == expected

    def test_has_sched_reflects_existing_files(self):
        """予定があるかはファイルの中身（``SchedDataEnt``）で見る。"""
        target = datetime.date(2021, 3, 15)
        self.write_data(target, [mk_dataline(date=target.isoformat())])

        month_cal = self.loader().load_month_cal(2021, 3)

        by_date = {
            d.date: d.has_sched for week in month_cal.weeks for d in week
        }
        assert by_date[target] is True
        assert by_date[datetime.date(2021, 3, 14)] is False

    def test_has_sched_ignores_empty_file(self):
        """予定を全部削除した日（空のファイルが残る）にはドットを出さない。"""
        target = datetime.date(2021, 3, 15)
        self.write_data(target, [])

        month_cal = self.loader().load_month_cal(2021, 3)

        by_date = {
            d.date: d.has_sched for week in month_cal.weeks for d in week
        }
        assert by_date[target] is False

    def test_missing_month_directory(self):
        """データディレクトリごと無い月でも、例外にならず全部 False。"""
        month_cal = self.loader().load_month_cal(2030, 2)

        for week in month_cal.weeks:
            for day in week:
                assert day.has_sched is False

    def test_cached_within_one_loader(self):
        """同じ月は、同じ ``SchedLoader`` の中で使い回される。

        週パネルごとに 2 ヶ月分を持たせると、同じ月が複数の週から
        要求されるため。
        """
        loader = self.loader()

        first = loader.load_month_cal(2021, 3)
        second = loader.load_month_cal(2021, 3)

        assert first is second

    def test_has_important_reflects_important_title(self):
        """タイトルが「!」始まりの日は ``has_important`` が真になる（TODO-129）。"""
        important_day = datetime.date(2021, 3, 15)
        plain_day = datetime.date(2021, 3, 16)
        self.write_data(
            important_day,
            [
                mk_dataline(
                    date=important_day.isoformat(), title="!重要な会議"
                )
            ],
        )
        self.write_data(
            plain_day,
            [mk_dataline(date=plain_day.isoformat(), title="ふつうの会議")],
        )

        month_cal = self.loader().load_month_cal(2021, 3)

        by_date = {
            d.date: d.has_important for week in month_cal.weeks for d in week
        }
        assert by_date[important_day] is True
        assert by_date[plain_day] is False

    def test_canceled_important_is_not_important(self):
        """取り消し済み（「(欠)」始まり）は ``has_important`` が偽（TODO-129）。"""
        target = datetime.date(2021, 3, 15)
        self.write_data(
            target,
            [mk_dataline(date=target.isoformat(), title="(欠)重要な会議")],
        )

        month_cal = self.loader().load_month_cal(2021, 3)

        by_date = {
            d.date: d.has_important for week in month_cal.weeks for d in week
        }
        assert by_date[target] is False

    def test_is_holiday_reflects_holiday_type(self):
        """``type`` が「祝日」の予定がある日は ``is_holiday`` が真（TODO-129）。"""
        target = datetime.date(2021, 3, 15)
        self.write_data(
            target,
            [
                mk_dataline(
                    date=target.isoformat(), type="祝日", title="春分の日"
                )
            ],
        )

        month_cal = self.loader().load_month_cal(2021, 3)

        by_date = {
            d.date: d.is_holiday for week in month_cal.weeks for d in week
        }
        assert by_date[target] is True
        assert by_date[datetime.date(2021, 3, 16)] is False

    def test_todo_deadline_sets_has_todo_but_not_has_sched(self):
        """ToDo の締切がある日は ``has_todo`` が真、``has_sched`` は偽
        （ToDo は通常の予定として数えない。TODO-129）。
        """
        target = datetime.date(2021, 3, 15)
        todo_path = self.datadir / "ToDo.jsonl"
        todo_path.write_text(
            mk_dataline(date=target.isoformat(), type="□ToDo", title="報告書")
            + "\n",
            encoding="utf-8",
        )

        month_cal = self.loader().load_month_cal(2021, 3)

        by_date_todo = {
            d.date: d.has_todo for week in month_cal.weeks for d in week
        }
        by_date_sched = {
            d.date: d.has_sched for week in month_cal.weeks for d in week
        }
        assert by_date_todo[target] is True
        assert by_date_sched[target] is False

    def test_todo_deadline_sets_has_todo_important(self):
        """タイトルが「!」始まりの ToDo の締切日は ``has_todo_important``
        が真、ふつうの ToDo の締切日は偽（TODO-132）。
        """
        important_day = datetime.date(2021, 3, 15)
        plain_day = datetime.date(2021, 3, 16)
        todo_path = self.datadir / "ToDo.jsonl"
        todo_path.write_text(
            mk_dataline(
                date=important_day.isoformat(), type="□ToDo", title="!報告書"
            )
            + "\n"
            + mk_dataline(
                date=plain_day.isoformat(), type="□ToDo", title="連絡"
            )
            + "\n",
            encoding="utf-8",
        )

        month_cal = self.loader().load_month_cal(2021, 3)

        by_date = {
            d.date: d.has_todo_important
            for week in month_cal.weeks
            for d in week
        }
        assert by_date[important_day] is True
        assert by_date[plain_day] is False

    def test_canceled_important_todo_is_not_important(self):
        """取り消し済み（「(欠)」始まり）の重要な ToDo は
        ``has_todo_important`` が偽（TODO-132）。
        """
        target = datetime.date(2021, 3, 15)
        todo_path = self.datadir / "ToDo.jsonl"
        todo_path.write_text(
            mk_dataline(
                date=target.isoformat(), type="□ToDo", title="(欠)!報告書"
            )
            + "\n",
            encoding="utf-8",
        )

        month_cal = self.loader().load_month_cal(2021, 3)

        by_date = {
            d.date: d.has_todo_important
            for week in month_cal.weeks
            for d in week
        }
        assert by_date[target] is False

    def test_todo_in_day_file_is_shown_as_todo(self):
        """日付ファイルに ToDo 型の行が混ざっていても印が消えない
        （TODO-129）。

        正常な操作では ``SchedUpdater`` が ToDo を ``ToDo.jsonl`` へ
        書くので混ざらないが、``migrate`` したデータや手で直した
        ファイルでは起こりうる。そのとき ``has_sched`` は偽になるので、
        四角のほうで拾う。
        """
        target = datetime.date(2021, 3, 15)
        self.write_data(
            target,
            [
                mk_dataline(
                    date=target.isoformat(), type="□ToDo", title="報告書"
                )
            ],
        )

        month_cal = self.loader().load_month_cal(2021, 3)

        by_date = {
            d.date: (d.has_sched, d.has_todo)
            for week in month_cal.weeks
            for d in week
        }
        assert by_date[target] == (False, True)

    def test_todo_in_day_file_important_is_shown_as_important(self):
        """日付ファイルに混ざった重要な ToDo 型の行（「!」始まり）は、
        ``ToDo.jsonl`` を経由しなくても ``has_todo_important`` が真になる
        （TODO-132）。
        """
        target = datetime.date(2021, 3, 15)
        self.write_data(
            target,
            [
                mk_dataline(
                    date=target.isoformat(), type="□ToDo", title="!報告書"
                )
            ],
        )

        month_cal = self.loader().load_month_cal(2021, 3)

        by_date = {
            d.date: d.has_todo_important
            for week in month_cal.weeks
            for d in week
        }
        assert by_date[target] is True

    def test_no_todo_file_does_not_raise(self):
        """ToDo ファイルが無くても例外にならない（TODO-129）。"""
        month_cal = self.loader().load_month_cal(2021, 3)

        for week in month_cal.weeks:
            for day in week:
                assert day.has_todo is False

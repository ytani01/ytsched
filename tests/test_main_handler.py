#
# (c) 2026 Yoichi Tanibayashi
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

日付は ``id="date-YYYY-MM-DD"`` で見る（1 日につき 1 回だけ出る）。
検索モードでは、1 件も見つからなかった日は出ないので、この印が
「その日が出たかどうか」になる。
"""

import datetime
import json
from unittest import mock
from urllib.parse import urlencode

from helpers import URL_PREFIX
from test_web import (
    DATE1,
    DATE1_STR,
    WebTestBase,
    date_id,
    mk_dataline,
)

from ytsched.main_handler import MainHandler

CONF_FNAME = "Conf.cgi"


#
# 1. 設定値の取り出し 4 か所の、条件の食い違い
#
class TestConfArgs(WebTestBase):
    """設定値の取り出し 4 か所は、条件が揃っていない。

    ``search_str`` と ``search_n`` は ``is not None`` で、
    ``todo_days`` と ``filter_str`` は truthy で分岐する
    （``empty_is_given``）。差が出るのは空文字を渡したときだけなので、
    ``Conf.cgi`` の中身と画面で押さえる。

    ただし、**外から差が見えるのは ``search_str``/``filter_str`` の
    2 か所だけ**。``search_n`` の ``convert`` は ``int``、
    ``todo_days`` の ``convert`` は ``str2todo_days()``（中で ``int()``
    を呼ぶ）で、どちらも ``int('')`` が必ず失敗して「渡されていない」
    のと同じ扱いになる（TODO-027）ため、空文字が分岐に入っても
    入らなくても結果が変わらない。つまり、この 2 か所の
    ``empty_is_given`` を揃えてもここのテストは落ちない（TODO-028）。
    """

    def conf_text(self):
        """``Conf.cgi`` の中身。ファイルが無ければ ``None``。"""
        path = self.datadir / CONF_FNAME
        if not path.exists():
            return None
        return path.read_text(encoding="utf-8")

    def test_empty_search_str_is_saved(self):
        """空の ``search_str`` は「渡された」扱いで、保存される。"""
        self.get_body(URL_PREFIX + "/", date=DATE1_STR, search_str="")

        assert self.conf_text() == "SearchStr\t\n"

    def test_empty_filter_str_is_not_saved(self):
        """空の ``filter_str`` は「渡されていない」扱いで、保存されない。

        ``Conf.cgi`` そのものが作られない。
        """
        self.get_body(URL_PREFIX + "/", date=DATE1_STR, filter_str="")

        assert self.conf_text() is None

    def test_empty_search_str_clears_saved_search_str(self):
        """空の ``search_str`` は、保存済みの検索語を消す。"""
        self.write_data(DATE1, [mk_dataline(), mk_dataline(sde_id="id-2")])
        self.get_body(URL_PREFIX + "/", date=DATE1_STR, search_str="会議室")

        body = self.get_body(URL_PREFIX + "/", date=DATE1_STR, search_str="")

        assert self.conf_text() == "SearchStr\t\n"
        # 検索モードから抜けるので、検索期間・件数のバーは出ない
        assert "目標件数" not in body

    def test_empty_filter_str_keeps_saved_filter_str(self):
        """空の ``filter_str`` では、保存済みの絞り込みが消えない。

        空文字は「渡されていない」扱いなので、``Conf.cgi`` の値へ
        落ちて、絞り込みがそのまま効き続ける。
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

        assert self.conf_text() == "FilterStr\t病院\n"
        assert "歯医者" in body
        assert "定例ミーティング" not in body

    def test_empty_search_n_is_not_saved(self):
        """空の ``search_n`` は ``int('')`` にならず、保存もされない。

        ``is not None`` で分岐するので空文字がそのまま ``int()`` へ
        渡るが、数字として読めないので「渡されていない」のと同じ扱いに
        なる（TODO-027）。**以前はここで 500 になり、空のまま
        ``Conf.cgi`` に残っていた**。
        """
        res = self.fetch(
            URL_PREFIX + "/?" + urlencode({"date": DATE1_STR, "search_n": ""})
        )

        assert res.code == 200
        assert self.conf_text() is None

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

        assert self.conf_text() is None

    def test_search_str_is_saved_as_is_and_shown_lowered(self):
        """``Conf.cgi`` には元のまま、画面には小文字で出る。

        小文字化は ``set_conf()`` の**あと**に行われる。
        """
        body = self.get_body(
            URL_PREFIX + "/", date=DATE1_STR, search_str="ABC"
        )

        assert self.conf_text() == "SearchStr\tABC\n"
        assert 'value="abc"' in body

    def test_filter_str_is_saved_as_is_and_shown_lowered(self):
        """``filter_str`` も、保存は元のまま・表示は小文字。"""
        body = self.get_body(
            URL_PREFIX + "/", date=DATE1_STR, filter_str="ABC"
        )

        assert self.conf_text() == "FilterStr\tABC\n"
        assert 'value="abc"' in body


#
# 2. 検索モードの打ち切り条件
#
class TestSearchModeRange(WebTestBase):
    """検索モードで、どこまでさかのぼるか。

    ``self._days``（45）と ``SEARCH_MODE_DAYS``（365）の境界を
    またぐ位置にデータを置いて確かめる。
    """

    DAYS = MainHandler.DEF_DAYS  # 45

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

    def test_normal_mode_range_is_days_before_and_after(self):
        """検索しないときの範囲は ``[date - days, date + days - 1]``。

        検索モードでないので、予定が無い日も欄が出る。
        """
        body = self.get_body(URL_PREFIX + "/", date=self.BASE.isoformat())

        day = datetime.timedelta(1)
        assert date_id(self.BASE - day * self.DAYS) in body
        assert date_id(self.BASE - day * (self.DAYS + 1)) not in body
        assert date_id(self.BASE + day * (self.DAYS - 1)) in body
        assert date_id(self.BASE + day * self.DAYS) not in body

    def test_search_mode_stops_365_days_after_first_hit(self):
        """1 件目が見つかったあとは、365 日前まででやめる。

        ``SEARCH_MODE_DAYS`` ちょうどの日は見るが、その 1 日前は
        見ない。
        """
        day = datetime.timedelta(1)
        limit = day * MainHandler.SEARCH_MODE_DAYS

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
        1 件目までは ``SEARCH_MODE_MAX_DAYS`` まで探し続ける。
        """
        old = self.BASE - datetime.timedelta(400)
        self.write_hits(old)

        body = self.search(search_n=10)

        assert date_id(old) in body

    def test_search_mode_max_days_when_nothing_is_found(self):
        """1 件も無いときは ``SEARCH_MODE_MAX_DAYS`` までさかのぼる。

        ``date_from`` が縮まないので、hidden の ``date_from`` が
        1825 日前のままになる。
        """
        body = self.search(search_n=10)

        date_from = self.BASE - datetime.timedelta(
            MainHandler.SEARCH_MODE_MAX_DAYS
        )
        assert f'value="{date_from}"' in body

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
        orig = MainHandler.cmd_add

        def spy(handler, *args):
            calls.append(args)
            return orig(handler, *args)

        return calls, mock.patch.object(MainHandler, "cmd_add", spy)

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

    def test_deadline_without_times_keeps_the_space(self):
        """時刻が空でも形は変わらない（``〆日付 `` のあとが空になる）。

        末尾に空白が 1 つ残るが、いまはこう動く。
        """
        self.post_done(deadline_time_start="", deadline_time_end="")

        data = self.read_json(datetime.date.today())
        assert data["detail"] == "〆2021/03/05 \n詳細"

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

    ``cur_day`` → ``date`` → ``modified_date`` → ``year``+``month``
    +``day`` の順に上書きされる（後のものが勝つ）。
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

    def test_year_month_day_beats_date(self):
        """``year`` ``month`` ``day`` が 3 つ揃えば、``date`` より強い。"""
        body = self.get_body(
            URL_PREFIX + "/",
            date=DATE1_STR,
            year="2021",
            month="5",
            day="6",
        )

        assert date_id(datetime.date(2021, 5, 6)) in body
        assert date_id(DATE1) not in body

    def test_incomplete_year_month_day_is_ignored(self):
        """1 つでも欠けると、``year`` ``month`` ``day`` は無視される。"""
        for args in [
            {"month": "5", "day": "6"},
            {"year": "2021", "day": "6"},
            {"year": "2021", "month": "5"},
        ]:
            body = self.get_body(URL_PREFIX + "/", date=DATE1_STR, **args)

            assert date_id(DATE1) in body
            assert date_id(datetime.date(2021, 5, 6)) not in body

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

    def test_year_month_day_beats_modified_date(self):
        """``year`` ``month`` ``day`` は ``modified_date`` より強い。

        データは ``date`` 引数の日に書かれるが、表示だけ動く。
        """
        body = self.post_body(
            URL_PREFIX + "/",
            cmd="add",
            sde_id="",
            date=DATE1_STR,
            sde_type="会議",
            title="新しい予定",
            place="",
            detail="",
            year="2021",
            month="5",
            day="6",
        )

        assert date_id(datetime.date(2021, 5, 6)) in body
        assert date_id(DATE1) not in body
        assert self.data_path(DATE1).exists()

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
        """期限が ``today + todo_days`` ちょうどなら、今日の欄に出る。"""
        self.write_todo(datetime.date.today() + datetime.timedelta(3))

        body = self.get_body(URL_PREFIX + "/", todo_days="3")

        assert self.TITLE in body

    def test_todo_one_day_over_the_boundary_is_not_shown(self):
        """1 日でも先なら、今日の欄には出ない。"""
        self.write_todo(datetime.date.today() + datetime.timedelta(4))

        body = self.get_body(URL_PREFIX + "/", todo_days="3")

        assert self.TITLE not in body

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

        ``DAYS`` は 1 なので、期限の日（3 日前）の欄は出ていない。
        """
        self.write_todo(datetime.date.today() - datetime.timedelta(3))

        body = self.get_body(URL_PREFIX + "/", todo_days="0")

        assert body.count(self.TITLE) == 1

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

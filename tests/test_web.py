#
# (c) 2026 Yoichi Tanibayashi
#
"""MainHandler / EditHandler のテスト（tornado.testing）"""

import datetime
from unittest import mock
from urllib.parse import urlencode

import pytest
import tornado.testing
from helpers import URL_PREFIX, make_app

from ytsched.main_handler import MainHandler

DATE1 = datetime.date(2021, 3, 1)
DATE1_STR = "2021-03-01"

# タブ区切りの項目の並びが見えるよう、f-string にせず
# join のまま残す（TODO-015）
DATALINE1 = "\t".join(  # noqa: FLY002
    [
        "id-1",
        "2021/03/01",
        "09:05-10:30",
        "会議",
        "定例ミーティング",
        "会議室",
        "detail1",
    ]
)
DATALINE2 = "\t".join(  # noqa: FLY002
    [
        "id-2",
        "2021/03/01",
        "13:00-14:00",
        "私用",
        "歯医者",
        "病院",
        "detail2",
    ]
)

FORM_HEADERS = {"Content-Type": "application/x-www-form-urlencoded"}


class WebTestBase(tornado.testing.AsyncHTTPTestCase):
    """テスト用の datadir を持つ ``AsyncHTTPTestCase``

    ``AsyncHTTPTestCase`` は ``unittest.TestCase`` なので、``tmp_path``
    は autouse の fixture 経由で受け取る（引数では受け取れない）。
    """

    DAYS = 1

    @pytest.fixture(autouse=True)
    def _datadir(self, tmp_path):
        self.datadir = tmp_path / "data"
        self.datadir.mkdir()

    def get_app(self):
        return make_app(self.datadir, days=self.DAYS)

    def write_data(self, date, lines):
        """データファイルを書く。"""
        path = self.datadir / date.strftime("%Y") / date.strftime("%m")
        path.mkdir(parents=True, exist_ok=True)
        path = path / (date.strftime("%d") + ".cgi")
        path.write_text("".join(l + "\n" for l in lines), encoding="utf-8")
        return path

    def data_path(self, date):
        return (
            self.datadir
            / date.strftime("%Y")
            / date.strftime("%m")
            / (date.strftime("%d") + ".cgi")
        )

    def backup_path(self, date):
        path = self.data_path(date)
        return path.parent / (path.name + ".bak")

    def get_body(self, path, **args):
        """GET して、200 を確かめて、本文を返す。"""
        if args:
            path = f"{path}?{urlencode(args)}"

        res = self.fetch(path)
        assert res.code == 200
        return res.body.decode("utf-8")

    def post_body(self, path, **args):
        """POST して、200 を確かめて、本文を返す。"""
        res = self.fetch(
            path, method="POST", headers=FORM_HEADERS, body=urlencode(args)
        )
        assert res.code == 200
        return res.body.decode("utf-8")


class TestMainHandler(WebTestBase):
    """``MainHandler`` の表示"""

    def test_get(self):
        body = self.get_body(URL_PREFIX + "/")
        assert "Ytsched" in body

    def test_get_root_and_no_slash(self):
        for path in ["/", URL_PREFIX, URL_PREFIX + "/"]:
            assert self.fetch(path).code == 200

    def test_template_is_rendered(self):
        """テンプレートが展開されている。"""
        body = self.get_body(URL_PREFIX + "/")
        assert "{%" not in body
        assert "{{" not in body

    def test_date_argument(self):
        body = self.get_body(URL_PREFIX + "/", date=DATE1_STR)
        assert 'id="date-2021-03-01"' in body
        assert 'id="date-2021-02-28"' in body

    def test_sde_is_displayed(self):
        self.write_data(DATE1, [DATALINE1, DATALINE2])

        body = self.get_body(URL_PREFIX + "/", date=DATE1_STR)

        assert "定例ミーティング" in body
        assert "歯医者" in body

    def test_filter_str(self):
        """``filter_str`` に合うものだけが出る。

        ``filter_str`` 自体は入力欄に出るので、絞り込む語（``病院``）と、
        表示を確かめる語（``歯医者``）は分ける。
        """
        self.write_data(DATE1, [DATALINE1, DATALINE2])

        body = self.get_body(
            URL_PREFIX + "/", date=DATE1_STR, filter_str="病院"
        )

        assert "歯医者" in body
        assert "定例ミーティング" not in body

    def test_filter_str_negative(self):
        """``!`` 始まりは、マッチしたものを除く。

        ``filter_str`` 自体は入力欄に出るので、除外する語には
        表示されるスケジュールに含まれない語を使う。
        """
        self.write_data(DATE1, [DATALINE1, DATALINE2])

        body = self.get_body(
            URL_PREFIX + "/", date=DATE1_STR, filter_str="!病院"
        )

        assert "歯医者" not in body
        assert "定例ミーティング" in body

    def test_filter_str_is_saved(self):
        self.get_body(URL_PREFIX + "/", date=DATE1_STR, filter_str="歯医者")

        conf = (self.datadir / "Conf.cgi").read_text(encoding="utf-8")
        assert "FilterStr\t歯医者\n" in conf

    def test_search_str(self):
        """``search_str`` に合うものだけが出る。

        ``search_str`` 自体も入力欄に出るので、探す語（``病院``）と、
        表示を確かめる語（``歯医者``）は分ける。
        """
        self.write_data(DATE1, [DATALINE1, DATALINE2])

        body = self.get_body(
            URL_PREFIX + "/", date=DATE1_STR, search_str="病院"
        )

        assert "歯医者" in body
        assert "定例ミーティング" not in body

    def test_todo_days(self):
        self.get_body(URL_PREFIX + "/", date=DATE1_STR, todo_days="7")

        conf = (self.datadir / "Conf.cgi").read_text(encoding="utf-8")
        assert "ToDo_Days\t7\n" in conf

    def test_search_n(self):
        self.get_body(URL_PREFIX + "/", date=DATE1_STR, search_n="3")

        conf = (self.datadir / "Conf.cgi").read_text(encoding="utf-8")
        assert "SearchN\t3\n" in conf

    def test_saved_filter_str_is_reused(self):
        """一度指定した ``filter_str`` は、次の表示にも効く。"""
        self.write_data(DATE1, [DATALINE1, DATALINE2])
        self.get_body(URL_PREFIX + "/", date=DATE1_STR, filter_str="病院")

        body = self.get_body(URL_PREFIX + "/", date=DATE1_STR)

        assert "歯医者" in body
        assert "定例ミーティング" not in body

    def test_invalid_filter_str_shows_all(self):
        """不正な ``filter_str`` は、絞り込みを無視して全件出す。"""
        self.write_data(DATE1, [DATALINE1, DATALINE2])

        body = self.get_body(URL_PREFIX + "/", date=DATE1_STR, filter_str="[")

        assert "定例ミーティング" in body
        assert "歯医者" in body
        assert "フィルタの正規表現" in body
        assert 'value="["' in body

    def test_invalid_filter_str_negative_shows_all(self):
        """``!`` 始まりでも、中身が不正なら絞り込みを無視する。"""
        self.write_data(DATE1, [DATALINE1, DATALINE2])

        body = self.get_body(
            URL_PREFIX + "/", date=DATE1_STR, filter_str="!["
        )

        assert "定例ミーティング" in body
        assert "歯医者" in body
        assert "フィルタの正規表現" in body

    def test_invalid_search_str_shows_all(self):
        """不正な ``search_str`` では、検索モードに入らない。"""
        self.write_data(DATE1, [DATALINE1, DATALINE2])

        body = self.get_body(URL_PREFIX + "/", date=DATE1_STR, search_str="(")

        assert "定例ミーティング" in body
        assert "歯医者" in body
        assert "検索の正規表現" in body
        assert 'value="("' in body
        # 検索期間・件数のバーは出ない
        assert "目標件数" not in body

    def test_invalid_filter_str_and_search_str(self):
        """両方とも不正なら、知らせも両方出る。"""
        self.write_data(DATE1, [DATALINE1])

        body = self.get_body(
            URL_PREFIX + "/",
            date=DATE1_STR,
            filter_str="[",
            search_str="(",
        )

        assert "定例ミーティング" in body
        assert "フィルタの正規表現" in body
        assert "検索の正規表現" in body

    def test_valid_search_str_shows_search_bar(self):
        """正しい ``search_str`` なら、検索モードに入る。"""
        self.write_data(DATE1, [DATALINE1, DATALINE2])

        body = self.get_body(
            URL_PREFIX + "/", date=DATE1_STR, search_str="病院"
        )

        assert "目標件数" in body
        assert "フィルタの正規表現" not in body
        assert "検索の正規表現" not in body

    def test_invalid_filter_str_is_saved(self):
        """不正な ``filter_str`` も、今までどおり保存される。"""
        self.get_body(URL_PREFIX + "/", date=DATE1_STR, filter_str="[")

        conf = (self.datadir / "Conf.cgi").read_text(encoding="utf-8")
        assert "FilterStr\t[\n" in conf

    def test_year_month_day_arguments(self):
        body = self.get_body(
            URL_PREFIX + "/", year="2021", month="3", day="1"
        )

        assert 'id="date-2021-03-01"' in body

    def test_cur_day_argument(self):
        """``date`` が無ければ ``cur_day`` を使う。"""
        body = self.get_body(URL_PREFIX + "/", cur_day=DATE1_STR)

        assert 'id="date-2021-03-01"' in body

    def test_todo_is_displayed(self):
        """ToDo は、期限の日付の欄に出る。"""
        todo_line = "\t".join(  # noqa: FLY002
            [
                "id-t",
                "2021/03/01",
                ":-:",
                "□買い物",
                "ノートを買う",
                "",
                "",
            ]
        )
        (self.datadir / "ToDo.cgi").write_text(
            todo_line + "\n", encoding="utf-8"
        )

        body = self.get_body(URL_PREFIX + "/", date=DATE1_STR)

        assert "ノートを買う" in body

    def test_todo_with_filter_str(self):
        """``filter_str`` は ToDo にも効く。"""
        todo_line = "\t".join(  # noqa: FLY002
            [
                "id-t",
                "2021/03/01",
                ":-:",
                "□買い物",
                "ノートを買う",
                "",
                "",
            ]
        )
        (self.datadir / "ToDo.cgi").write_text(
            todo_line + "\n", encoding="utf-8"
        )

        body = self.get_body(
            URL_PREFIX + "/", date=DATE1_STR, filter_str="雑貨"
        )
        assert "ノートを買う" not in body

        body = self.get_body(
            URL_PREFIX + "/", date=DATE1_STR, filter_str="!雑貨"
        )
        assert "ノートを買う" in body

    def test_todo_with_search_str(self):
        """``search_str`` は ToDo にも効く。"""
        todo_line = "\t".join(  # noqa: FLY002
            [
                "id-t",
                "2021/03/01",
                ":-:",
                "□買い物",
                "ノートを買う",
                "",
                "",
            ]
        )
        (self.datadir / "ToDo.cgi").write_text(
            todo_line + "\n", encoding="utf-8"
        )

        body = self.get_body(
            URL_PREFIX + "/", date=DATE1_STR, search_str="ノート"
        )

        assert "ノートを買う" in body

    def test_search_n_limits_days(self):
        """検索は ``search_n`` 件見つかった日までさかのぼる。"""
        for day in range(1, 7):
            date = datetime.date(2021, 3, day)
            line = "\t".join(
                [
                    f"id-{day}",
                    date.strftime("%Y/%m/%d"),
                    "09:00-10:00",
                    "会議",
                    "定例ミーティング",
                    "会議室",
                    "",
                ]
            )
            self.write_data(date, [line])

        body = self.get_body(
            URL_PREFIX + "/",
            date="2021-03-06",
            search_str="ミーティング",
            search_n="3",
        )

        assert 'id="date-2021-03-06"' in body
        assert 'id="date-2021-03-04"' in body
        assert 'id="date-2021-03-03"' not in body

    def test_todo_is_displayed_on_today(self):
        """期限が先の ToDo も、``todo_days`` の範囲なら今日の欄に出る。"""
        deadline = datetime.date.today() + datetime.timedelta(3)
        todo_line = "\t".join(
            [
                "id-t",
                deadline.strftime("%Y/%m/%d"),
                ":-:",
                "□買い物",
                "ノートを買う",
                "",
                "",
            ]
        )
        (self.datadir / "ToDo.cgi").write_text(
            todo_line + "\n", encoding="utf-8"
        )

        body = self.get_body(URL_PREFIX + "/", todo_days="7")

        assert "ノートを買う" in body

    def test_todo_is_not_displayed_on_today(self):
        """``todo_days`` の範囲外なら、今日の欄には出ない。"""
        deadline = datetime.date.today() + datetime.timedelta(30)
        todo_line = "\t".join(
            [
                "id-t",
                deadline.strftime("%Y/%m/%d"),
                ":-:",
                "□買い物",
                "ノートを買う",
                "",
                "",
            ]
        )
        (self.datadir / "ToDo.cgi").write_text(
            todo_line + "\n", encoding="utf-8"
        )

        body = self.get_body(URL_PREFIX + "/", todo_days="7")

        assert "ノートを買う" not in body


class TestUpdate(WebTestBase):
    """``cmd=add`` → ``cmd=update`` → ``cmd=del``"""

    def add_sde(self, title="新しい予定"):
        """1 件追加して、その sde_id を返す。"""
        self.post_body(
            URL_PREFIX + "/",
            cmd="add",
            sde_id="",
            date=DATE1_STR,
            time_start="09:05",
            time_end="10:30",
            sde_type="会議",
            title=title,
            place="会議室",
            detail="詳細",
        )

        lines = self.data_path(DATE1).read_text(encoding="utf-8").splitlines()
        assert len(lines) == 1
        return lines[0].split("\t")[0]

    def test_add(self):
        sde_id = self.add_sde()

        line = self.data_path(DATE1).read_text(encoding="utf-8").rstrip("\n")
        assert line == "\t".join(  # noqa: FLY002
            [
                sde_id,
                "2021/03/01",
                "09:05-10:30",
                "会議",
                "新しい予定",
                "会議室",
                "詳細",
            ]
        )

    def test_add_is_displayed(self):
        self.add_sde()

        body = self.get_body(URL_PREFIX + "/", date=DATE1_STR)
        assert "新しい予定" in body

    def test_update(self):
        sde_id = self.add_sde()

        self.post_body(
            URL_PREFIX + "/",
            cmd="update",
            sde_id=sde_id,
            orig_date=DATE1_STR,
            date=DATE1_STR,
            time_start="09:05",
            time_end="10:30",
            sde_type="会議",
            title="変更後",
            place="会議室",
            detail="詳細",
        )

        line = self.data_path(DATE1).read_text(encoding="utf-8").rstrip("\n")
        assert line.split("\t")[0] == sde_id
        assert line.split("\t")[4] == "変更後"

    def test_del(self):
        sde_id = self.add_sde()

        self.post_body(
            URL_PREFIX + "/",
            cmd="del",
            sde_id=sde_id,
            orig_date=DATE1_STR,
            date=DATE1_STR,
            sde_type="会議",
            title="新しい予定",
        )

        # 空になってもデータファイルは残る
        assert self.data_path(DATE1).read_text(encoding="utf-8") == ""

        body = self.get_body(URL_PREFIX + "/", date=DATE1_STR)
        assert "新しい予定" not in body

    def test_update_keeps_backup(self):
        """1 件しか予定が無い日を編集しても、``.bak`` が空にならない。

        ``cmd=update`` は 1 リクエストで ``save()`` が 2 回走る。
        2 回目は 0 バイトのファイルを ``.bak`` へ移してはいけない。
        """
        sde_id = self.add_sde()

        self.post_body(
            URL_PREFIX + "/",
            cmd="update",
            sde_id=sde_id,
            orig_date=DATE1_STR,
            date=DATE1_STR,
            time_start="09:05",
            time_end="10:30",
            sde_type="会議",
            title="変更後",
            place="会議室",
            detail="詳細",
        )

        assert "変更後" in self.data_path(DATE1).read_text(encoding="utf-8")
        assert "新しい予定" in self.backup_path(DATE1).read_text(
            encoding="utf-8"
        )

    def test_del_twice_keeps_backup(self):
        """``cmd=del`` が 2 回走っても、``.bak`` が空にならない。

        削除後の画面をリロードすると POST が再送される。
        """
        sde_id = self.add_sde()

        for _ in range(2):
            self.post_body(
                URL_PREFIX + "/",
                cmd="del",
                sde_id=sde_id,
                orig_date=DATE1_STR,
                date=DATE1_STR,
                sde_type="会議",
                title="新しい予定",
            )

        assert self.data_path(DATE1).read_text(encoding="utf-8") == ""
        assert "新しい予定" in self.backup_path(DATE1).read_text(
            encoding="utf-8"
        )

    def test_update_clears_search_str(self):
        """``cmd=update`` 経由でも、検索がクリアされる。"""
        sde_id = self.add_sde()
        self.get_body(URL_PREFIX + "/", date=DATE1_STR, search_str="会議")

        self.post_body(
            URL_PREFIX + "/",
            cmd="update",
            sde_id=sde_id,
            orig_date=DATE1_STR,
            date=DATE1_STR,
            sde_type="会議",
            title="新しい予定",
            search_str="",
        )

        conf = (self.datadir / "Conf.cgi").read_text(encoding="utf-8")
        assert "SearchStr\t\n" in conf

    def test_update_search_str_is_lowered(self):
        """``cmd=update`` 経由でも、検索語が小文字になる。

        edit 画面に渡る値を、``render()`` の引数で見る。
        """
        sde_id = self.add_sde()

        with mock.patch.object(MainHandler, "render") as render:
            self.post_body(
                URL_PREFIX + "/",
                cmd="update",
                sde_id=sde_id,
                orig_date=DATE1_STR,
                date=DATE1_STR,
                sde_type="会議",
                title="新しい予定",
                search_str="ABC",
            )

        assert render.call_args.args[0] == MainHandler.HTML_EDIT
        assert render.call_args.kwargs["search_str"] == "abc"

    def test_todo_done(self):
        """ToDo を完了（種別を ToDo から外す）と、今日の予定になる。"""
        self.post_body(
            URL_PREFIX + "/",
            cmd="add",
            sde_id="",
            date=DATE1_STR,
            sde_type="会議",
            title="ノートを買う",
            place="",
            detail="詳細",
            deadline_date="2021-03-05",
            deadline_time_start="10:00",
            deadline_time_end="11:00",
        )

        today = datetime.date.today()
        assert not self.data_path(DATE1).exists()

        field = (
            self.data_path(today)
            .read_text(encoding="utf-8")
            .rstrip("\n")
            .split("\t")
        )
        assert field[1] == today.strftime("%Y/%m/%d")
        assert field[2].endswith("-:")
        assert field[6] == "〆2021/03/05 10:00-11:00<br />詳細"

    def test_add_todo(self):
        """ToDo は ``ToDo.cgi`` へ入る。"""
        self.post_body(
            URL_PREFIX + "/",
            cmd="add",
            sde_id="",
            date=DATE1_STR,
            sde_type="□買い物",
            title="ノートを買う",
            place="",
            detail="",
        )

        assert not self.data_path(DATE1).exists()
        line = (
            (self.datadir / "ToDo.cgi")
            .read_text(encoding="utf-8")
            .rstrip("\n")
        )
        assert line.split("\t")[4] == "ノートを買う"


class TestEditHandler(WebTestBase):
    """``EditHandler``"""

    def test_get_new(self):
        body = self.get_body(URL_PREFIX + "/edit", date=DATE1_STR)

        assert "{%" not in body
        assert "{{" not in body
        assert 'value="2021-03-01"' in body

    def test_get_new_no_slash_and_slash(self):
        for path in [URL_PREFIX + "/edit", URL_PREFIX + "/edit/"]:
            assert self.fetch(path).code == 200

    def test_get_existing(self):
        self.write_data(DATE1, [DATALINE1])

        body = self.get_body(
            URL_PREFIX + "/edit", date=DATE1_STR, sde_id="id-1"
        )

        assert "定例ミーティング" in body
        assert "会議室" in body

    def test_get_existing_todo(self):
        todo_line = "\t".join(  # noqa: FLY002
            [
                "id-t",
                "2021/03/01",
                ":-:",
                "□買い物",
                "ノートを買う",
                "",
                "",
            ]
        )
        (self.datadir / "ToDo.cgi").write_text(
            todo_line + "\n", encoding="utf-8"
        )

        body = self.get_body(
            URL_PREFIX + "/edit",
            date=DATE1_STR,
            sde_id="id-t",
            todo_flag="true",
        )

        assert "ノートを買う" in body

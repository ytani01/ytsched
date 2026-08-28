#
# (c) 2026 ytani01
#
"""MainHandler / EditHandler のテスト（tornado.testing）"""

import contextlib
import datetime
import html
import io
import json
import re
from unittest import mock
from urllib.parse import urlencode

import pytest
import tornado.testing
from helpers import URL_PREFIX, app_sd, make_app
from loguru import logger

from ytsched import handler_util
from ytsched.edit_handler import EditHandler
from ytsched.main_handler import MainHandler
from ytsched.sched_update import SchedUpdater
from ytsched.ytsched import SchedDataFile

DATE1 = datetime.date(2021, 3, 1)
DATE1_STR = "2021-03-01"


def mk_dataline(**kwargs):
    """テスト用の 1 行（JSON Lines）を作る。"""
    data = {
        "sde_id": "id-1",
        "date": DATE1_STR,
        "time_start": "09:05",
        "time_end": "10:30",
        "type": "会議",
        "title": "定例ミーティング",
        "place": "会議室",
        "detail": "detail1",
    }
    data.update(kwargs)
    return json.dumps(data, ensure_ascii=False)


DATALINE1 = mk_dataline()
DATALINE2 = mk_dataline(
    sde_id="id-2",
    time_start="13:00",
    time_end="14:00",
    type="私用",
    title="歯医者",
    place="病院",
    detail="detail2",
)

FORM_HEADERS = {"Content-Type": "application/x-www-form-urlencoded"}


def date_id(date):
    """1 日分の欄に付く id（テンプレート ``main.html``）。"""
    return f'id="date-{date}"'


def week_panel(body):
    """いま見ている週の ``.my-week-panel`` だけを取り出す（TODO-069）。

    前後数ヶ月ぶんの週を DOM に持つようになり、``id="date-..."`` も
    その全部に付くので、「その日が本文にあるか」は「その日が
    表示中の週に入っているか」ではなくなった。週の範囲を見るときは、
    ``my-week-cur`` が付いた panel の中だけを見る。
    """
    marker = 'class="my-week-panel my-week-cur"'
    start = body.index(marker)
    next_start = body.find('class="my-week-panel', start + len(marker))
    if next_start == -1:
        next_start = len(body)
    return body[start:next_start]


def day_block(body, date):
    """``date`` の日付ブロックだけを取り出す（``main.html``。TODO-049）。

    週表示になり、期限が先の ToDo でもその日が週の範囲に入っていれば
    欄に出るようになったので、「今日の欄にだけ出ない」ことを見るには
    本文全体でなく、この欄だけを見る必要がある。
    """
    marker = date_id(date)
    start = body.index(marker)
    next_start = body.find('id="date-', start + len(marker))
    if next_start == -1:
        next_start = len(body)
    return body[start:next_start]


CONF_FNAME = "conf.json"


def read_conf(datadir):
    """``conf.json`` の中身（TODO-032）。無ければ ``FileNotFoundError``。"""
    path = datadir / CONF_FNAME
    return json.loads(path.read_text(encoding="utf-8"))


def write_conf(datadir, conf):
    """``conf.json`` を書く（テストの下ごしらえ用）。"""
    (datadir / CONF_FNAME).write_text(
        json.dumps(conf, ensure_ascii=False), encoding="utf-8"
    )


def orig_date_in(body):
    """編集画面の隠しフィールド ``orig_date`` の値（無ければ ``None``）。"""
    match = re.search(r'id="orig_date"[^>]*value="([^"]*)"', body, re.DOTALL)
    if match is None:
        return None
    return match.group(1)


@contextlib.contextmanager
def capture_log(level="WARNING"):
    """ログを集める。

    ``mylog`` は loguru なので、``caplog``（標準の ``logging``）では
    拾えない。``logger.add()`` で一時的な出力先を足す。
    """
    out = io.StringIO()
    handler_id = logger.add(out, level=level, format="{level}:{message}")
    try:
        yield out
    finally:
        logger.remove(handler_id)


class WebTestBase(tornado.testing.AsyncHTTPTestCase):
    """テスト用の datadir を持つ ``AsyncHTTPTestCase``

    ``AsyncHTTPTestCase`` は ``unittest.TestCase`` なので、``tmp_path``
    は autouse の fixture 経由で受け取る（引数では受け取れない）。
    """

    @pytest.fixture(autouse=True)
    def _datadir(self, tmp_path):
        self.datadir = tmp_path / "data"
        self.datadir.mkdir()

    def get_app(self):
        return make_app(self.datadir)

    def write_data(self, date, lines):
        """データファイルを書く。"""
        path = self.datadir / date.strftime("%Y") / date.strftime("%m")
        path.mkdir(parents=True, exist_ok=True)
        path = path / (date.strftime("%d") + ".jsonl")
        path.write_text("".join(l + "\n" for l in lines), encoding="utf-8")
        return path

    def data_path(self, date):
        return (
            self.datadir
            / date.strftime("%Y")
            / date.strftime("%m")
            / (date.strftime("%d") + ".jsonl")
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
        """``date`` を含む週（月曜〜日曜）が表示される（TODO-049）。

        ``DATE1`` は月曜。
        """
        body = self.get_body(URL_PREFIX + "/", date=DATE1_STR)
        assert 'id="date-2021-03-01"' in body  # 月曜 (DATE1)
        assert 'id="date-2021-03-07"' in body  # 日曜

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

        assert read_conf(self.datadir)["FilterStr"] == "歯医者"

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

    def test_search_str_with_zenkaku_paren(self):
        """全角括弧のまま検索しても当たる（TODO-029）。

        入力側も ``normalize()`` を通るので、``（重要）`` は
        ``(重要)`` として（正規表現のグループとして）照合される。
        """
        self.write_data(
            DATE1,
            [mk_dataline(title="会議（重要）の件"), DATALINE2],
        )

        body = self.get_body(
            URL_PREFIX + "/", date=DATE1_STR, search_str="（重要）"
        )

        assert "会議（重要）の件" in body
        assert "歯医者" not in body

    def test_filter_str_with_zenkaku_paren(self):
        """絞り込みも同じく、全角括弧のまま当たる（TODO-029）。"""
        self.write_data(
            DATE1,
            [mk_dataline(title="会議（重要）の件"), DATALINE2],
        )

        body = self.get_body(
            URL_PREFIX + "/", date=DATE1_STR, filter_str="（重要）"
        )

        assert "会議（重要）の件" in body
        assert "歯医者" not in body

    def test_todo_days(self):
        self.get_body(URL_PREFIX + "/", date=DATE1_STR, todo_days="7")

        assert read_conf(self.datadir)["ToDo_Days"] == "7"

    def test_search_n(self):
        self.get_body(URL_PREFIX + "/", date=DATE1_STR, search_n="3")

        assert read_conf(self.datadir)["SearchN"] == "3"

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

        assert read_conf(self.datadir)["FilterStr"] == "["

    def test_cur_day_argument(self):
        """``date`` が無ければ ``cur_day`` を使う。"""
        body = self.get_body(URL_PREFIX + "/", cur_day=DATE1_STR)

        assert 'id="date-2021-03-01"' in body

    def test_todo_is_displayed(self):
        """ToDo は、期限の日付の欄に出る。"""
        todo_line = mk_dataline(
            sde_id="id-t",
            time_start=None,
            time_end=None,
            type="□買い物",
            title="ノートを買う",
            place="",
            detail="",
        )
        (self.datadir / "ToDo.jsonl").write_text(
            todo_line + "\n", encoding="utf-8"
        )

        body = self.get_body(URL_PREFIX + "/", date=DATE1_STR)

        assert "ノートを買う" in body

    def test_todo_with_filter_str(self):
        """``filter_str`` は ToDo にも効く。"""
        todo_line = mk_dataline(
            sde_id="id-t",
            time_start=None,
            time_end=None,
            type="□買い物",
            title="ノートを買う",
            place="",
            detail="",
        )
        (self.datadir / "ToDo.jsonl").write_text(
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
        todo_line = mk_dataline(
            sde_id="id-t",
            time_start=None,
            time_end=None,
            type="□買い物",
            title="ノートを買う",
            place="",
            detail="",
        )
        (self.datadir / "ToDo.jsonl").write_text(
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
            line = mk_dataline(
                sde_id=f"id-{day}",
                date=date.isoformat(),
                time_start="09:00",
                time_end="10:00",
                detail="",
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
        todo_line = mk_dataline(
            sde_id="id-t",
            date=deadline.isoformat(),
            time_start=None,
            time_end=None,
            type="□買い物",
            title="ノートを買う",
            place="",
            detail="",
        )
        (self.datadir / "ToDo.jsonl").write_text(
            todo_line + "\n", encoding="utf-8"
        )

        body = self.get_body(URL_PREFIX + "/", todo_days="7")

        assert "ノートを買う" in body

    def test_todo_is_not_displayed_on_today(self):
        """``todo_days`` の範囲外なら、今日の欄には出ない。"""
        deadline = datetime.date.today() + datetime.timedelta(30)
        todo_line = mk_dataline(
            sde_id="id-t",
            date=deadline.isoformat(),
            time_start=None,
            time_end=None,
            type="□買い物",
            title="ノートを買う",
            place="",
            detail="",
        )
        (self.datadir / "ToDo.jsonl").write_text(
            todo_line + "\n", encoding="utf-8"
        )

        body = self.get_body(URL_PREFIX + "/", todo_days="7")

        # 期限の日 (今日 + 30 日) は前後数ヶ月ぶんの週に入っていて、
        # その日の欄には出る。ここで見るのは「今日の欄に出ないこと」
        # なので、今日の欄だけを取り出す (TODO-069)
        assert "ノートを買う" not in day_block(body, datetime.date.today())


class TestWeekBar(WebTestBase):
    """上部の週の帯（TODO-055）

    帯には横ゲージだけを出す。今週から何週離れているか（``+3w``）は、
    ゲージの針の上にある（TODO-066）。文字は JavaScript が読み込み時に
    書き込むので（TODO-078）、それを見るテストは
    ``tests/test_browser.py`` 側にある。
    """

    def week_bar(self, body):
        """帯の中身を返す。帯が無ければ ``None``。"""
        m = re.search(r'id="week_bar".*?<!-- container -->', body, re.DOTALL)
        if m is None:
            return None
        return m.group(0)

    def test_no_date_range_in_week_bar(self):
        """期間は帯に出さない（TODO-066。``DATE1`` は月曜）。

        各日の欄に日付が出ているので、帯との二重表示をやめた。
        """
        bar = self.week_bar(self.get_body(URL_PREFIX + "/", date=DATE1_STR))

        assert bar is not None
        assert "2021/03/01" not in bar

    def test_no_week_bar_in_search_mode(self):
        """検索モードでは帯を出さない。

        検索結果は日付が飛び飛びで週の区切りに合わず、期間は検索側の
        帯が出している。
        """
        self.write_data(DATE1, [DATALINE1, DATALINE2])

        body = self.get_body(
            URL_PREFIX + "/", date=DATE1_STR, search_str="病院"
        )

        assert self.week_bar(body) is None


class TestDateColumn(WebTestBase):
    """日付の欄を押したときの動き（TODO-055）"""

    def date_col_onmousedown(self, body, date):
        """その日の日付の欄の ``onmousedown`` を返す。

        属性値は autoescape で ``&#x27;`` になっているので戻してから
        返す。
        """
        m = re.search(
            r'my-date-col[^>]*?onmousedown="([^"]*)"',
            body[body.index(date_id(date)) :],
        )
        assert m is not None
        return html.unescape(m.group(1))

    def test_date_col_opens_edit(self):
        """通常モードでは、その日の新規追加の画面へ移る。

        週表示ではその日がすでに画面に出ていて、押しても何も変わらな
        かったので、この操作を予定の追加に充てた。
        """
        body = self.get_body(URL_PREFIX + "/", date=DATE1_STR)

        onmousedown = self.date_col_onmousedown(body, DATE1)

        assert "doGet(" in onmousedown
        assert URL_PREFIX + "/edit/" in onmousedown
        assert "'date': '2021-03-01'" in onmousedown
        assert "'sde_id': ''" in onmousedown

    def test_date_col_in_search_mode(self):
        """検索モードでは今までどおり、その週へ移って検索を解除する。"""
        self.write_data(DATE1, [DATALINE1, DATALINE2])

        body = self.get_body(
            URL_PREFIX + "/", date=DATE1_STR, search_str="病院"
        )

        onmousedown = self.date_col_onmousedown(body, DATE1)

        assert "doPost(" in onmousedown
        assert "edit/" not in onmousedown
        assert "'search_str': ''" in onmousedown


class TestMonthMiniCal(WebTestBase):
    """週間表示の月間ミニカレンダー（TODO-103）"""

    def test_shows_two_months(self):
        """いま見ている週の月と、その翌月の 2 ヶ月分が出る。

        ``DATE1``（2021-03-01）は月曜。
        """
        body = self.get_body(URL_PREFIX + "/", date=DATE1_STR)
        panel = week_panel(body)

        captions = re.findall(r'my-mini-cal-caption">\s*([^<]+?)\s*<', panel)
        assert captions == ["2021/03", "2021/04"]

    def test_day_with_sched_has_dot(self):
        """予定がある日には、印（ドット）が付く。"""
        target = datetime.date(2021, 4, 10)
        self.write_data(target, [mk_dataline(date=target.isoformat())])

        body = self.get_body(URL_PREFIX + "/", date=DATE1_STR)
        panel = week_panel(body)

        m = re.search(
            r"<td[^>]*>\s*<div class=\"my-mini-cal-daynum\">10</div>"
            r"(.*?)</td>",
            panel[panel.index("2021/04") :],
            re.DOTALL,
        )
        assert m is not None
        assert "my-mini-cal-dot" in m.group(1)

    def test_day_click_scrolls_to_date(self):
        """日付のセルは ``scrollToDate()`` でその日へジャンプする。"""
        body = self.get_body(URL_PREFIX + "/", date=DATE1_STR)
        panel = week_panel(body)

        assert (
            f"onmousedown=\"scrollToDate('{URL_PREFIX}/', '2021-03-15');\""
            in panel
        )

    def test_out_of_month_day_is_not_clickable(self):
        """前後の月の埋めセルは ``onmousedown`` を持たない。

        2021-04-30 は金曜なので、4 月分の最後の週は 5 月 1 日・2 日
        まで伸びる。その 5 月 1 日の埋めセルを見る。
        """
        body = self.get_body(URL_PREFIX + "/", date=DATE1_STR)
        panel = week_panel(body)

        april = panel[panel.index("2021/04") :]
        m = re.search(
            r'<td class="my-mini-cal-day my-mini-cal-day-out"[^>]*>'
            r'\s*<div class="my-mini-cal-daynum">1</div>',
            april,
        )
        assert m is not None

    def test_not_shown_in_search_mode(self):
        """検索モードでは出さない（週の区切りに合わないため）。"""
        self.write_data(DATE1, [DATALINE1])

        body = self.get_body(
            URL_PREFIX + "/", date=DATE1_STR, search_str="定例"
        )

        assert "my-mini-cal-row" not in body


class TestManifestAndIcons(WebTestBase):
    """manifest.json とアイコンが HTTP で引ける（TODO-039）"""

    def test_manifest(self):
        res = self.fetch(URL_PREFIX + "/static/manifest.json")

        assert res.code == 200
        assert "json" in res.headers["Content-Type"]

    def test_apple_touch_icon(self):
        assert (
            self.fetch(URL_PREFIX + "/static/icons/apple-touch-icon.png").code
            == 200
        )

    def test_favicon(self):
        assert self.fetch(URL_PREFIX + "/static/favicon.ico").code == 200

    def test_links_in_html(self):
        body = self.get_body(URL_PREFIX + "/")

        assert 'rel="manifest"' in body
        assert 'rel="apple-touch-icon"' in body


class TestInvalidArgs(WebTestBase):
    """数字・日付として読めない引数の扱い（TODO-027）

    500 にせず、その指定を無視して画面を出す。不正な値は
    ``conf.json`` へ保存しない。不正な正規表現の扱い（TODO-012）と
    同じ考え方。
    """

    def conf_data(self):
        """``conf.json`` の中身。ファイルが無ければ ``None``。"""
        if not (self.datadir / CONF_FNAME).exists():
            return None
        return read_conf(self.datadir)

    def today_id(self):
        return date_id(datetime.date.today())

    #
    # search_n
    #
    def test_invalid_search_n_is_not_an_error(self):
        """数字にならない ``search_n`` でも画面は出る。"""
        body = self.get_body(URL_PREFIX + "/", date=DATE1_STR, search_n="abc")

        assert date_id(DATE1) in body

    def test_invalid_search_n_is_not_saved(self):
        """数字にならない ``search_n`` は ``conf.json`` に残らない。"""
        self.get_body(URL_PREFIX + "/", date=DATE1_STR, search_n="abc")

        assert self.conf_data() is None

    def test_invalid_search_n_does_not_break_next_request(self):
        """一度踏んでも、次の素の GET が開ける。

        以前は ``SearchN=abc`` が残って、以後ずっと 500 だった。
        """
        self.get_body(URL_PREFIX + "/", date=DATE1_STR, search_n="abc")

        body = self.get_body(URL_PREFIX + "/", date=DATE1_STR)

        assert date_id(DATE1) in body

    def test_invalid_search_n_falls_back_to_the_default(self):
        """数字にならない ``search_n`` は既定値になる。"""
        body = self.get_body(
            URL_PREFIX + "/",
            date=DATE1_STR,
            search_str="ミーティング",
            search_n="abc",
        )

        assert f'value="{MainHandler.DEF_SEARCH_N}" selected' in body

    def test_invalid_search_n_keeps_saved_search_n(self):
        """保存済みの ``SearchN`` は、不正な値では消えない。

        「渡されていない」のと同じ扱いなので、``conf.json`` の値へ
        落ちる。
        """
        self.get_body(URL_PREFIX + "/", date=DATE1_STR, search_n="3")

        body = self.get_body(
            URL_PREFIX + "/",
            date=DATE1_STR,
            search_str="ミーティング",
            search_n="abc",
        )

        assert read_conf(self.datadir)["SearchN"] == "3"
        assert 'value="3" selected' in body

    def test_broken_search_n_in_conf_falls_back_to_the_default(self):
        """``conf.json`` に残っている不正な値も既定値へ落とす。

        保存の側だけ直しても、踏んでしまった ``conf.json`` は
        直らないため。
        """
        write_conf(self.datadir, {"SearchN": "abc"})

        body = self.get_body(
            URL_PREFIX + "/", date=DATE1_STR, search_str="ミーティング"
        )

        assert f'value="{MainHandler.DEF_SEARCH_N}" selected' in body

    #
    # todo_days
    #
    def test_invalid_todo_days_is_not_an_error(self):
        """数字にならない ``todo_days`` でも画面は出る。"""
        body = self.get_body(
            URL_PREFIX + "/", date=DATE1_STR, todo_days="abc"
        )

        assert date_id(DATE1) in body

    def test_invalid_todo_days_is_not_saved(self):
        """数字にならない ``todo_days`` は ``conf.json`` に残らない。"""
        self.get_body(URL_PREFIX + "/", date=DATE1_STR, todo_days="abc")

        assert self.conf_data() is None

    def test_invalid_todo_days_falls_back_to_the_default(self):
        """数字にならない ``todo_days`` は既定値になる。"""
        body = self.get_body(
            URL_PREFIX + "/", date=DATE1_STR, todo_days="abc"
        )

        assert f'value="{MainHandler.DEF_TODO_DAYS}" selected' in body

    def test_broken_todo_days_in_conf_falls_back_to_the_default(self):
        """``conf.json`` に残っている不正な値も既定値へ落とす。"""
        write_conf(self.datadir, {"ToDo_Days": "abc"})

        body = self.get_body(URL_PREFIX + "/", date=DATE1_STR)

        assert date_id(DATE1) in body
        assert f'value="{MainHandler.DEF_TODO_DAYS}" selected' in body

    #
    # LoadMonths (TODO-069)
    #
    def week_panel_count(self, body):
        """描かれた週の数（``.my-week-panel`` の数）。"""
        return body.count('class="my-week-panel')

    def test_load_months_default_is_one_month_each_way(self):
        """既定では前後 1 ヶ月ぶん（前後 4 週 + 今の週 = 9 週）。"""
        body = self.get_body(URL_PREFIX + "/", date=DATE1_STR)

        weeks_n = MainHandler.months2weeks(MainHandler.DEF_LOAD_MONTHS)
        assert self.week_panel_count(body) == weeks_n * 2 + 1

    def test_load_months_zero_leaves_only_the_current_week(self):
        """``0`` なら今の週だけ。"""
        write_conf(self.datadir, {"LoadMonths": "0"})

        body = self.get_body(URL_PREFIX + "/", date=DATE1_STR)

        assert self.week_panel_count(body) == 1

    def test_load_months_widens_the_range(self):
        """大きくすると、その分だけ週が増える。"""
        write_conf(self.datadir, {"LoadMonths": "2"})

        body = self.get_body(URL_PREFIX + "/", date=DATE1_STR)

        weeks_n = MainHandler.months2weeks(2)
        assert self.week_panel_count(body) == weeks_n * 2 + 1

    def test_broken_load_months_falls_back_to_the_default(self):
        """数字にならない値も、範囲の外も既定値へ落とす。"""
        for value in ("abc", "-1", "99"):
            write_conf(self.datadir, {"LoadMonths": value})

            body = self.get_body(URL_PREFIX + "/", date=DATE1_STR)

            weeks_n = MainHandler.months2weeks(MainHandler.DEF_LOAD_MONTHS)
            assert self.week_panel_count(body) == weeks_n * 2 + 1, value

    def test_load_months_is_not_overwritten(self):
        """手で書いた値は ``conf.json`` から消えない。

        画面から変える設定ではないので、アプリは読むだけで
        ``set_conf()`` しない（TODO-069）。他の設定を保存したときに
        巻き添えで消えないことまで見る。
        """
        write_conf(self.datadir, {"LoadMonths": "2"})

        self.get_body(URL_PREFIX + "/", date=DATE1_STR, todo_days="7")

        conf = read_conf(self.datadir)
        assert conf["LoadMonths"] == "2"
        assert conf["ToDo_Days"] == "7"

    #
    # AutoTurnMsec (TODO-084)
    #
    def test_auto_turn_msec_default(self):
        """既定値が、``main-page.js`` へ渡す定数に入る。"""
        body = self.get_body(URL_PREFIX + "/", date=DATE1_STR)

        assert (
            f"const auto_turn_msec = {MainHandler.DEF_AUTO_TURN_MSEC};"
            in body
        )

    def test_auto_turn_msec_from_conf(self):
        """``conf.json`` の値が、定数に入る。"""
        write_conf(self.datadir, {"AutoTurnMsec": "500"})

        body = self.get_body(URL_PREFIX + "/", date=DATE1_STR)

        assert "const auto_turn_msec = 500;" in body

    def test_broken_auto_turn_msec_falls_back_to_the_default(self):
        """数字にならない値も、範囲の外も既定値へ落とす。"""
        for value in ("abc", "100", "99999"):
            write_conf(self.datadir, {"AutoTurnMsec": value})

            body = self.get_body(URL_PREFIX + "/", date=DATE1_STR)

            assert (
                f"const auto_turn_msec = {MainHandler.DEF_AUTO_TURN_MSEC};"
                in body
            ), value

    def test_auto_turn_msec_is_not_overwritten(self):
        """手で書いた値は ``conf.json`` から消えない (``LoadMonths`` と同じ)。

        画面から変える設定ではないので、アプリは読むだけで
        ``set_conf()`` しない。他の設定を保存したときに巻き添えで
        消えないことまで見る。
        """
        write_conf(self.datadir, {"AutoTurnMsec": "500"})

        self.get_body(URL_PREFIX + "/", date=DATE1_STR, todo_days="7")

        conf = read_conf(self.datadir)
        assert conf["AutoTurnMsec"] == "500"
        assert conf["ToDo_Days"] == "7"

    def test_search_mode_has_only_one_week(self):
        """検索モードでは週の区切りに合わないので 1 つだけ。"""
        body = self.get_body(
            URL_PREFIX + "/", date=DATE1_STR, search_str="ミーティング"
        )

        assert self.week_panel_count(body) == 1

    #
    # date / cur_day
    #
    def test_invalid_date_falls_back_to_cur_day(self):
        """日付として読めない ``date`` は「無し」扱い。"""
        body = self.get_body(URL_PREFIX + "/", date="abc", cur_day=DATE1_STR)

        assert date_id(DATE1) in body

    def test_invalid_cur_day_falls_back_to_today(self):
        """日付として読めない ``cur_day`` は今日になる。"""
        body = self.get_body(URL_PREFIX + "/", cur_day="abc")

        assert self.today_id() in body

    def test_invalid_date_and_cur_day_fall_back_to_today(self):
        """両方とも読めなければ今日。"""
        body = self.get_body(URL_PREFIX + "/", date="abc", cur_day="abc")

        assert self.today_id() in body

    #
    # 数字・日付にはなるが、表示に使えない値（TODO-027）
    #
    def test_far_future_date_is_ignored(self):
        """``datetime.date.max`` に近すぎる ``date`` は「無し」扱い。

        日付としては正しいが、前後へ広げるところで
        ``OverflowError`` になる。
        """
        body = self.get_body(
            URL_PREFIX + "/", date="9999-12-31", cur_day=DATE1_STR
        )

        assert date_id(DATE1) in body

    def test_far_past_date_is_ignored(self):
        """``datetime.date.min`` に近すぎる ``date`` も同じ。"""
        body = self.get_body(
            URL_PREFIX + "/", date="0001-01-01", cur_day=DATE1_STR
        )

        assert date_id(DATE1) in body

    def test_the_newest_usable_date_still_works(self):
        """使える範囲の上端は、今までどおり出る。"""
        date = datetime.date.max - datetime.timedelta(
            handler_util.SEARCH_HARD_LIMIT_DAYS
        )

        body = self.get_body(URL_PREFIX + "/", date=date.isoformat())

        assert date_id(date) in body

    def test_the_oldest_usable_date_works_in_search_mode(self):
        """使える範囲の下端は、検索モード（5 年前まで遡る）でも開ける。

        範囲の幅は、この遡る分（``SEARCH_HARD_LIMIT_DAYS``）で決めて
        いる。1 件も見つからない日は出ないので、200 で見る。
        """
        date = datetime.date.min + datetime.timedelta(
            handler_util.SEARCH_HARD_LIMIT_DAYS
        )

        res = self.fetch(
            URL_PREFIX
            + "/?"
            + urlencode({"date": date.isoformat(), "search_str": "会議"})
        )

        assert res.code == 200

    #
    # todo_days: 数字にはなるが大きすぎる値（TODO-027）
    #
    # ToDo が 1 件も無いと ``load_todo()`` の中の足し算まで行かない
    # ので、ToDo を置いた状態で見る。
    #
    TODO_TITLE = "ノートを買う"

    def write_todo(self, deadline):
        """期限 ``deadline`` の ToDo を 1 件書く。"""
        line = mk_dataline(
            sde_id="id-t",
            date=deadline.isoformat(),
            time_start=None,
            time_end=None,
            type="□買い物",
            title=self.TODO_TITLE,
            place="",
            detail="",
        )
        (self.datadir / "ToDo.jsonl").write_text(
            line + "\n", encoding="utf-8"
        )

    def test_huge_todo_days_is_not_an_error(self):
        """大きすぎる ``todo_days`` でも画面は出る。"""
        self.write_todo(DATE1)

        body = self.get_body(
            URL_PREFIX + "/", date=DATE1_STR, todo_days="99999999999"
        )

        assert date_id(DATE1) in body

    def test_huge_todo_days_is_not_saved(self):
        """大きすぎる ``todo_days`` は ``conf.json`` に残らない。"""
        self.write_todo(DATE1)

        self.get_body(
            URL_PREFIX + "/", date=DATE1_STR, todo_days="99999999999"
        )

        assert self.conf_data() is None

    def test_huge_todo_days_does_not_break_next_request(self):
        """一度踏んでも、次の素の GET が開ける。

        以前は ``ToDo_Days=99999999999`` が ``conf.json`` に残って、
        ToDo がある限りトップページも開けなかった。
        """
        self.write_todo(DATE1)
        self.get_body(
            URL_PREFIX + "/", date=DATE1_STR, todo_days="99999999999"
        )

        body = self.get_body(URL_PREFIX + "/", date=DATE1_STR)

        assert date_id(DATE1) in body

    def test_huge_todo_days_in_conf_falls_back_to_the_default(self):
        """``conf.json`` に残っている大きすぎる値も既定値へ落とす。"""
        self.write_todo(DATE1)
        write_conf(self.datadir, {"ToDo_Days": "99999999999"})

        body = self.get_body(URL_PREFIX + "/", date=DATE1_STR)

        assert date_id(DATE1) in body
        assert f'value="{MainHandler.DEF_TODO_DAYS}" selected' in body

    def test_invalid_todo_days_keeps_saved_todo_days(self):
        """保存済みの ``ToDo_Days`` は、不正な値では消えない。

        ``search_n`` と同じで、「渡されていない」のと同じ扱いなので
        ``conf.json`` の値へ落ちる。
        """
        self.get_body(URL_PREFIX + "/", date=DATE1_STR, todo_days="7")

        body = self.get_body(
            URL_PREFIX + "/", date=DATE1_STR, todo_days="abc"
        )

        assert read_conf(self.datadir)["ToDo_Days"] == "7"
        assert 'value="7" selected' in body

    #
    # 警告ログ
    #
    def test_invalid_search_n_logs_a_warning(self):
        """不正な値は、黙って捨てずに警告を 1 行出す。"""
        with capture_log() as log:
            self.get_body(URL_PREFIX + "/", date=DATE1_STR, search_n="abc")

        assert "WARNING:search_n='abc'" in log.getvalue()
        assert "ignored" in log.getvalue()

    def test_out_of_range_todo_days_logs_a_warning(self):
        """範囲外の値も、範囲が分かる形で警告を出す。"""
        days_max = max(MainHandler.TODO_DAYS.values())

        with capture_log() as log:
            self.get_body(
                URL_PREFIX + "/", date=DATE1_STR, todo_days="99999999999"
            )

        assert f"must be in -1..{days_max}" in log.getvalue()


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
        return json.loads(lines[0])["sde_id"]

    def test_add(self):
        sde_id = self.add_sde()

        line = self.data_path(DATE1).read_text(encoding="utf-8").rstrip("\n")
        assert json.loads(line) == {
            "sde_id": sde_id,
            "date": "2021-03-01",
            "time_start": "09:05",
            "time_end": "10:30",
            "type": "会議",
            "title": "新しい予定",
            "place": "会議室",
            "detail": "詳細",
        }

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
        assert json.loads(line)["sde_id"] == sde_id
        assert json.loads(line)["title"] == "変更後"

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

    def test_fix_keeps_backup_of_both_entries(self):
        """同じ日に 2 件あるとき、片方を ``fix`` しても ``.bak`` に両方
        残る(TODO-077)。

        ``fix`` は ``cmd_del()`` → ``cmd_add()`` で実装されている。
        del と add でそれぞれ ``save()`` すると、2 回目の ``.bak`` が
        「1 件消えた直後」を写してしまい、修正前の内容がどこにも
        残らなかった。
        """
        self.write_data(DATE1, [DATALINE1, DATALINE2])

        self.post_body(
            URL_PREFIX + "/",
            cmd="fix",
            sde_id="id-2",
            orig_date=DATE1_STR,
            date=DATE1_STR,
            time_start="13:00",
            time_end="14:00",
            sde_type="私用",
            title="歯医者(変更)",
            place="病院",
            detail="detail2",
        )

        backup_lines = (
            self.backup_path(DATE1).read_text(encoding="utf-8").splitlines()
        )
        backup_ids = {json.loads(line)["sde_id"] for line in backup_lines}
        assert backup_ids == {"id-1", "id-2"}

    def test_exec_update_saves_even_on_error(self):
        """途中で例外が出ても、そのリクエストの中で保存する(TODO-077)。

        ``SchedData`` はアプリ全体で 1 つなので、変更の印を残したまま
        抜けると、**次の関係の無いリクエストの保存に紛れ込む**。
        ``exec_update()`` は ``finally`` で保存する。
        """
        self.write_data(DATE1, [DATALINE1, DATALINE2])

        with mock.patch.object(
            SchedUpdater, "cmd_add", side_effect=RuntimeError("boom")
        ):
            res = self.fetch(
                URL_PREFIX + "/",
                method="POST",
                headers=FORM_HEADERS,
                body=urlencode(
                    {
                        "cmd": "fix",
                        "sde_id": "id-2",
                        "orig_date": DATE1_STR,
                        "date": DATE1_STR,
                        "sde_type": "私用",
                        "title": "歯医者",
                    }
                ),
            )

        assert res.code == 500

        # 削除だけが済んだ状態が、このリクエストの中で書かれている
        assert "id-2" not in self.data_path(DATE1).read_text(encoding="utf-8")
        backup = self.backup_path(DATE1).read_text(encoding="utf-8")
        assert "id-1" in backup
        assert "id-2" in backup

        # 印は残っていないので、次のリクエストが巻き添えにしない
        sd = app_sd(self._app)
        assert not sd._dirty_sdf

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

        assert read_conf(self.datadir)["SearchStr"] == ""

    def test_update_search_str_is_lowered(self):
        """``cmd=update`` 経由でも、検索語が小文字になる。

        更新したあとは編集画面へリダイレクトするので (TODO-050)、
        飛んだ先の ``EditHandler`` に渡る値を ``render()`` の引数で見る。
        """
        sde_id = self.add_sde()

        with mock.patch.object(EditHandler, "render") as render:
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

        assert render.call_args.args[0] == EditHandler.HTML_EDIT
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

        data = json.loads(
            self.data_path(today).read_text(encoding="utf-8").rstrip("\n")
        )
        assert data["date"] == today.isoformat()
        assert data["time_end"] is None
        assert data["detail"] == "〆2021/03/05 10:00-11:00\n詳細"

    def test_add_without_date(self):
        """``date`` が空の非 ToDo は、今日の予定になる (TODO-016)。"""
        self.post_body(
            URL_PREFIX + "/",
            cmd="add",
            sde_id="",
            date="",
            sde_type="会議",
            title="日付なしの予定",
            place="",
            detail="",
        )

        today = datetime.date.today()
        assert not (self.datadir / "ToDo.jsonl").exists()

        data = json.loads(
            self.data_path(today).read_text(encoding="utf-8").rstrip("\n")
        )
        assert data["date"] == today.isoformat()
        assert data["title"] == "日付なしの予定"

    def test_update_sde_not_found(self):
        """更新したはずのデータが見つからないときは 404 (TODO-016)。"""
        sde_id = self.add_sde()

        with mock.patch.object(SchedDataFile, "get_sde", return_value=None):
            res = self.fetch(
                URL_PREFIX + "/",
                method="POST",
                headers=FORM_HEADERS,
                body=urlencode(
                    {
                        "cmd": "update",
                        "sde_id": sde_id,
                        "orig_date": DATE1_STR,
                        "date": DATE1_STR,
                        "sde_type": "会議",
                        "title": "新しい予定",
                    }
                ),
            )

        assert res.code == 404

    def test_add_todo(self):
        """ToDo は ``ToDo.jsonl`` へ入る。"""
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
            (self.datadir / "ToDo.jsonl")
            .read_text(encoding="utf-8")
            .rstrip("\n")
        )
        assert json.loads(line)["title"] == "ノートを買う"


class TestInvalidUpdateArgs(WebTestBase):
    """``cmd=add``/``fix``/``update``/``del`` の日付・時刻が読めないとき

    ここは**データを書き込む**経路なので、読めない引数は既定値へ
    落とさずに 400 で断る（TODO-027）。表示の経路のように「無視して
    既定値」にすると、利用者が指定していない日へデータが動いてしまう。

    400 のときに**データが 1 行も変わっていないこと**まで見る。
    """

    def add_sde(self, title="新しい予定"):
        """DATE1 に 1 件追加して、その sde_id を返す。"""
        self.post_body(
            URL_PREFIX + "/",
            cmd="add",
            sde_id="",
            date=DATE1_STR,
            sde_type="会議",
            title=title,
            place="",
            detail="",
        )

        lines = self.data_path(DATE1).read_text(encoding="utf-8").splitlines()
        assert len(lines) == 1
        return json.loads(lines[0])["sde_id"]

    def write_todo(self, sde_id="id-t"):
        """ToDo を 1 件書く。"""
        line = mk_dataline(
            sde_id=sde_id,
            time_start=None,
            time_end=None,
            type="□買い物",
            title="ノートを買う",
            place="",
            detail="",
        )
        (self.datadir / "ToDo.jsonl").write_text(
            line + "\n", encoding="utf-8"
        )

    def post_res(self, **args):
        """POST して、レスポンスをそのまま返す（200 を確かめない）。"""
        return self.fetch(
            URL_PREFIX + "/",
            method="POST",
            headers=FORM_HEADERS,
            body=urlencode(args),
        )

    def snapshot(self):
        """``datadir`` 以下のファイルの中身を全部読む。

        400 のときに 1 行も変わっていないことを、日付ごとのファイルも
        ``ToDo.jsonl`` もまとめて見るため。
        """
        return {
            str(p.relative_to(self.datadir)): p.read_bytes()
            for p in sorted(self.datadir.rglob("*"))
            if p.is_file()
        }

    #
    # date が読めないとき: 400（書き込みは 1 つも起きない）
    #
    def test_add_with_unreadable_date_is_400(self):
        """日付として読めない ``date`` は 400。"""
        before = self.snapshot()

        res = self.post_res(
            cmd="add",
            sde_id="",
            date="abc",
            sde_type="会議",
            title="読めない日付の予定",
            place="",
            detail="",
        )

        assert res.code == 400
        assert self.snapshot() == before
        assert not (self.datadir / "ToDo.jsonl").exists()
        assert not self.data_path(datetime.date.today()).exists()

    def test_add_with_far_future_date_is_400(self):
        """日付にはなるが、表示に使えない ``date`` も 400。"""
        before = self.snapshot()

        res = self.post_res(
            cmd="add",
            sde_id="",
            date="9999-12-31",
            sde_type="会議",
            title="遠すぎる予定",
            place="",
            detail="",
        )

        assert res.code == 400
        assert self.snapshot() == before
        assert not self.data_path(datetime.date.today()).exists()

    #
    # orig_date が読めないとき: 400（消しも足しもしない）
    #
    def test_del_with_unreadable_orig_date_is_400(self):
        """読めない ``orig_date`` の ``cmd=del`` は 400。元の予定も無事。"""
        sde_id = self.add_sde()
        before = self.snapshot()

        res = self.post_res(
            cmd="del",
            sde_id=sde_id,
            orig_date="abc",
            date=DATE1_STR,
            sde_type="会議",
            title="新しい予定",
        )

        assert res.code == 400
        assert self.snapshot() == before
        assert "新しい予定" in self.data_path(DATE1).read_text(
            encoding="utf-8"
        )

    def test_del_with_unreadable_orig_date_keeps_todo(self):
        """``None`` へ落として ToDo を消す、という消し間違いをしない。

        ``orig_date`` が無い（＝ ToDo）ときは ``None`` で ToDo の
        ファイルを指すので、読めない値をそのまま ``None`` にすると
        別のファイルを消しに行くことになる。
        """
        self.write_todo()
        before = self.snapshot()

        res = self.post_res(
            cmd="del",
            sde_id="id-t",
            orig_date="abc",
            date=DATE1_STR,
            sde_type="□買い物",
            title="ノートを買う",
        )

        assert res.code == 400
        assert self.snapshot() == before
        todo = (self.datadir / "ToDo.jsonl").read_text(encoding="utf-8")
        assert "ノートを買う" in todo

    def test_del_with_unreadable_orig_date_logs_a_warning(self):
        """断ったことは、黙って済ませずに警告を出す。"""
        sde_id = self.add_sde()

        with capture_log() as log:
            res = self.post_res(
                cmd="del",
                sde_id=sde_id,
                orig_date="abc",
                date=DATE1_STR,
                sde_type="会議",
                title="新しい予定",
            )

        assert res.code == 400
        assert "orig_date='abc'" in log.getvalue()

    def test_update_with_unreadable_orig_date_is_400(self):
        """``cmd=update`` も 400。元の予定は消えず、重複も作らない。"""
        self.add_sde()
        sde_id = json.loads(
            self.data_path(DATE1).read_text(encoding="utf-8").rstrip("\n")
        )["sde_id"]
        before = self.snapshot()

        res = self.post_res(
            cmd="update",
            sde_id=sde_id,
            orig_date="abc",
            date=DATE1_STR,
            sde_type="会議",
            title="変更後",
            place="",
            detail="",
        )

        assert res.code == 400
        assert self.snapshot() == before
        lines = self.data_path(DATE1).read_text(encoding="utf-8").splitlines()
        assert len(lines) == 1
        assert "新しい予定" in lines[0]

    def test_far_future_orig_date_is_400(self):
        """日付にはなるが表示に使えない ``orig_date`` も 400。"""
        self.write_todo()
        before = self.snapshot()

        res = self.post_res(
            cmd="del",
            sde_id="id-t",
            orig_date="9999-12-31",
            date=DATE1_STR,
            sde_type="□買い物",
            title="ノートを買う",
        )

        assert res.code == 400
        assert self.snapshot() == before
        todo = (self.datadir / "ToDo.jsonl").read_text(encoding="utf-8")
        assert "ノートを買う" in todo

    #
    # time_start / time_end が読めないとき: 400（前は 500 だった）
    #
    def assert_unreadable_time_is_400(self, arg_name):
        """時刻として読めない値を渡して、400 とデータ無傷を確かめる。

        ``AsyncHTTPTestCase`` は ``unittest.TestCase`` なので
        ``pytest.mark.parametrize`` が効かない。呼び分ける。
        """
        before = self.snapshot()

        args = {
            "cmd": "add",
            "sde_id": "",
            "date": DATE1_STR,
            "sde_type": "会議",
            "title": "読めない時刻の予定",
            "place": "",
            "detail": "",
            arg_name: "abc",
        }
        res = self.post_res(**args)

        assert res.code == 400
        assert self.snapshot() == before
        assert not self.data_path(DATE1).exists()

    def test_unreadable_time_start_is_400(self):
        """時刻として読めない ``time_start`` は 400。

        ``datetime.time.fromisoformat()`` を素通しにしていた頃は 500
        だった（TODO-027）。
        """
        self.assert_unreadable_time_is_400("time_start")

    def test_unreadable_time_end_is_400(self):
        """``time_end`` も同じ。"""
        self.assert_unreadable_time_is_400("time_end")

    def test_out_of_range_time_is_400(self):
        """``25:00`` のような時刻も 400。"""
        res = self.post_res(
            cmd="add",
            sde_id="",
            date=DATE1_STR,
            sde_type="会議",
            title="範囲外の時刻",
            place="",
            detail="",
            time_start="25:00",
        )

        assert res.code == 400
        assert not self.data_path(DATE1).exists()

    #
    # 400 のガードが、普通の操作まで止めていないこと
    #
    def test_del_with_valid_orig_date_deletes(self):
        """``orig_date`` が正しければ、今までどおり消える。"""
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

        assert self.data_path(DATE1).read_text(encoding="utf-8") == ""

    def test_update_with_valid_orig_date_replaces(self):
        """``orig_date`` が正しければ、今までどおり置き換わる。"""
        sde_id = self.add_sde()

        self.post_body(
            URL_PREFIX + "/",
            cmd="update",
            sde_id=sde_id,
            orig_date=DATE1_STR,
            date=DATE1_STR,
            sde_type="会議",
            title="変更後",
            place="",
            detail="",
        )

        lines = self.data_path(DATE1).read_text(encoding="utf-8").splitlines()
        assert len(lines) == 1
        assert json.loads(lines[0])["title"] == "変更後"

    def test_del_todo_with_empty_orig_date_still_works(self):
        """``orig_date`` が空のときは、今までどおり ToDo を消す。

        空は「指定が無かった」で、読めない値とは別扱い（TODO-016）。
        """
        self.write_todo()

        self.post_body(
            URL_PREFIX + "/",
            cmd="del",
            sde_id="id-t",
            orig_date="",
            date="",
            sde_type="□買い物",
            title="ノートを買う",
        )

        todo = (self.datadir / "ToDo.jsonl").read_text(encoding="utf-8")
        assert "ノートを買う" not in todo


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

    def test_get_unknown_sde_id(self):
        """存在しない ``sde_id`` は 404 (TODO-016)。"""
        self.write_data(DATE1, [DATALINE1])

        res = self.fetch(
            f"{URL_PREFIX}/edit?"
            + urlencode({"date": DATE1_STR, "sde_id": "no-such-id"})
        )
        assert res.code == 404

    def test_get_unknown_sde_id_todo(self):
        """ToDo でも、存在しない ``sde_id`` は 404 (TODO-016)。"""
        res = self.fetch(
            f"{URL_PREFIX}/edit?"
            + urlencode(
                {
                    "date": DATE1_STR,
                    "sde_id": "no-such-id",
                    "todo_flag": "true",
                }
            )
        )
        assert res.code == 404

    def test_unreadable_date_falls_back_to_today(self):
        """日付として読めない ``date`` は今日 (TODO-027)。

        以前はここが ``fromisoformat()`` の素通しで 500 だった。
        """
        body = self.get_body(URL_PREFIX + "/edit", date="abc")

        today = datetime.date.today()
        assert f'value="{today.isoformat()}"' in body

    def test_far_future_date_falls_back_to_today(self):
        """日付にはなるが、表示に使えない ``date`` も今日。"""
        body = self.get_body(URL_PREFIX + "/edit", date="9999-12-31")

        today = datetime.date.today()
        assert f'value="{today.isoformat()}"' in body

    def test_orig_date_is_the_file_date(self):
        """``orig_date`` は、その行が入っているファイルの日付。"""
        self.write_data(DATE1, [DATALINE1])

        body = self.get_body(
            URL_PREFIX + "/edit", date=DATE1_STR, sde_id="id-1"
        )

        assert orig_date_in(body) == DATE1_STR

    def test_orig_date_of_a_new_sde_is_the_date(self):
        """新規のときは、今までどおり表示している日付。"""
        body = self.get_body(URL_PREFIX + "/edit", date=DATE1_STR)

        assert orig_date_in(body) == DATE1_STR

    def test_get_existing_todo(self):
        todo_line = mk_dataline(
            sde_id="id-t",
            time_start=None,
            time_end=None,
            type="□買い物",
            title="ノートを買う",
            place="",
            detail="",
        )
        (self.datadir / "ToDo.jsonl").write_text(
            todo_line + "\n", encoding="utf-8"
        )

        body = self.get_body(
            URL_PREFIX + "/edit",
            date=DATE1_STR,
            sde_id="id-t",
            todo_flag="true",
        )

        assert "ノートを買う" in body
        # ToDo は ``ToDo.jsonl`` にあるので、``orig_date`` は付かない
        assert orig_date_in(body) is None


class TestEditOrigDate(WebTestBase):
    """行の ``date`` がファイル名から決まる日付と食い違うとき（TODO-029）

    ``load_line()`` は行の ``date`` を信じて残す（警告だけ出す）。
    編集画面の ``orig_date`` を「その行が入っているファイルの日付」に
    してあるので、``fix`` しても重複しない。
    """

    OTHER_STR = "2021-03-05"
    OTHER = datetime.date(2021, 3, 5)

    def write_mismatched(self):
        """``2021/03/01.jsonl`` に ``date`` が別の日の行を書く。"""
        return self.write_data(DATE1, [mk_dataline(date=self.OTHER_STR)])

    def test_orig_date_is_the_file_date(self):
        """行の ``date``（表示）ではなく、ファイルの日付になる。"""
        self.write_mismatched()

        body = self.get_body(
            URL_PREFIX + "/edit", date=DATE1_STR, sde_id="id-1"
        )

        assert orig_date_in(body) == DATE1_STR
        # 表示上の日付は、今までどおり行の ``date``
        assert f'value="{self.OTHER_STR}"' in body

    def test_fix_does_not_duplicate(self):
        """編集画面から ``fix`` しても、行が二重にならない。

        TODO-029 の前は ``orig_date`` が行の ``date``（``03-05``）
        だったので、``03-01`` の行が消えずに残り、``03-05`` にも
        書かれて**重複**した。
        """
        self.write_mismatched()
        body = self.get_body(
            URL_PREFIX + "/edit", date=DATE1_STR, sde_id="id-1"
        )

        self.post_body(
            URL_PREFIX + "/",
            cmd="fix",
            sde_id="id-1",
            orig_date=orig_date_in(body),
            date=self.OTHER_STR,
            sde_type="会議",
            title="定例ミーティング",
            place="会議室",
            detail="detail1",
        )

        assert self.data_path(DATE1).read_text(encoding="utf-8") == ""
        lines = (
            self.data_path(self.OTHER)
            .read_text(encoding="utf-8")
            .splitlines()
        )
        assert len(lines) == 1
        assert json.loads(lines[0])["sde_id"] == "id-1"


class TestRedirect(WebTestBase):
    """POST したあとに GET へ飛ばす (POST-Redirect-GET、TODO-050)

    リロードしても再送信にならないよう、POST では描画せず、
    ``302`` で日付付きの GET へ飛ばす。
    """

    def post_no_redirect(self, path, **args):
        """POST して、リダイレクトを追わずに応答を返す。"""
        return self.fetch(
            path,
            method="POST",
            headers=FORM_HEADERS,
            body=urlencode(args),
            follow_redirects=False,
            raise_error=False,
        )

    def add_sde(self, title="新しい予定"):
        """1 件追加して、その sde_id を返す。"""
        self.post_body(
            URL_PREFIX + "/",
            cmd="add",
            sde_id="",
            date=DATE1_STR,
            sde_type="会議",
            title=title,
        )

        lines = self.data_path(DATE1).read_text(encoding="utf-8").splitlines()
        assert len(lines) == 1
        return json.loads(lines[0])["sde_id"]

    def test_post_redirects_to_get(self):
        """素の POST も、日付付きの GET へ飛ばす。"""
        res = self.post_no_redirect(URL_PREFIX + "/", date=DATE1_STR)

        assert res.code == 302
        assert res.headers["Location"] == f"{URL_PREFIX}/?date={DATE1_STR}"

    def test_add_redirects_to_list(self):
        """追加したあとは一覧へ。"""
        res = self.post_no_redirect(
            URL_PREFIX + "/",
            cmd="add",
            sde_id="",
            date=DATE1_STR,
            sde_type="会議",
            title="新しい予定",
        )

        assert res.code == 302
        location = res.headers["Location"]
        assert location.startswith(f"{URL_PREFIX}/?")
        assert f"date={DATE1_STR}" in location

    def test_update_redirects_to_edit(self):
        """更新したあとは編集画面へ。留まる形は今までと同じ。"""
        sde_id = self.add_sde()

        res = self.post_no_redirect(
            URL_PREFIX + "/",
            cmd="update",
            sde_id=sde_id,
            orig_date=DATE1_STR,
            date=DATE1_STR,
            sde_type="会議",
            title="直した予定",
        )

        assert res.code == 302
        location = res.headers["Location"]
        assert location.startswith(f"{URL_PREFIX}/edit/?")
        assert f"sde_id={sde_id}" in location

    def test_del_redirects_to_list(self):
        """削除したあとは一覧へ。"""
        sde_id = self.add_sde()

        res = self.post_no_redirect(
            URL_PREFIX + "/",
            cmd="del",
            sde_id=sde_id,
            orig_date=DATE1_STR,
            date=DATE1_STR,
        )

        assert res.code == 302
        assert f"date={DATE1_STR}" in res.headers["Location"]

    def test_search_str_is_not_in_url(self):
        """検索語は URL に入れず、``conf.json`` に保存する。

        URL に持たせるのは日付だけ、と決めた (TODO-050)。
        """
        res = self.post_no_redirect(
            URL_PREFIX + "/", date=DATE1_STR, search_str="ABC"
        )

        assert res.code == 302
        assert "search_str" not in res.headers["Location"]
        assert read_conf(self.datadir)["SearchStr"] == "abc"

    def test_get_with_date_query(self):
        """GET のクエリで渡した日付で表示できる (ブックマーク)。"""
        body = self.get_body(URL_PREFIX + "/", date=DATE1_STR)

        assert f'value="{DATE1_STR}"' in body

    def test_edit_search_str_comes_from_conf(self):
        """編集画面の検索語は、URL ではなく ``conf.json`` から読む。

        URL に持たせるのは日付だけと決めた (TODO-050)。検索語は
        「検索中かどうか」の判定にしか使っていない
        (``edit.html`` の ``sde_align``)。
        """
        # 検索して ``conf.json`` に保存させる
        self.get_body(URL_PREFIX + "/", search_str="会議")

        with mock.patch.object(EditHandler, "render") as render:
            self.fetch(f"{URL_PREFIX}/edit/?date={DATE1_STR}")

        assert render.call_args.kwargs["search_str"] == "会議"

    def test_update_does_not_put_search_str_in_url(self):
        """更新したあとの飛び先にも、検索語は付けない (TODO-050)。"""
        self.get_body(URL_PREFIX + "/", search_str="会議")
        sde_id = self.add_sde()

        res = self.post_no_redirect(
            URL_PREFIX + "/",
            cmd="update",
            sde_id=sde_id,
            orig_date=DATE1_STR,
            date=DATE1_STR,
            sde_type="会議",
            title="直した予定",
        )

        assert res.code == 302
        assert "search_str" not in res.headers["Location"]

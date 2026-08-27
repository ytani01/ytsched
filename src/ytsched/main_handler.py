#
# (c) 2026 ytani01
#
"""
MainHandler
"""

__author__ = "ytani01"
__date__ = "2021/01"

import datetime
import re
import urllib.parse
from collections.abc import Callable
from typing import ClassVar

import tornado.web

from . import handler_util
from .handler import HandlerBase
from .mylog import getLogger
from .sched_load import SchedLoadCond, SchedLoader, SchedSearchCond
from .sched_update import SchedUpdateForm, SchedUpdater
from .ytsched import SchedData, normalize


class MainHandler(HandlerBase):
    """
    Web request handler
    """

    __log = getLogger(__qualname__)

    # SEARCH_MODE_DAYS は SchedLoader にある (TODO-088)。
    # SEARCH_MODE_MAX_DAYS は handler_util にある (TODO-081)
    DEF_SEARCH_N = 5

    # ``LoadMonths`` を読むのは MainHandler だけ (TODO-081)
    CONF_KEY_LOAD_MONTHS = "LoadMonths"

    # 以下も MainHandler だけが読み書きする (TODO-082)
    CONF_KEY_TODO_DAYS = "ToDo_Days"
    CONF_KEY_FILTER_STR = "FilterStr"
    CONF_KEY_SEARCH_N = "SearchN"

    TODO_DAYS: ClassVar[dict[str, int]] = {
        "off": -1,
        "today": 0,
        "1d": 1,
        "3d": 3,
        "1w": 7,
        "2w": 14,
        "1m": 30,
        "1y": 365,
        "all": 365 * 100,
    }
    DEF_TODO_DAYS = 365

    DELTA_DAY1 = datetime.timedelta(1)

    #: 前後どれだけの週を DOM に持たせるか (ヶ月。TODO-069)。
    #: ``conf.json`` の ``LoadMonths`` で変えられる
    DEF_LOAD_MONTHS = 1
    LOAD_MONTHS_MIN = 0
    LOAD_MONTHS_MAX = 24
    #: ヶ月を週の数に直すときの、1 ヶ月の日数 (TODO-069)
    DAYS_PER_MONTH = 30

    def initialize(self, sd: SchedData) -> None:
        """``sd`` を受け取り、更新の実行役 (``SchedUpdater``) と
        読み込みの実行役 (``SchedLoader``) を作る (TODO-087・TODO-088)。
        """
        super().initialize(sd)
        self._updater = SchedUpdater(sd)
        self._loader = SchedLoader(sd)

    def post(self):
        """POST。値を保存して ``cmd`` を実行し、GET へ飛ばす (TODO-050)。

        描画は GET に任せる (POST-Redirect-GET)。**リロードしても
        再送信にならない**ようにするため。TODO-050 より前は、ここで
        ``get()`` を呼んでそのまま描いていた。

        POST で来るのは、``cmd`` (追加・修正・更新・削除) と、
        ``main.html`` の 3 つのフォーム (検索・ToDo の日数・絞り込み)。
        どれも値を ``conf.json`` へ保存するので、読むだけで保存される
        (``get_conf_arg()``)。
        """
        self.__log.debug(f"request={self.request.__dict__}")
        self.__log.debug(
            f"request.body_arguments={self.request.body_arguments}"
        )

        #
        # ``conf.json`` へ保存される値を読む (``get()`` と同じ変換)
        #
        _ = self.get_conf_arg(
            "search_str",
            self.CONF_KEY_SEARCH_STR,
            "",
            empty_is_given=True,
            convert=normalize,
        )
        _ = self.get_conf_arg(
            "filter_str",
            self.CONF_KEY_FILTER_STR,
            "",
            empty_is_given=True,
            convert=normalize,
        )
        _ = self.get_conf_arg(
            "todo_days",
            self.CONF_KEY_TODO_DAYS,
            self.DEF_TODO_DAYS,
            empty_is_given=False,
            convert=self.str2todo_days,
        )
        _ = self.get_conf_arg(
            "search_n",
            self.CONF_KEY_SEARCH_N,
            self.DEF_SEARCH_N,
            empty_is_given=True,
            convert=int,
        )

        #
        # command (add/fix/update/del)
        #
        modified_date, edit_url = self.exec_cmd()

        if edit_url:
            self.redirect(edit_url)
            return

        #
        # 表示する日付は、今までどおりの優先順位で決めてから渡す
        # (``cur_day`` などは GET には引き継がれないため)
        #
        date = self.get_date(modified_date)

        self.redirect(
            self.mkurl(
                self._url_prefix,
                {
                    "date": date,
                    "sde_align": self.get_argument("sde_align", None),
                },
            )
        )

    @staticmethod
    def mkurl(path: str, args: dict[str, object | None]) -> str:
        """パスとクエリから URL を組み立てる (TODO-050)。

        値が ``None`` や空のものは入れない。

        Parameters
        ----------
        path: str
        args: dict[str, object | None]

        Returns
        -------
        str

        """
        params = {key: str(val) for key, val in args.items() if val}
        if not params:
            return path

        return f"{path}?{urllib.parse.urlencode(params)}"

    def get(self):
        """GET method and rendering"""
        self.__log.debug(f"request={self.request}")
        self.__log.debug(f"request.path={self.request.path}")

        #
        # search_str
        #
        # 照合される側 (``SchedDataEnt.search_str()``) と同じ
        # ``normalize()`` を通す (TODO-029)。
        # 変換後の値を ``conf.json`` へ保存する
        search_str = self.get_conf_arg(
            "search_str",
            self.CONF_KEY_SEARCH_STR,
            "",
            empty_is_given=True,
            convert=normalize,
        )
        self.__log.debug(f"search_str='{search_str}'")

        #
        # set Date
        #
        date = self.get_date(None)

        #
        # todo_days_value
        #
        todo_days_value = self.get_conf_arg(
            "todo_days",
            self.CONF_KEY_TODO_DAYS,
            self.DEF_TODO_DAYS,
            empty_is_given=False,
            convert=self.str2todo_days,
        )
        self.__log.debug(f"todo_days_value={todo_days_value!a}")

        #
        # sde_align
        #
        sde_align = self.get_sde_align()

        #
        # filter_str
        #
        # 空文字は「絞り込みの解除」(TODO-028)。
        # ``normalize()`` を通してから ``conf.json`` へ保存する
        # (小文字化に加えて、全角括弧が半角になる。TODO-029)
        filter_str = self.get_conf_arg(
            "filter_str",
            self.CONF_KEY_FILTER_STR,
            "",
            empty_is_given=True,
            convert=normalize,
        )
        self.__log.debug(f"filter_str={filter_str!a}")

        #
        # 正規表現のコンパイル (TODO-012)
        #
        # 不正な正規表現は、その条件を無視して全件を出す。
        # 入力欄には元の文字列を残すので、マッチに使う変数だけ分ける。
        #
        filter_re, filter_neg, filter_error = self.compile_filter(filter_str)
        search_re, search_error = self.compile_search(search_str)

        # 検索モードかどうか (不正な正規表現のときは検索しない)
        search_mode = search_re is not None
        self.__log.debug(
            f"search_mode={search_mode},"
            f" filter_error={filter_error}, search_error={search_error}"
        )

        #
        # search_n
        #
        search_n = self.get_conf_arg(
            "search_n",
            self.CONF_KEY_SEARCH_N,
            self.DEF_SEARCH_N,
            empty_is_given=True,
            convert=int,
        )
        self.__log.debug(f"search_n={search_n}")

        #
        # 前後どれだけの週を持たせるか (TODO-069)
        #
        load_months = self.get_load_months()
        self.__log.debug(f"load_months={load_months}")

        #
        # load ToDo
        #
        todo_sde, todo_today_sde = self._loader.load_todo(
            filter_re, filter_neg, search_re, todo_days_value
        )

        #
        # load schedule data
        #
        cond = SchedLoadCond(
            filter_re=filter_re,
            filter_neg=filter_neg,
            todo_days_value=todo_days_value,
            todo_today_sde=todo_today_sde,
            todo_by_date=self._loader.mk_todo_by_date(
                search_re, todo_days_value, todo_sde
            ),
        )
        # 検索モードかどうかは ``search_re`` そのもので分ける
        # (``search_mode`` と同じ条件。型チェッカもここで絞り込める)
        if search_re is not None:
            sched, date_from, date_to = self._loader.search(
                date, cond, SchedSearchCond(search_re, search_n)
            )
        else:
            sched, date_from, date_to = self._loader.load_week(date, cond)

        #
        # 前後の週も一緒に描いて返す (TODO-057・TODO-069・TODO-088)
        #
        weeks = self.mk_weeks(
            date, cond, sched, date_from, search_mode, load_months
        )

        #
        # render
        #
        today = datetime.date.today()
        self.render(
            self.HTML_MAIN,
            title=self._title,
            author=self._author,
            version=self._version,
            url_prefix=self._url_prefix,
            today=today,
            delta_day1=self.DELTA_DAY1,
            date=date,
            date_from=date_from,
            date_to=date_to,
            sched=sched,
            weeks=weeks,
            todo_days_list=self.TODO_DAYS,
            todo_days_value=todo_days_value,
            filter_str=filter_str,
            search_str=search_str,
            search_mode=search_mode,
            filter_error=filter_error,
            search_error=search_error,
            search_n=search_n,
            sde_align=sde_align,
            sd=self._sd,
        )

    def mk_weeks(
        self,
        date: datetime.date,
        cond: SchedLoadCond,
        sched: list[dict],
        date_from: datetime.date,
        search_mode: bool,
        load_months: int,
    ) -> list[dict[str, object]]:
        """前後の週も一緒に描くための ``weeks`` を組み立てる
        (TODO-057・TODO-069・TODO-088)。

        スワイプで指に追従させるため隣の週を出していたのを、前後
        ``load_months`` ヶ月ぶんへ広げた。ブラウザはこの中を動く
        かぎり、ページを読み直さない。
        検索モードは週の区切りに合わないので、今の週だけ (1 要素)。

        検索モードでも ``monday`` には ``date`` を含む週の月曜を
        入れておく (TODO-088)。``data-monday`` を出すかどうかは
        テンプレート側で ``search_mode`` を見て決める。

        Parameters
        ----------
        date: datetime.date
        cond: SchedLoadCond
        sched: list[dict]
            いまの週 (検索モードでは検索結果) の ``sched``
        date_from: datetime.date
            通常モードでは、いまの週の月曜
        search_mode: bool
        load_months: int

        Returns
        -------
        list[dict[str, object]]

        """
        if search_mode:
            # 検索モードの範囲は週の区切りに合わないので、隣の週は
            # 持たせない (TODO-069)。DOM の中で週を移ることも無い
            monday = date - datetime.timedelta(date.weekday())
            return [{"offset": 0, "monday": monday, "sched": sched}]

        weeks: list[dict[str, object]] = []
        weeks_n = self.months2weeks(load_months)
        for offset in range(-weeks_n, weeks_n + 1):
            monday = date_from + datetime.timedelta(7 * offset)
            if offset == 0:
                sched_offset = sched
            else:
                sched_offset, _, _ = self._loader.load_week(monday, cond)
            weeks.append(
                {
                    "offset": offset,
                    "monday": monday,
                    "sched": sched_offset,
                }
            )

        return weeks

    def str2ymd_date(self, value: str) -> datetime.date:
        """``year/month/day`` の形の文字列を日付にする (TODO-027)。

        ``convert_value()`` に渡す変換関数。``ymd2date()`` が 3 つの
        引数を ``/`` で繋いで渡す。数が合わなければ ``ValueError``。

        年・月・日は、``datetime.date()`` へ渡す**前に**、それぞれの
        範囲を見る (``check_int_range()``)。日が月末を越えているか
        どうかは ``datetime.date()`` が見る。

        Parameters
        ----------
        value: str
            ``2021/3/1`` の形 (0 詰めはしない)

        Returns
        -------
        datetime.date

        """
        year_str, month_str, day_str = value.split("/")

        year = handler_util.check_int_range(
            "year", int(year_str), datetime.MINYEAR, datetime.MAXYEAR
        )
        month = handler_util.check_int_range("month", int(month_str), 1, 12)
        day = handler_util.check_int_range("day", int(day_str), 1, 31)

        return handler_util.check_date(datetime.date(year, month, day))

    def str2todo_days(self, value: str) -> int:
        """ToDo の期間 (日数) にする (TODO-027)。

        ``convert_value()`` に渡す変換関数。数字にならない値も、
        画面で選べる範囲 (``TODO_DAYS``) の外も ``ValueError``。
        範囲外の日数は、``load_todo()`` の
        ``today + datetime.timedelta(todo_days_value)`` が
        ``OverflowError`` になる。

        Parameters
        ----------
        value: str

        Returns
        -------
        int

        """
        return handler_util.check_int_range(
            "todo_days",
            int(value),
            min(self.TODO_DAYS.values()),
            max(self.TODO_DAYS.values()),
        )

    def str2load_months(self, value: str) -> int:
        """DOM に持たせる前後の月数にする (TODO-069)。

        ``convert_value()`` に渡す変換関数。数字にならない値も、
        ``LOAD_MONTHS_MIN``〜``LOAD_MONTHS_MAX`` の外も ``ValueError``。

        Parameters
        ----------
        value: str

        Returns
        -------
        int

        """
        return handler_util.check_int_range(
            self.CONF_KEY_LOAD_MONTHS,
            int(value),
            self.LOAD_MONTHS_MIN,
            self.LOAD_MONTHS_MAX,
        )

    def get_load_months(self) -> int:
        """DOM に持たせる前後の月数を ``conf.json`` から読む (TODO-069)。

        **他の設定と違い、リクエストの引数では変えられない。**
        画面から変えるものではなく、利用者が ``conf.json`` へ手で
        書く値なので、``get_conf_arg()`` を通さず読むだけにする
        （``set_conf()`` しないので、手で書いた値は消えない）。

        読めない値 (数字にならない、範囲の外) は警告を 1 行出して
        既定値へ落とす。不正な引数の扱い (TODO-027) と同じ。

        Returns
        -------
        int

        """
        value = self.get_conf(self.CONF_KEY_LOAD_MONTHS)
        if value is None:
            return self.DEF_LOAD_MONTHS

        converted = handler_util.convert_value(
            self.CONF_KEY_LOAD_MONTHS, value, self.str2load_months
        )
        if converted is None:
            return self.DEF_LOAD_MONTHS

        return converted

    @classmethod
    def months2weeks(cls, months: int) -> int:
        """月数を、前後それぞれの週の数に直す (TODO-069)。

        1 ヶ月を ``DAYS_PER_MONTH``(30) 日として数える。暦の月に
        合わせないのは、**前後で週の数が変わると DOM の並びが
        左右で非対称になる**ため。

        Parameters
        ----------
        months: int

        Returns
        -------
        int

        """
        return round(months * cls.DAYS_PER_MONTH / 7)

    def get_conf_arg[T](
        self,
        arg_name: str,
        conf_key: str,
        default: T,
        *,
        empty_is_given: bool,
        convert: Callable[[str], T],
    ) -> T:
        """引数か ``conf.json`` から設定値を取り出す。

        引数が渡されていれば、その値を使い、``conf.json`` の値と違えば
        保存する。渡されていなければ ``conf.json`` の値、それも無ければ
        ``default`` を使う。

        ``empty_is_given`` は、**空文字を「渡された」とみなすか**。
        ``search_str``/``filter_str``/``search_n`` は ``True``、
        ``todo_days`` だけ ``False`` (TODO-021・TODO-028)。

        値は ``convert`` を通してから返す。**変換できない値は「渡されて
        いない」のと同じ扱いにして、``conf.json`` へ保存しない**
        (TODO-027)。``conf.json`` に既に入っている値も、変換できなければ
        ``default`` へ落とす。

        ``conf.json`` へ保存するのは、**変換したあとの値**
        (``search_str``/``filter_str`` なら ``normalize()`` を通したもの。
        TODO-028・TODO-029)。ただし ``search_n``/``todo_days`` のように
        文字列でない値になるものは、渡された文字列のまま保存する。

        Parameters
        ----------
        arg_name: str
            リクエスト引数の名前
        conf_key: str
            ``conf.json`` のキー
        default: T
            引数も ``conf.json`` も無い (または変換できない) ときの値
        empty_is_given: bool
        convert: Callable[[str], T]
            ``search_n`` は ``int``、``todo_days`` は
            ``str2todo_days()``、``search_str``/``filter_str`` は
            ``normalize()``。**``normalize()`` は失敗しないので検証には
            ならない** (揃えるためと、返す型を決めるために渡している)

        Returns
        -------
        T

        """
        conf_value = self.get_conf(conf_key)
        value = self.get_argument(arg_name, None)
        self.__log.debug(f"{arg_name}={value!a}, {conf_key}={conf_value!a}")

        if value is not None and (empty_is_given or value):
            converted = handler_util.convert_value(arg_name, value, convert)
            if converted is not None:
                # 保存するのは、実際に使う値 (TODO-028)。
                # 文字列にならないものは、渡された文字列のまま
                save_value = (
                    converted if isinstance(converted, str) else value
                )
                if save_value != conf_value:
                    self.set_conf(conf_key, save_value)
                return converted

        if conf_value:
            converted = handler_util.convert_value(
                conf_key, conf_value, convert
            )
            if converted is not None:
                return converted

        return default

    def exec_cmd(self) -> tuple[datetime.date | None, str | None]:
        """``cmd`` (add/fix/update/del) を実行する。

        Returns
        -------
        modified_date: datetime.date | None
        edit_url: str | None
            編集画面へ戻すときの行き先 (``cmd=update``)。TODO-050 より
            前はここで編集画面を描いていたが、``post()`` がリダイレクト
            するようになったので、行き先だけを返す

        """
        cmd = self.get_argument("cmd", None)

        if cmd not in ["add", "fix", "update", "del"]:
            return None, None

        form = self.get_update_form(cmd)
        modified_date, modified_sde_id = self._updater.exec_update(form)
        self.__log.debug(
            f"modified_date={modified_date}, modified_sde_id={modified_sde_id}"
        )

        if cmd in ["del"]:
            self.__log.debug(f"modified_date={modified_date}")
            return modified_date, None

        sde = self._updater.get_modified_sde(modified_date, modified_sde_id)
        if sde is None:
            # 更新したはずのデータが見つからない (TODO-016)
            raise tornado.web.HTTPError(
                404,
                "sde not found: date=%s, sde_id=%s (cmd=%s)",
                modified_date,
                modified_sde_id,
                cmd,
            )

        todo_flag = sde.is_todo()
        if todo_flag:
            modified_date = sde.date

        self.__log.debug(f"modified_date={modified_date}")

        if cmd in ["update"]:
            # 更新したあとも編集画面に留まる。編集画面の ``orig_date``
            # (読み直したファイルの日付) は ``EditHandler`` が決めるので、
            # ここからは送らない (TODO-029・TODO-034)
            edit_url = self.mkurl(
                self._url_prefix + "edit/",
                {
                    "date": modified_date,
                    "sde_id": modified_sde_id,
                    "todo_flag": str(todo_flag).lower(),
                },
            )
            return modified_date, edit_url

        return modified_date, None

    def get_update_form(self, cmd: str) -> SchedUpdateForm:
        """フォームの引数を取り出して ``SchedUpdateForm`` に詰める
        (TODO-087)。

        ``orig_date`` → ``date`` → 時刻 → その他、の順は変えない
        (空でないのに読めない値を、書き込みが 1 つも起きる前に 400 で
        断るため。TODO-027)。

        Parameters
        ----------
        cmd: str

        Returns
        -------
        SchedUpdateForm

        """
        # get orig_date
        # ``get_date_arg()``/``get_time_arg()`` は、空でないのに読めない
        # 値を 400 で断る。書き込みが 1 つも起きる前に弾くために、
        # ``cmd_del()``/``cmd_add()`` より先に呼んでおく (TODO-027)
        orig_date = self.get_date_arg("orig_date")
        self.__log.debug(f"orig_date={orig_date}")

        # get (new) date
        date = self.get_date_arg("date")
        self.__log.debug(f"date={date}")

        # get times
        time_start = self.get_time_arg("time_start")
        time_end = self.get_time_arg("time_end")
        self.__log.debug(f"time_start, time_end: {time_start}-{time_end}")

        # get sde_type, title, place
        sde_type = self.get_argument("sde_type", "")
        title = self.get_argument("title", "")
        place = self.get_argument("place", "")
        self.__log.debug(f"[{sde_type}]{title}@{place}")

        # get detail
        detail = self.get_argument("detail", "")
        self.__log.debug(f"detail:'{detail}'")

        # set deadline_*
        (
            deadline_date_str,
            deadline_time_start_str,
            deadline_time_end_str,
        ) = self.get_deadline_str()

        # sde_id
        sde_id: str | None = self.get_argument("sde_id")
        self.__log.debug(f"sde_id={sde_id}")

        return SchedUpdateForm(
            cmd=cmd,
            sde_id=sde_id,
            orig_date=orig_date,
            date=date,
            time_start=time_start,
            time_end=time_end,
            sde_type=sde_type,
            title=title,
            place=place,
            detail=detail,
            deadline_date_str=deadline_date_str,
            deadline_time_start_str=deadline_time_start_str,
            deadline_time_end_str=deadline_time_end_str,
        )

    def get_date(self, modified_date: datetime.date | None) -> datetime.date:
        """表示する日付を決める。

        強い順に ``year``+``month``+``day``、``modified_date``、
        ``date``、``cur_day``、今日。

        Parameters
        ----------
        modified_date: datetime.date | None

        Returns
        -------
        datetime.date

        """
        cur_day = datetime.date.today()  # default

        cur_day_str = self.get_argument("cur_day", None)
        if cur_day_str:
            # 日付として読めなければ今日のまま (TODO-027)
            parsed = handler_util.convert_value(
                "cur_day", cur_day_str, handler_util.str2date
            )
            if parsed is not None:
                cur_day = parsed
        self.__log.debug(f"cur_day={cur_day}")

        date = None  # default

        date_str = self.get_argument("date", None)
        self.__log.debug(f"date_str={date_str}")
        if date_str:
            # 日付として読めなければ「指定が無かった」のと同じ (TODO-027)
            date = handler_util.convert_value(
                "date", date_str, handler_util.str2date
            )

        if modified_date:
            date = modified_date

        year = self.get_argument("year", None)
        month = self.get_argument("month", None)
        day = self.get_argument("day", None)

        if year and month and day:
            # 日付にならなければ「指定が無かった」のと同じ (TODO-027)
            parsed = self.ymd2date(year, month, day)
            if parsed is not None:
                date = parsed

        if not date:
            date = cur_day

        self.__log.debug(f"date={date}")
        return date

    def ymd2date(
        self, year: str, month: str, day: str
    ) -> datetime.date | None:
        """``year``/``month``/``day`` を日付にする (TODO-027)。

        数字にならない値も、``month=13``/``day=32`` のような範囲外も、
        表示に使えないほど遠い日付も ``None`` を返して、警告を 1 行
        出す。変換と警告は ``convert_value()`` に任せるので、3 つを
        ``year/month/day`` の形に繋いでから渡す。

        Parameters
        ----------
        year: str
        month: str
        day: str

        Returns
        -------
        datetime.date | None
            日付にならなければ ``None``

        """
        return handler_util.convert_value(
            "year/month/day", f"{year}/{month}/{day}", self.str2ymd_date
        )

    def get_sde_align(self) -> str:
        """スケジュールの表示位置 (``top``/``bottom``)。"""
        sde_align = self.get_argument("sde_align", None)
        self.__log.debug(f"sde_align={sde_align}")
        if not sde_align:
            sde_align = "top"
            self.__log.debug(f"[fix]sde_align={sde_align}")

        return sde_align

    def compile_filter(
        self, filter_str: str
    ) -> tuple[re.Pattern[str] | None, bool, bool]:
        """絞り込み用の正規表現をコンパイルする。

        Parameters
        ----------
        filter_str: str

        Returns
        -------
        filter_re: re.Pattern[str] | None
            不正な正規表現のときは ``None``
        filter_neg: bool
            ``!`` 始まり(否定)かどうか
        filter_error: bool

        """
        filter_neg = filter_str.startswith("!")
        filter_pattern = filter_str[1:] if filter_neg else filter_str
        filter_re = self.compile_re(filter_pattern)

        return filter_re, filter_neg, filter_re is None

    def compile_search(
        self, search_str: str
    ) -> tuple[re.Pattern[str] | None, bool]:
        """検索用の正規表現をコンパイルする。

        Parameters
        ----------
        search_str: str

        Returns
        -------
        search_re: re.Pattern[str] | None
            検索しない、または不正な正規表現のときは ``None``
        search_error: bool

        """
        search_re = None
        if search_str:
            search_re = self.compile_re(search_str)

        return search_re, bool(search_str) and search_re is None

    def compile_re(self, pattern: str) -> re.Pattern[str] | None:
        """正規表現をコンパイルする。

        Parameters
        ----------
        pattern: str

        Returns
        -------
        re.Pattern[str] | None
            不正な正規表現の場合は ``None``

        """
        try:
            return re.compile(pattern)
        except re.error as ex:
            self.__log.warning(f"{type(ex).__name__}:{ex}:{pattern!a}")
            return None

    def get_date_arg(self, arg_name: str) -> datetime.date | None:
        """フォームの引数を日付として取り出す（空なら ``None``）。

        書き込む経路 (``exec_update()``) 専用。**空でないのに日付として
        読めない値**（形式が不正、または ``date_range()`` の外）は
        400 で断る (TODO-027)。表示の経路のように既定値へ落とすと、
        利用者が指定していない日へデータが動いてしまうため。

        空のときは今までどおり ``None``。``date`` なら
        ``SchedDataEnt`` 側で今日になり (TODO-016)、``orig_date`` なら
        ToDo のファイルを指す。

        Parameters
        ----------
        arg_name: str

        Returns
        -------
        datetime.date | None

        Raises
        ------
        tornado.web.HTTPError
            空でないのに日付として読めないとき (400)

        """
        value = self.get_argument(arg_name, None)
        if not value:
            return None

        date = handler_util.convert_value(
            arg_name, value, handler_util.str2date
        )
        if date is None:
            raise tornado.web.HTTPError(
                400, "invalid date: %s=%r", arg_name, value
            )

        return date

    def get_time_arg(self, arg_name: str) -> datetime.time | None:
        """フォームの引数を時刻として取り出す（空なら ``None``）。

        ``get_date_arg()`` と同じで、**空でないのに時刻として読めない
        値**は 400 で断る (TODO-027)。

        Parameters
        ----------
        arg_name: str

        Returns
        -------
        datetime.time | None

        Raises
        ------
        tornado.web.HTTPError
            空でないのに時刻として読めないとき (400)

        """
        value = self.get_argument(arg_name, None)
        if not value:
            return None

        time = handler_util.convert_value(
            arg_name, value, datetime.time.fromisoformat
        )
        if time is None:
            raise tornado.web.HTTPError(
                400, "invalid time: %s=%r", arg_name, value
            )

        return time

    def get_deadline_str(self) -> tuple[str, str, str]:
        """締切(``deadline_*``)のフォーム引数を取り出す。

        Returns
        -------
        deadline_date_str: str
        deadline_time_start_str: str
        deadline_time_end_str: str
            空でなければ先頭に ``-`` が付く

        """
        deadline_date_str = self.get_argument("deadline_date", "")
        deadline_time_start_str = self.get_argument("deadline_time_start", "")
        deadline_time_end_str = self.get_argument("deadline_time_end", "")
        if deadline_time_end_str:
            deadline_time_end_str = "-" + deadline_time_end_str

        self.__log.debug(
            f"deadline: {deadline_date_str} {deadline_time_start_str}"
            f"{deadline_time_end_str}"
        )

        return (
            deadline_date_str,
            deadline_time_start_str,
            deadline_time_end_str,
        )

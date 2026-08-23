#
# (c) 2021 Yoichi Tanibayashi
#
"""
MainHandler
"""

__author__ = "Yoichi Tanibayashi"
__date__ = "2021/01"

import datetime
import math
import re
from collections.abc import Callable
from typing import ClassVar

import tornado.web

from .handler import HandlerBase
from .mylog import getLogger
from .ytsched import SchedDataEnt


def days2y_offset(days: float) -> int:
    """
    Parameters
    ----------
    days: float

    Returns
    -------
    y_offset: int

    """
    dd = 0.6
    a = 70
    b = 0

    if days == 0:
        return 0

    y_offset = round(math.log10(float(abs(days)) + dd) * a + b)

    if days < 0:
        return -y_offset
    return y_offset


DAYS_YEAR = 31 + 28.25 + 31 + 30 + 31 + 30 + 31 + 31 + 30 + 31 + 30 + 31
DAYS_MONTH = DAYS_YEAR / 12

GAGE = [
    {"label": "-30y", "y_offset": days2y_offset(-DAYS_YEAR * 30)},
    {"label": "-10y", "y_offset": days2y_offset(-DAYS_YEAR * 10)},
    {"label": "-3y", "y_offset": days2y_offset(-DAYS_YEAR * 3)},
    {"label": "-1y", "y_offset": days2y_offset(-DAYS_YEAR * 1)},
    {"label": "-3m", "y_offset": days2y_offset(-DAYS_MONTH * 3)},
    {"label": "-1m", "y_offset": days2y_offset(-DAYS_MONTH * 1)},
    {"label": "-1w", "y_offset": days2y_offset(-7)},
    {"label": "-3d", "y_offset": days2y_offset(-3)},
    {"label": "+3d", "y_offset": days2y_offset(+3)},
    {"label": "+1w", "y_offset": days2y_offset(+7)},
    {"label": "+1m", "y_offset": days2y_offset(+DAYS_MONTH * 1)},
    {"label": "+3m", "y_offset": days2y_offset(+DAYS_MONTH * 3)},
    {"label": "+1y", "y_offset": days2y_offset(+DAYS_YEAR * 1)},
    {"label": "+3y", "y_offset": days2y_offset(+DAYS_YEAR * 3)},
    {"label": "+10y", "y_offset": days2y_offset(+DAYS_YEAR * 10)},
    {"label": "+30y", "y_offset": days2y_offset(+DAYS_YEAR * 30)},
]


class MainHandler(HandlerBase):
    """
    Web request handler
    """

    __log = getLogger(__qualname__)

    DEF_DAYS = 45
    # SEARCH_MODE_MAX_DAYS は HandlerBase にある (TODO-027)
    SEARCH_MODE_DAYS = 365
    DEF_SEARCH_N = 5

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

    COOKIE_TODO_DAYS = "todo_days"

    DELTA_DAY1 = datetime.timedelta(1)

    def post(self):
        """POST"""
        self.__log.debug(f"request={self.request.__dict__}")
        self.__log.debug(
            f"request.body_arguments={self.request.body_arguments}"
        )

        self.get()

    def get(self):
        """GET method and rendering"""
        self.__log.debug(f"request={self.request}")
        self.__log.debug(f"request.path={self.request.path}")

        #
        # search_str
        #
        search_str = self.get_conf_arg(
            "search_str",
            self.CONF_KEY_SEARCH_STR,
            "",
            empty_is_given=True,
            convert=str,
        )
        search_str = search_str.lower()
        self.__log.debug(f"search_str='{search_str}'")

        #
        # command (add/fix/del)
        #
        modified_date, modified_sde_id, rendered = self.exec_cmd(search_str)
        if rendered:
            return

        #
        # set Date
        #
        date = self.get_date(modified_date)

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
        filter_str = self.get_conf_arg(
            "filter_str",
            self.CONF_KEY_FILTER_STR,
            "",
            empty_is_given=False,
            convert=str,
        )
        filter_str = filter_str.lower()
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
        # load ToDo
        #
        todo_sde, todo_today_sde = self.load_todo(
            filter_re, filter_neg, search_re, todo_days_value
        )

        #
        # load schedule data
        #
        sched, date_from, date_to = self.load_sched(
            date,
            filter_re,
            filter_neg,
            search_re,
            search_mode,
            search_n,
            todo_days_value,
            todo_sde,
            todo_today_sde,
        )

        #
        # render
        #
        self.render(
            self.HTML_MAIN,
            title=self._title,
            author=self._author,
            version=self._version,
            url_prefix=self._url_prefix,
            today=datetime.date.today(),
            delta_day1=self.DELTA_DAY1,
            date=date,
            date_from=date_from,
            date_to=date_to,
            sched=sched,
            modified_sde_id=modified_sde_id,
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
            gage=GAGE,
        )

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

        year = self.check_int_range(
            "year", int(year_str), datetime.MINYEAR, datetime.MAXYEAR
        )
        month = self.check_int_range("month", int(month_str), 1, 12)
        day = self.check_int_range("day", int(day_str), 1, 31)

        return self.check_date(datetime.date(year, month, day))

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
        return self.check_int_range(
            "todo_days",
            int(value),
            min(self.TODO_DAYS.values()),
            max(self.TODO_DAYS.values()),
        )

    def get_conf_arg[T](
        self,
        arg_name: str,
        conf_key: str,
        default: T,
        *,
        empty_is_given: bool,
        convert: Callable[[str], T],
    ) -> T:
        """引数か ``Conf.cgi`` から設定値を取り出す。

        引数が渡されていれば、その値を使い、``Conf.cgi`` の値と違えば
        保存する。渡されていなければ ``Conf.cgi`` の値、それも無ければ
        ``default`` を使う。

        ``empty_is_given`` は、**空文字を「渡された」とみなすか**。
        ``search_str``/``search_n`` は ``True``、
        ``todo_days``/``filter_str`` は ``False`` で、
        4 つの取り出し方は揃っていない (TODO-021)。

        値は ``convert`` を通してから返す。**変換できない値は「渡されて
        いない」のと同じ扱いにして、``Conf.cgi`` へ保存しない**
        (TODO-027)。``Conf.cgi`` に既に入っている値も、変換できなければ
        ``default`` へ落とす。

        Parameters
        ----------
        arg_name: str
            リクエスト引数の名前
        conf_key: str
            ``Conf.cgi`` のキー
        default: T
            引数も ``Conf.cgi`` も無い (または変換できない) ときの値
        empty_is_given: bool
        convert: Callable[[str], T]
            ``search_n`` は ``int``、``todo_days`` は
            ``str2todo_days()``。``search_str``/``filter_str`` は
            ``str`` で、**これは失敗しないので検証にはならない**
            (返す型を決めるために渡している)

        Returns
        -------
        T

        """
        conf_value = self.get_conf(conf_key)
        value = self.get_argument(arg_name, None)
        self.__log.debug(f"{arg_name}={value!a}, {conf_key}={conf_value!a}")

        if value is not None and (empty_is_given or value):
            converted = self.convert_value(arg_name, value, convert)
            if converted is not None:
                if value != conf_value:
                    self.set_conf(conf_key, value)
                return converted

        if conf_value:
            converted = self.convert_value(conf_key, conf_value, convert)
            if converted is not None:
                return converted

        return default

    def exec_cmd(
        self, search_str: str
    ) -> tuple[datetime.date | None, str | None, bool]:
        """``cmd`` (add/fix/update/del) を実行する。

        Parameters
        ----------
        search_str: str
            ``update`` のときの描画に渡す

        Returns
        -------
        modified_date: datetime.date | None
        modified_sde_id: str | None
        rendered: bool
            描画まで済ませたかどうか。``True`` なら呼び出し側は
            そのまま ``return`` する

        """
        cmd = self.get_argument("cmd", None)

        if cmd not in ["add", "fix", "update", "del"]:
            return None, None, False

        modified_date, modified_sde_id = self.exec_update(cmd)
        self.__log.debug(
            f"modified_date={modified_date},"
            f" modified_sde_id={modified_sde_id}"
        )

        if cmd in ["del"]:
            self.__log.debug(f"modified_date={modified_date}")
            return modified_date, modified_sde_id, False

        sde = self.get_modified_sde(cmd, modified_date, modified_sde_id)

        todo_flag = sde.is_todo()
        if todo_flag:
            modified_date = sde.date

        self.__log.debug(f"modified_date={modified_date}")

        if cmd in ["update"]:
            self.render(
                self.HTML_EDIT,
                title=self._title,
                author=self._author,
                version=self._version,
                url_prefix=self._url_prefix,
                post_url=self._url_prefix,
                date=modified_date,
                sde=sde,
                new_flag=False,
                todo_flag=todo_flag,
                search_str=search_str,
            )
            return modified_date, modified_sde_id, True

        return modified_date, modified_sde_id, False

    def get_modified_sde(
        self,
        cmd: str,
        modified_date: datetime.date | None,
        modified_sde_id: str | None,
    ) -> SchedDataEnt:
        """更新したデータを読み直す。

        見つからなければ 404 (TODO-016)。

        Parameters
        ----------
        cmd: str
        modified_date: datetime.date | None
        modified_sde_id: str | None

        Returns
        -------
        SchedDataEnt

        """
        sdf = self._sd.get_sdf(modified_date)
        sde = sdf.get_sde(modified_sde_id)
        self.__log.debug(f"sde={sde}")

        if sde is None:
            # 更新したはずのデータが見つからない (TODO-016)
            raise tornado.web.HTTPError(
                404,
                "sde not found: date=%s, sde_id=%s (cmd=%s)",
                modified_date,
                modified_sde_id,
                cmd,
            )

        return sde

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
            parsed = self.convert_value("cur_day", cur_day_str, self.str2date)
            if parsed is not None:
                cur_day = parsed
        self.__log.debug(f"cur_day={cur_day}")

        date = None  # default

        date_str = self.get_argument("date", None)
        self.__log.debug(f"date_str={date_str}")
        if date_str:
            # 日付として読めなければ「指定が無かった」のと同じ (TODO-027)
            date = self.convert_value("date", date_str, self.str2date)

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
        return self.convert_value(
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

    def load_todo(
        self,
        filter_re: re.Pattern[str] | None,
        filter_neg: bool,
        search_re: re.Pattern[str] | None,
        todo_days_value: int,
    ) -> tuple[list[SchedDataEnt], list[SchedDataEnt]]:
        """ToDo を読み込む。

        Parameters
        ----------
        filter_re: re.Pattern[str] | None
        filter_neg: bool
        search_re: re.Pattern[str] | None
        todo_days_value: int

        Returns
        -------
        todo_sde: list[SchedDataEnt]
            後に、日々のスケジュール``out_sde``に統合
        todo_today_sde: list[SchedDataEnt]
            期限は先だが、今日に表示すべきToDo

        """
        today = datetime.date.today()

        todo_sdf = self._sd.get_sdf(None)
        todo_sde = []
        todo_today_sde = []
        for sde in todo_sdf.sde:
            if not self.filter_match(filter_re, filter_neg, sde):
                continue

            if not self.search_match(search_re, sde):
                continue

            todo_sde.append(sde)
            self.__log.debug(f"sde={sde}")

            if sde.date > today + datetime.timedelta(todo_days_value):
                continue

            if sde.date == today:
                continue

            todo_today_sde.append(sde)
            self.__log.debug(f"sde={sde}")

        return todo_sde, todo_today_sde

    def load_sched(
        self,
        date: datetime.date,
        filter_re: re.Pattern[str] | None,
        filter_neg: bool,
        search_re: re.Pattern[str] | None,
        search_mode: bool,
        search_n: int,
        todo_days_value: int,
        todo_sde: list[SchedDataEnt],
        todo_today_sde: list[SchedDataEnt],
    ) -> tuple[list[dict], datetime.date, datetime.date]:
        """表示する日々のスケジュールを集める。

        Parameters
        ----------
        date: datetime.date
        filter_re: re.Pattern[str] | None
        filter_neg: bool
        search_re: re.Pattern[str] | None
        search_mode: bool
        search_n: int
        todo_days_value: int
        todo_sde: list[SchedDataEnt]
        todo_today_sde: list[SchedDataEnt]

        Returns
        -------
        sched: list[dict]
        date_from: datetime.date
            検索モードでは、打ち切った日まで縮む
        date_to: datetime.date

        """
        sched = []
        date_from = date - datetime.timedelta(self._days)
        date_to = date + datetime.timedelta(self._days - 1)

        if search_mode:
            date_from = date - datetime.timedelta(self.SEARCH_MODE_MAX_DAYS)
            date_from1 = date - datetime.timedelta(self.SEARCH_MODE_DAYS)
            date_to = date

        search_count = 0
        date1 = date_to + self.DELTA_DAY1
        while date1 > date_from:
            if search_mode and search_count > 0:
                if search_count >= search_n:
                    date_from = date1
                    break

                if date1 <= date_from1:
                    date_from = date1
                    break

            date1 -= self.DELTA_DAY1

            sdf = self._sd.get_sdf(date1)

            out_sde = []
            for sde in sdf.sde:
                # self.__log.debug(f"sde={sde}")
                if not self.filter_match(filter_re, filter_neg, sde):
                    continue

                if not self.search_match(search_re, sde):
                    continue

                out_sde.append(sde)
                search_count += 1

            if todo_days_value >= 0:
                # todo_sde
                for sde in todo_sde:
                    if not self.search_match(search_re, sde):
                        continue

                    if sde.date == date1:
                        out_sde.append(sde)
                        self.__log.debug(f"out_sde.append:{sde}")

                # todo_today_sde
                if not search_mode and date1 == datetime.date.today():
                    out_sde.extend(todo_today_sde)

            if search_mode and not out_sde:
                continue

            out_sde = sorted(out_sde, key=lambda x: x.get_sortkey())

            sched.append(
                {"date": date1, "is_holiday": sdf.is_holiday, "sde": out_sde}
            )

        return sched[::-1], date_from, date_to

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

    def filter_match(
        self,
        filter_re: re.Pattern[str] | None,
        filter_neg: bool,
        sde: SchedDataEnt,
    ) -> bool:
        """``sde`` がフィルタに合うか。

        ``filter_re`` が ``None``(不正な正規表現)のときは、
        絞り込みを無視して常に ``True`` を返す。

        Parameters
        ----------
        filter_re: re.Pattern[str] | None
        filter_neg: bool
            ``!`` 始まり(否定)かどうか
        sde: SchedDataEnt

        Returns
        -------
        bool

        """
        if filter_re is None:
            return True

        found = filter_re.search(sde.search_str()) is not None
        return found != filter_neg

    def search_match(
        self,
        search_re: re.Pattern[str] | None,
        sde: SchedDataEnt,
    ) -> bool:
        """``sde`` が検索文字列に合うか。

        ``search_re`` が ``None``(検索しない、または不正な正規表現)の
        ときは、絞り込まずに常に ``True`` を返す。

        Parameters
        ----------
        search_re: re.Pattern[str] | None
        sde: SchedDataEnt

        Returns
        -------
        bool

        """
        if search_re is None:
            return True

        return search_re.search(sde.search_str()) is not None

    def exec_update(
        self, cmd: str
    ) -> tuple[datetime.date | None, str | None]:
        """
        Parameters
        ----------
        cmd: str

        Returns
        -------
        date: datetime.date | None
            更新された日付。ToDo の場合は None
        modified_sde_id: str | None
            更新されたスケジュールID。``del`` の場合は None
        """
        self.__log.debug("")

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

        if deadline_date_str and not SchedDataEnt.type_is_todo(sde_type):
            #
            # ToDoが完了した場合
            #
            date, time_start, time_end, detail = self.fix_todo_done(
                deadline_date_str,
                deadline_time_start_str,
                deadline_time_end_str,
                detail,
            )

        # sde_id
        sde_id: str | None = self.get_argument("sde_id")
        self.__log.debug(f"sde_id={sde_id}")

        # exec cmd
        self.__log.debug(f"EXEC: {cmd}")

        new_sde = None
        modified_sde_id = None

        if cmd in ["add"]:
            sde_id = None

        if cmd in ["del", "fix", "update"]:
            self.cmd_del(orig_date, sde_id)

        if cmd in ["add", "fix", "update"]:
            new_sde = self.cmd_add(
                sde_id,
                date,
                time_start,
                time_end,
                sde_type,
                title,
                place,
                detail,
            )

        if new_sde:
            modified_sde_id = new_sde.sde_id
            date = new_sde.date
            if new_sde.is_todo():
                date = None

        self.__log.debug(f"date={date}, modified_sde_id={modified_sde_id}")
        return date, modified_sde_id

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

        date = self.convert_value(arg_name, value, self.str2date)
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

        time = self.convert_value(
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

    def fix_todo_done(
        self,
        deadline_date_str: str,
        deadline_time_start_str: str,
        deadline_time_end_str: str,
        detail: str,
    ) -> tuple[datetime.date, datetime.time, datetime.time | None, str]:
        """ToDoが完了した場合の補正。

        ``date``, ``time_start``を現在日時にして、``detail``の先頭に
        元の締切を書き足す。

        Parameters
        ----------
        deadline_date_str: str
        deadline_time_start_str: str
        deadline_time_end_str: str
        detail: str

        Returns
        -------
        date: datetime.date
        time_start: datetime.time
        time_end: datetime.time | None
        detail: str

        """
        date = datetime.date.today()
        self.__log.debug(f"[fix] date={date}")

        time_start = datetime.datetime.now().time()
        # msec を切り捨てる
        time_start = datetime.time.fromisoformat(
            time_start.strftime(SchedDataEnt.TIME_FORMAT)
        )
        self.__log.debug(f"[fix] time_start={time_start}")
        time_end = None

        deadline_date = deadline_date_str.replace("-", "/")
        detail = (
            f"〆{deadline_date} "
            f"{deadline_time_start_str}{deadline_time_end_str}\n"
            f"{detail}"
        )
        self.__log.debug(f"[fix] detail={detail}")

        return date, time_start, time_end, detail

    def cmd_add(
        self,
        sde_id,
        date,
        time_start,
        time_end,
        sde_type,
        title,
        place,
        detail,
    ):
        """
        Parameters
        ----------
        sde_id: str
        date: datetime.date
        time_start, time_end:
        sde_type: str
        title: str
        place: str
        detail: str

        Returns
        -------
        new_sde: SchedDataEnt

        """
        self.__log.debug(f"sde_id={sde_id}, date={date}")

        new_sde = SchedDataEnt(
            sde_id,
            date,
            time_start,
            time_end,
            sde_type,
            title,
            place,
            detail,
        )
        if new_sde.is_todo():
            self._sd.add_sde(None, new_sde)
        else:
            # ``date`` が空でも ``SchedDataEnt`` 側で今日に補正される。
            # 書き込み先も ``new_sde.date`` に合わせる (TODO-016)
            self._sd.add_sde(new_sde.date, new_sde)

        return new_sde

    def cmd_del(self, date, sde_id):
        """
        Parameters
        ----------
        date: datetime.date

        sde_id: str

        """
        self.__log.debug(f"date={date}, sde_id={sde_id}")

        self._sd.del_sde(date, sde_id)

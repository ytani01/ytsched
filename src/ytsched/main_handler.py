#
# (c) 2026 ytani01
#
"""
MainHandler
"""

__author__ = "ytani01"
__date__ = "2021/01"

import datetime
import math
import re
import urllib.parse
from collections.abc import Callable
from typing import ClassVar

import tornado.web

from .handler import HandlerBase
from .mylog import getLogger
from .ytsched import SchedDataEnt, normalize


def days2x_percent(days: float) -> float:
    """今週の中心からの左右のずれを、ゲージの幅に対する割合 (%) で返す

    対数なので、日数が小さいところほど目盛りの間隔が広がる。そのままだと
    左右対称に置く ``-1w`` と ``+1w`` の間だけが広く空くので、
    ``DAYS_GAGE_K`` で割ってから対数を取って詰めている (TODO-059)。

    Parameters
    ----------
    days: float

    Returns
    -------
    x_percent: float

    """
    x_percent = (
        50.0
        * math.log10(1 + abs(days) / DAYS_GAGE_K)
        / math.log10(1 + DAYS_GAGE_MAX / DAYS_GAGE_K)
    )
    x_percent = min(x_percent, 50.0)

    if days < 0:
        return -x_percent
    return x_percent


DAYS_YEAR = 31 + 28.25 + 31 + 30 + 31 + 30 + 31 + 31 + 30 + 31 + 30 + 31
DAYS_MONTH = DAYS_YEAR / 12
DAYS_GAGE_MAX = DAYS_YEAR * 30


def calc_gage_label(date: datetime.date, today: datetime.date) -> str:
    """針の上に出す、今週からの差の文字 (TODO-072)。

    どちらも月曜へ丸めてから差を取る。同じ週なら ``±0``。1 ヶ月に
    届かないうちは週数 (``+3w``)、1 ヶ月から 1 年までは月数
    (``+1.2m``)、1 年からは年数 (``+1.2y``)。月と年は小数点以下 1 桁。

    JavaScript 側 (``my.js`` の ``gageDiffLabel()``) と同じ区切り・
    同じ書き方にしてある。読み込んだ直後の一度だけここが埋め、
    あとは JavaScript が書き換えるため、食い違うと針が動く前後で
    文字が変わって見える。

    Parameters
    ----------
    date: datetime.date
        表示している週の中の、どの日でもよい
    today: datetime.date

    Returns
    -------
    label: str

    """
    monday = date - datetime.timedelta(date.weekday())
    this_monday = today - datetime.timedelta(today.weekday())
    days = (monday - this_monday).days

    if days == 0:
        return "\u00b10"
    if abs(days) < DAYS_MONTH:
        return f"{days // 7:+d}w"
    if abs(days) < DAYS_YEAR:
        return f"{days / DAYS_MONTH:+.1f}m"
    return f"{days / DAYS_YEAR:+.1f}y"


# 中心の近くをどれだけ詰めるか (TODO-059)。大きいほど詰まる。10 のとき
# ``-1w`` と ``+1w`` の間隔が 7.6%。**これより大きくすると、幅 360px で
# ``1w`` と ``1m`` のラベルが重なる**（15 で重なることを実測した）ので、
# 上げるときは実際の見え方を確かめること
DAYS_GAGE_K = 10.0

GAGE = [
    {"label": "-30y", "x_percent": days2x_percent(-DAYS_YEAR * 30)},
    {"label": "-10y", "x_percent": days2x_percent(-DAYS_YEAR * 10)},
    {"label": "-3y", "x_percent": days2x_percent(-DAYS_YEAR * 3)},
    {"label": "-1y", "x_percent": days2x_percent(-DAYS_YEAR)},
    {"label": "-3m", "x_percent": days2x_percent(-DAYS_MONTH * 3)},
    {"label": "-1m", "x_percent": days2x_percent(-DAYS_MONTH)},
    {"label": "-1w", "x_percent": days2x_percent(-7)},
    {"label": "+1w", "x_percent": days2x_percent(+7)},
    {"label": "+1m", "x_percent": days2x_percent(+DAYS_MONTH)},
    {"label": "+3m", "x_percent": days2x_percent(+DAYS_MONTH * 3)},
    {"label": "+1y", "x_percent": days2x_percent(+DAYS_YEAR)},
    {"label": "+3y", "x_percent": days2x_percent(+DAYS_YEAR * 3)},
    {"label": "+10y", "x_percent": days2x_percent(+DAYS_YEAR * 10)},
    {"label": "+30y", "x_percent": days2x_percent(+DAYS_YEAR * 30)},
]


class MainHandler(HandlerBase):
    """
    Web request handler
    """

    __log = getLogger(__qualname__)

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

    DELTA_DAY1 = datetime.timedelta(1)

    #: 前後どれだけの週を DOM に持たせるか (ヶ月。TODO-069)。
    #: ``conf.json`` の ``LoadMonths`` で変えられる
    DEF_LOAD_MONTHS = 1
    LOAD_MONTHS_MIN = 0
    LOAD_MONTHS_MAX = 24
    #: ヶ月を週の数に直すときの、1 ヶ月の日数 (TODO-069)
    DAYS_PER_MONTH = 30

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
        search_str = self.get_conf_arg(
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
        modified_date, edit_url = self.exec_cmd(search_str)

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
        # 前後の週も一緒に描いて返す (TODO-057・TODO-069)
        #
        # スワイプで指に追従させるため隣の週を出していたのを、前後
        # ``load_months`` ヶ月ぶんへ広げた。ブラウザはこの中を動く
        # かぎり、ページを読み直さない。
        # 検索モードは週の区切りに合わないので、今の週だけ (1 要素)。
        #
        # ``monday`` は検索モードだけ None になるので、値の型を
        # 揃えずに ``object`` で受ける (テンプレートへ渡すだけ)
        weeks: list[dict[str, object]] = []
        if search_mode:
            # 検索モードの範囲は週の区切りに合わないので、月曜は
            # 持たせない (TODO-069)。DOM の中で週を移ることも無い
            weeks = [{"offset": 0, "monday": None, "sched": sched}]
        else:
            weeks_n = self.months2weeks(load_months)
            for offset in range(-weeks_n, weeks_n + 1):
                monday = date_from + datetime.timedelta(7 * offset)
                if offset == 0:
                    sched_offset = sched
                else:
                    sched_offset, _, _ = self.load_sched(
                        monday,
                        filter_re,
                        filter_neg,
                        search_re,
                        search_mode,
                        search_n,
                        todo_days_value,
                        todo_sde,
                        todo_today_sde,
                    )
                weeks.append(
                    {
                        "offset": offset,
                        "monday": monday,
                        "sched": sched_offset,
                    }
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
            gage_label=calc_gage_label(date, today),
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
        return self.check_int_range(
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

        converted = self.convert_value(
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
            converted = self.convert_value(arg_name, value, convert)
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
            converted = self.convert_value(conf_key, conf_value, convert)
            if converted is not None:
                return converted

        return default

    def exec_cmd(
        self, search_str: str
    ) -> tuple[datetime.date | None, str | None]:
        """``cmd`` (add/fix/update/del) を実行する。

        Parameters
        ----------
        search_str: str
            ``update`` のあと、編集画面へ引き継ぐ

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

        modified_date, modified_sde_id = self.exec_update(cmd)
        self.__log.debug(
            f"modified_date={modified_date}, modified_sde_id={modified_sde_id}"
        )

        if cmd in ["del"]:
            self.__log.debug(f"modified_date={modified_date}")
            return modified_date, None

        sde = self.get_modified_sde(cmd, modified_date, modified_sde_id)

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

    def mk_todo_by_date(
        self,
        search_re: re.Pattern[str] | None,
        todo_days_value: int,
        todo_sde: list[SchedDataEnt],
    ) -> dict[datetime.date, list[SchedDataEnt]]:
        """ToDo を期限の日付で引けるようにする (TODO-028)。

        ``load_sched()`` は 1 日ずつさかのぼるので、日ごとに
        ``todo_sde`` を全件見ると、日数 × 件数だけ照合が走る。
        先に日付でまとめておけば 1 回で済む。並び順は ``todo_sde`` の
        まま。

        ``todo_days_value`` が負のときは ToDo を混ぜないので、空の
        ``dict`` を返す。

        Parameters
        ----------
        search_re: re.Pattern[str] | None
        todo_days_value: int
        todo_sde: list[SchedDataEnt]

        Returns
        -------
        dict[datetime.date, list[SchedDataEnt]]

        """
        by_date: dict[datetime.date, list[SchedDataEnt]] = {}

        if todo_days_value < 0:
            return by_date

        for sde in todo_sde:
            if not self.search_match(search_re, sde):
                continue

            by_date.setdefault(sde.date, []).append(sde)

        return by_date

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
            通常モードでは ``date`` を含む週の月曜 (TODO-049)。
            検索モードでは、打ち切った日まで縮む
        date_to: datetime.date
            通常モードでは ``date_from`` の 6 日後 (日曜)

        Notes
        -----
        検索モードでは最大 ``SEARCH_MODE_MAX_DAYS``(1825) 日をさかのぼる
        ので、**データファイルが無い日は開きに行かない** (TODO-028)。
        開いても中身が空の ``SchedDataFile`` になるだけで、``sched`` の
        中身も ``search_count`` の数え方も変わらない。日付の欄そのものは
        今までどおり出す (検索モードで 1 件も当たらない日を落とすのは、
        下の ``if search_mode and not out_sde`` のほう)。

        ``todo_sde`` の照合も、日ごとに全件見ずに、日付で引けるように
        しておく (TODO-028)。

        """
        todo_by_date = self.mk_todo_by_date(
            search_re, todo_days_value, todo_sde
        )

        sched = []
        monday = date - datetime.timedelta(date.weekday())
        date_from = monday
        date_to = monday + datetime.timedelta(6)

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

            # ファイルが無い日は開きに行かない (TODO-028)
            sdf = None
            if self._sd.sdf_exists(date1):
                sdf = self._sd.get_sdf(date1)

            out_sde = []
            for sde in sdf.sde if sdf else []:
                # self.__log.debug(f"sde={sde}")
                if not self.filter_match(filter_re, filter_neg, sde):
                    continue

                if not self.search_match(search_re, sde):
                    continue

                out_sde.append(sde)
                search_count += 1

            if todo_days_value >= 0:
                # todo_sde
                out_sde.extend(todo_by_date.get(date1, []))

                # todo_today_sde
                if not search_mode and date1 == datetime.date.today():
                    out_sde.extend(todo_today_sde)

            if search_mode and not out_sde:
                continue

            out_sde = sorted(out_sde, key=lambda x: x.get_sortkey())

            sched.append(
                {
                    "date": date1,
                    "is_holiday": sdf.is_holiday if sdf else False,
                    "sde": out_sde,
                }
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
        deadline_time = f"{deadline_time_start_str}{deadline_time_end_str}"
        # 時刻が無ければ、区切りの空白も付けない (TODO-028)
        deadline_line = f"〆{deadline_date}"
        if deadline_time:
            deadline_line += f" {deadline_time}"

        detail = f"{deadline_line}\n{detail}"
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

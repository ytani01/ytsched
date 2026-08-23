#
# (c) 2020 Yoichi Tanibayashi
#
"""
HandlerBase
"""

__author__ = "Yoichi Tanibayashi"
__date__ = "2021/01"

import datetime
import os
from collections.abc import Callable

import tornado.web

from .mylog import getLogger


class HandlerBase(tornado.web.RequestHandler):
    """HandlerBase"""

    __log = getLogger(__qualname__)

    # 検索モードで遡る最大の日数。``date_range()`` が使うので、
    # ``MainHandler`` ではなくここに置く (TODO-027)
    SEARCH_MODE_MAX_DAYS = 365 * 5

    CONF_FNAME = "Conf.cgi"
    CONF_ENCODE = "utf-8"
    CONF_KEY_TODO_DAYS = "ToDo_Days"
    CONF_KEY_FILTER_STR = "FilterStr"
    CONF_KEY_SEARCH_STR = "SearchStr"
    CONF_KEY_SEARCH_N = "SearchN"

    HTML_MAIN = "main.html"
    HTML_EDIT = "edit.html"

    def __init__(self, app, req):
        """Constructor"""
        super().__init__(app, req)

        self.__log.debug(f"app={app}")
        self.__log.debug(f"req={req}")

        self._app = app
        self._req = req

        # 属性への代入は明示のまま(型チェッカが属性を追えなくなるため)
        self._title = app.settings.get("title")
        self._author = app.settings.get("author")
        self._version = app.settings.get("version")
        self._url_prefix = app.settings.get("url_prefix")
        self._datadir = app.settings.get("datadir")
        self._days = app.settings.get("days")
        self._sd = app.settings.get("sd")

        self._conf_file = os.path.join(self._datadir, self.CONF_FNAME)

        self.__log.debug(
            f"title={self._title}, author={self._author},"
            f" version={self._version}, url_prefix={self._url_prefix},"
            f" datadir={self._datadir}, days={self._days},"
            f" sd={self._sd}, conf_file={self._conf_file}"
        )

        self._conf = self.load_conf()

    def load_conf(self):
        """``Conf.cgi`` を読み込んで dict で返す。

        ファイルが無ければ空の dict を返す。
        """
        self.__log.debug("")

        conf: dict[str, str] = {}

        try:
            with open(self._conf_file, encoding=self.CONF_ENCODE) as f:
                lines = f.readlines()
        except FileNotFoundError:
            return conf

        for line in lines:
            line = line.rstrip("\n")
            if not line:
                continue

            self.__log.debug(f"line={line}")

            if "\t" not in line:
                self.__log.warning(f"{line!a}: no tab .. ignored")
                continue

            (param, value) = line.split("\t", maxsplit=1)
            self.__log.debug(f"{param!a},{value!a}.")
            conf[param] = value

        return conf

    def save_conf(self):
        """設定を ``Conf.cgi`` へ書き出す。"""
        self.__log.debug("")

        with open(self._conf_file, mode="w", encoding=self.CONF_ENCODE) as f:
            f.writelines(f"{p}\t{self._conf[p]}\n" for p in self._conf)

    def get_conf(self, name):
        """設定値を返す。無ければ ``None`` を返す。"""
        self.__log.debug(f"name={name}")

        return self._conf.get(name)

    def set_conf(self, name, value):
        """設定値を変更して、``Conf.cgi`` へ保存する。"""
        self.__log.debug(f"name={name}, value='{value}'")
        self._conf[name] = value
        self.save_conf()

    def convert_value[T](
        self, name: str, value: str, convert: Callable[[str], T]
    ) -> T | None:
        """文字列を ``convert`` で変換する (TODO-027)。

        変換できない値は ``None`` を返して、警告を 1 行出す。
        不正な正規表現の扱い (TODO-012) と揃えて、例外にはしない。

        ``convert`` には、**変換したあとに使える範囲かどうかまで見る**
        関数を渡す (``str2date()``/``str2todo_days()`` など)。範囲を
        見ないまま ``datetime.date()`` や ``datetime.timedelta()`` へ
        渡すと、``ValueError`` ではなく ``OverflowError`` になって、
        ここでは拾えない。

        Parameters
        ----------
        name: str
            警告に出す名前 (引数名か ``Conf.cgi`` のキー)
        value: str
        convert: Callable[[str], T]
            ``int`` や ``str2date()`` など

        Returns
        -------
        T | None
            変換できなければ ``None``

        """
        try:
            return convert(value)
        except ValueError as ex:
            self.__log.warning(f"{name}={value!a}: {ex} .. ignored")
            return None

    def date_range(self) -> tuple[datetime.date, datetime.date]:
        """表示に使える日付の範囲 (TODO-027)。

        ``load_sched()`` は、指定された日付から前後へ日をずらしながら
        スケジュールを集める。ずらす幅は最大で ``SEARCH_MODE_MAX_DAYS``
        日 (``--days`` がそれより大きければ、その日数)。
        ``datetime.date.min``/``datetime.date.max`` ぎりぎりの日付を
        受け取ると、この足し引きが ``OverflowError`` になるので、
        ずらす幅のぶんだけ内側を「使える範囲」とする。

        Returns
        -------
        tuple[datetime.date, datetime.date]
            使える日付の、最小と最大

        """
        margin = datetime.timedelta(
            max(self._days, self.SEARCH_MODE_MAX_DAYS)
        )
        return datetime.date.min + margin, datetime.date.max - margin

    def check_date(self, date: datetime.date) -> datetime.date:
        """``date_range()`` の外なら ``ValueError`` (TODO-027)。

        Parameters
        ----------
        date: datetime.date

        Returns
        -------
        datetime.date
            範囲内なら、そのまま返す

        """
        date_min, date_max = self.date_range()

        if not date_min <= date <= date_max:
            raise ValueError(
                f"date must be in {date_min}..{date_max}, not {date}"
            )

        return date

    def str2date(self, value: str) -> datetime.date:
        """ISO 8601 の文字列を、表示に使える日付にする (TODO-027)。

        ``convert_value()`` に渡す変換関数。日付として読めない値も、
        使える範囲の外の日付も ``ValueError``。

        Parameters
        ----------
        value: str

        Returns
        -------
        datetime.date

        """
        return self.check_date(datetime.date.fromisoformat(value))

    def check_int_range(
        self, name: str, value: int, value_min: int, value_max: int
    ) -> int:
        """範囲外の整数なら ``ValueError`` (TODO-027)。

        ``datetime.date()`` や ``datetime.timedelta()`` は、C の
        ``int`` に収まらない値を渡されると ``OverflowError``
        (``ValueError`` のサブクラスではない) を投げる。渡す前に
        ここで弾いて、他の範囲外と同じ ``ValueError`` に揃える。

        Parameters
        ----------
        name: str
            警告に出す名前
        value: int
        value_min: int
        value_max: int

        Returns
        -------
        int
            範囲内なら、そのまま返す

        """
        if not value_min <= value <= value_max:
            raise ValueError(
                f"{name} must be in {value_min}..{value_max}, not {value}"
            )

        return value

#
# (c) 2026 ytani01
#
"""一覧画面のリクエスト引数を読み、検証する (TODO-106)。"""

import dataclasses
import datetime
import re
from collections.abc import Callable
from typing import ClassVar, Protocol

import tornado.web

from . import handler_util
from .mylog import getLogger
from .sched_update import SchedUpdateForm
from .ytsched import normalize


class _ArgumentSource(Protocol):
    def get_argument(
        self, name: str, default: str | None = None
    ) -> str | None: ...

    def get_conf(self, name: str) -> str | None: ...

    def set_conf(self, name: str, value: str) -> None: ...


@dataclasses.dataclass(frozen=True)
class ConfArgs:
    """設定から得た一覧表示の条件。"""

    search_str: str
    filter_str: str
    todo_days_value: int
    search_n: int
    month_cal: bool


@dataclasses.dataclass(frozen=True)
class DisplayArgs:
    """クエリと設定から得た一覧表示の条件。"""

    conf: ConfArgs
    date: datetime.date
    sde_align: str
    view: str
    filter_re: re.Pattern[str] | None
    filter_neg: bool
    filter_error: bool
    search_re: re.Pattern[str] | None
    search_error: bool
    load_months: int
    auto_turn_msec: int

    @property
    def search_mode(self) -> bool:
        return self.search_re is not None

    @property
    def month_mode(self) -> bool:
        """月間表示かどうか（TODO-137）。

        検索モードが優先。検索結果は月の区切りに合わず、月間表示は
        ミニカレンダーそのものが目的なので、検索中は週間表示のまま。
        """
        return self.view == "month" and not self.search_mode


class MainBinder:
    """``MainHandler`` が受け取るフォームとクエリを束ねる。"""

    __log = getLogger(__qualname__)

    DEF_SEARCH_N = 5
    CONF_KEY_LOAD_MONTHS = "LoadMonths"
    CONF_KEY_TODO_DAYS = "ToDo_Days"
    CONF_KEY_FILTER_STR = "FilterStr"
    CONF_KEY_SEARCH_N = "SearchN"
    CONF_KEY_MONTH_CAL = "MonthCal"
    CONF_KEY_AUTO_TURN_MSEC = "AutoTurnMsec"

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
    DEF_MONTH_CAL = True
    DEF_LOAD_MONTHS = 1
    LOAD_MONTHS_MIN = 0
    LOAD_MONTHS_MAX = 24
    DEF_AUTO_TURN_MSEC = 700
    AUTO_TURN_MSEC_MIN = 300
    AUTO_TURN_MSEC_MAX = 10000

    def __init__(self, source: _ArgumentSource) -> None:
        self._source = source

    def update_conf_args(self) -> ConfArgs:
        return ConfArgs(
            search_str=self._update_conf_arg(
                "search_str",
                "SearchStr",
                "",
                empty_is_given=True,
                convert=normalize,
            ),
            filter_str=self._update_conf_arg(
                "filter_str",
                self.CONF_KEY_FILTER_STR,
                "",
                empty_is_given=True,
                convert=normalize,
            ),
            todo_days_value=self._update_conf_arg(
                "todo_days",
                self.CONF_KEY_TODO_DAYS,
                self.DEF_TODO_DAYS,
                empty_is_given=False,
                convert=self._str2todo_days,
            ),
            search_n=self._update_conf_arg(
                "search_n",
                self.CONF_KEY_SEARCH_N,
                self.DEF_SEARCH_N,
                empty_is_given=True,
                convert=int,
            ),
            month_cal=self._update_conf_arg(
                "month_cal",
                self.CONF_KEY_MONTH_CAL,
                self.DEF_MONTH_CAL,
                empty_is_given=False,
                convert=handler_util.str2month_cal,
            ),
        )

    def get_display_args(self) -> DisplayArgs:
        """表示に必要な引数をすべて読み、検証する。"""
        conf = self.update_conf_args()
        filter_re, filter_neg, filter_error = self._compile_filter(
            conf.filter_str
        )
        search_re, search_error = self._compile_search(conf.search_str)
        return DisplayArgs(
            conf=conf,
            date=self.get_date(None),
            sde_align=self.get_sde_align(),
            view=self.get_view(),
            filter_re=filter_re,
            filter_neg=filter_neg,
            filter_error=filter_error,
            search_re=search_re,
            search_error=search_error,
            load_months=self._get_conf_int(
                self.CONF_KEY_LOAD_MONTHS,
                self.DEF_LOAD_MONTHS,
                self.LOAD_MONTHS_MIN,
                self.LOAD_MONTHS_MAX,
            ),
            auto_turn_msec=self._get_conf_int(
                self.CONF_KEY_AUTO_TURN_MSEC,
                self.DEF_AUTO_TURN_MSEC,
                self.AUTO_TURN_MSEC_MIN,
                self.AUTO_TURN_MSEC_MAX,
            ),
        )

    def get_update_form(self, cmd: str) -> SchedUpdateForm:
        """更新フォームを読み、書き込み前に日付と時刻を検証する。"""
        orig_date = self._get_date_arg("orig_date")
        date = self._get_date_arg("date")
        time_start = self._get_time_arg("time_start")
        time_end = self._get_time_arg("time_end")
        deadline_date_str = self._argument("deadline_date", "") or ""
        deadline_time_start_str = (
            self._argument("deadline_time_start", "") or ""
        )
        deadline_time_end_str = self._argument("deadline_time_end", "") or ""
        if deadline_time_end_str:
            deadline_time_end_str = "-" + deadline_time_end_str
        return SchedUpdateForm(
            cmd=cmd,
            sde_id=self._argument("sde_id"),
            orig_date=orig_date,
            date=date,
            time_start=time_start,
            time_end=time_end,
            sde_type=self._argument("sde_type", "") or "",
            title=self._argument("title", "") or "",
            place=self._argument("place", "") or "",
            detail=self._argument("detail", "") or "",
            deadline_date_str=deadline_date_str,
            deadline_time_start_str=deadline_time_start_str,
            deadline_time_end_str=deadline_time_end_str,
        )

    def get_date(self, modified_date: datetime.date | None) -> datetime.date:
        cur_day = datetime.date.today()
        cur_day_str = self._argument("cur_day")
        if cur_day_str:
            parsed = handler_util.convert_value(
                "cur_day", cur_day_str, handler_util.str2date
            )
            if parsed is not None:
                cur_day = parsed
        date = None
        date_str = self._argument("date")
        if date_str:
            date = handler_util.convert_value(
                "date", date_str, handler_util.str2date
            )
        return modified_date or date or cur_day

    def get_sde_align(self) -> str:
        return self._argument("sde_align") or "top"

    def get_view(self) -> str:
        """``view`` クエリを読む（TODO-137）。

        ``conf.json`` には保存しない。``"month"`` 以外はすべて
        ``"week"`` として扱い、不正な値でもエラーにしない。
        """
        if self._argument("view") == "month":
            return "month"
        return "week"

    def _argument(self, name: str, default: str | None = None) -> str | None:
        return self._source.get_argument(name, default)

    def _str2todo_days(self, value: str) -> int:
        return handler_util.check_int_range(
            "todo_days",
            int(value),
            min(self.TODO_DAYS.values()),
            max(self.TODO_DAYS.values()),
        )

    def _get_conf_int(
        self, key: str, default: int, min_value: int, max_value: int
    ) -> int:
        value = self._source.get_conf(key)
        if value is None:
            return default
        converted = handler_util.convert_value(
            key,
            value,
            lambda v: handler_util.check_int_range(
                key, int(v), min_value, max_value
            ),
        )
        return default if converted is None else converted

    def _update_conf_arg[T](
        self,
        arg_name: str,
        conf_key: str,
        default: T,
        *,
        empty_is_given: bool,
        convert: Callable[[str], T],
    ) -> T:
        conf_value = self._source.get_conf(conf_key)
        value = self._argument(arg_name)
        if value is not None and (empty_is_given or value):
            converted = handler_util.convert_value(arg_name, value, convert)
            if converted is not None:
                save_value = (
                    converted if isinstance(converted, str) else value
                )
                if save_value != conf_value:
                    self._source.set_conf(conf_key, save_value)
                return converted
        if conf_value:
            converted = handler_util.convert_value(
                conf_key, conf_value, convert
            )
            if converted is not None:
                return converted
        return default

    def _compile_filter(
        self, value: str
    ) -> tuple[re.Pattern[str] | None, bool, bool]:
        negative = value.startswith("!")
        compiled = self._compile_re(value[1:] if negative else value)
        return compiled, negative, compiled is None

    def _compile_search(
        self, value: str
    ) -> tuple[re.Pattern[str] | None, bool]:
        compiled = self._compile_re(value) if value else None
        return compiled, bool(value) and compiled is None

    def _compile_re(self, pattern: str) -> re.Pattern[str] | None:
        try:
            return re.compile(pattern)
        except re.error as ex:
            self.__log.warning(f"{type(ex).__name__}:{ex}:{pattern!a}")
            return None

    def _get_date_arg(self, arg_name: str) -> datetime.date | None:
        value = self._argument(arg_name)
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

    def _get_time_arg(self, arg_name: str) -> datetime.time | None:
        value = self._argument(arg_name)
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

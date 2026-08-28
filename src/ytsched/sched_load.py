#
# (c) 2026 ytani01
#
"""
SchedLoader
"""

__author__ = "ytani01"
__date__ = "2026/08"

import dataclasses
import datetime
import re

from . import handler_util
from .mylog import getLogger
from .ytsched import SchedData, SchedDataEnt


def filter_match(
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


@dataclasses.dataclass
class SchedLoadCond:
    """一覧を組み立てるときの条件 (TODO-079・TODO-088)。

    ``MainHandler.get()`` は前後の週の数だけ ``load_week()`` を
    繰り返し呼ぶ (TODO-069) が、``date`` 以外の引数は毎回同じ値になる。
    ここへまとめて 1 つの引数にする。``todo_by_date``
    (``mk_todo_by_date()`` の結果) も持たせ、週ごとに作り直さず
    1 回だけ集計する。

    検索だけが使う ``search_re``/``search_n`` は ``SchedSearchCond``
    の持ち物 (TODO-088)。
    """

    filter_re: re.Pattern[str] | None
    filter_neg: bool
    todo_days_value: int
    todo_today_sde: list[SchedDataEnt]
    todo_by_date: dict[datetime.date, list[SchedDataEnt]]


@dataclasses.dataclass
class SchedSearchCond:
    """検索だけが使う条件 (TODO-088)。"""

    search_re: re.Pattern[str]
    search_n: int


@dataclasses.dataclass
class SchedDay:
    """``sched`` の 1 要素 (TODO-091)。

    ``load_week()``/``search()`` が返す ``sched`` の各日。
    """

    date: datetime.date
    is_holiday: bool
    sde: list[SchedDataEnt]


@dataclasses.dataclass
class SchedWeek:
    """``weeks`` の 1 要素 (TODO-091)。

    ``MainHandler.mk_weeks()`` が前後の週も含めて組み立てる。
    """

    offset: int
    monday: datetime.date
    sched: list[SchedDay]


class SchedLoader:
    """スケジュールを読み集める (TODO-088)。"""

    __log = getLogger(__qualname__)

    #: 1 件でも当たったら、ここまで戻って検索を打ち切る日数
    SEARCH_ENOUGH_DAYS = 365

    def __init__(self, sd: SchedData) -> None:
        """Constructor

        Parameters
        ----------
        sd: SchedData

        """
        self._sd = sd

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
            if not filter_match(filter_re, filter_neg, sde):
                continue

            if not search_match(search_re, sde):
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
        todo_days_value: int,
        todo_sde: list[SchedDataEnt],
    ) -> dict[datetime.date, list[SchedDataEnt]]:
        """ToDo を期限の日付で引けるようにする (TODO-028)。

        ``load_week()``/``search()`` は 1 日ずつさかのぼるので、日ごとに
        ``todo_sde`` を全件見ると、日数 × 件数だけ照合が走る。
        先に日付でまとめておけば 1 回で済む。並び順は ``todo_sde`` の
        まま。``get()`` が ``SchedLoadCond`` を作るところで 1 回だけ
        呼び、週の数だけ繰り返し呼ばないようにしている (TODO-079)。

        ``todo_sde`` は ``load_todo()`` が ``search_re`` で絞ったあとの
        ものなので、ここで検索の照合はしない (TODO-094)。

        ``todo_days_value`` が負のときは ToDo を混ぜないので、空の
        ``dict`` を返す。

        Parameters
        ----------
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
            by_date.setdefault(sde.date, []).append(sde)

        return by_date

    def _load_day(
        self,
        date1: datetime.date,
        cond: SchedLoadCond,
        search_re: re.Pattern[str] | None = None,
        extra_sde: list[SchedDataEnt] | None = None,
    ) -> tuple[SchedDay, int]:
        """1 日ぶんのスケジュールを集める (TODO-088)。

        ``load_week()``・``search()`` の共通部分。``search_re`` は
        検索のときだけ渡す (``load_week()`` は渡さないので、常に
        ``search_match()`` を通っても絞り込まれない)。``extra_sde`` は
        ``load_week()`` が今日の欄にだけ足す ``todo_today_sde`` 用。

        Parameters
        ----------
        date1: datetime.date
        cond: SchedLoadCond
        search_re: re.Pattern[str] | None
        extra_sde: list[SchedDataEnt] | None

        Returns
        -------
        day: SchedDay
            ``sched`` の 1 要素
        hit_count: int
            その日にファイルから当たった件数 (ToDo は数えない。
            検索の打ち切りに使う)

        """
        # ファイルが無い日は開きに行かない (TODO-028)
        sdf = None
        if self._sd.sdf_exists(date1):
            sdf = self._sd.get_sdf(date1)

        out_sde = []
        hit_count = 0
        for sde in sdf.sde if sdf else []:
            if not filter_match(cond.filter_re, cond.filter_neg, sde):
                continue

            if not search_match(search_re, sde):
                continue

            out_sde.append(sde)
            hit_count += 1

        if cond.todo_days_value >= 0:
            out_sde.extend(cond.todo_by_date.get(date1, []))

            if extra_sde:
                out_sde.extend(extra_sde)

        out_sde = sorted(out_sde, key=lambda x: x.get_sortkey())

        day = SchedDay(
            date=date1,
            is_holiday=sdf.is_holiday if sdf else False,
            sde=out_sde,
        )
        return day, hit_count

    def load_week(
        self,
        date: datetime.date,
        cond: SchedLoadCond,
    ) -> tuple[list[SchedDay], datetime.date, datetime.date]:
        """``date`` を含む週 (月曜〜日曜) のスケジュールを集める。

        Parameters
        ----------
        date: datetime.date
        cond: SchedLoadCond
            表示の条件 (TODO-079)。``get()`` が前後の週の数だけ
            呼び出すあいだ、``date`` 以外は同じ値になる

        Returns
        -------
        sched: list[SchedDay]
            日付の昇順。1 件も当たらない日も落とさない
        date_from: datetime.date
            ``date`` を含む週の月曜 (TODO-049)
        date_to: datetime.date
            ``date_from`` の 6 日後 (日曜)

        """
        monday = date - datetime.timedelta(date.weekday())
        date_from = monday
        date_to = monday + datetime.timedelta(6)
        today = datetime.date.today()

        sched = []
        date1 = date_from
        while date1 <= date_to:
            extra_sde = cond.todo_today_sde if date1 == today else None
            day, _hit_count = self._load_day(date1, cond, extra_sde=extra_sde)
            sched.append(day)
            date1 += datetime.timedelta(1)

        return sched, date_from, date_to

    def search(
        self,
        date: datetime.date,
        cond: SchedLoadCond,
        search_cond: SchedSearchCond,
    ) -> tuple[list[SchedDay], datetime.date, datetime.date]:
        """``date`` から過去へさかのぼって検索結果を集める。

        Parameters
        ----------
        date: datetime.date
        cond: SchedLoadCond
        search_cond: SchedSearchCond

        Returns
        -------
        sched: list[SchedDay]
            日付の昇順。1 件も当たらなかった日は並べない
            (ToDo だけの日は並べる)
        date_from: datetime.date
            打ち切った日 (最大でも ``SEARCH_HARD_LIMIT_DAYS``(1825) 日前)
        date_to: datetime.date
            ``date``

        Notes
        -----
        最大 ``SEARCH_HARD_LIMIT_DAYS``(1825) 日をさかのぼるので、
        **データファイルが無い日は開きに行かない** (TODO-028)。
        開いても中身が空の ``SchedDataFile`` になるだけで、``sched`` の
        中身も打ち切りの数え方も変わらない。

        """
        date_to = date
        date_from = date - datetime.timedelta(
            handler_util.SEARCH_HARD_LIMIT_DAYS
        )
        date_from1 = date - datetime.timedelta(self.SEARCH_ENOUGH_DAYS)

        sched = []
        search_count = 0
        date1 = date_to + datetime.timedelta(1)
        while date1 > date_from:
            if search_count > 0:
                if search_count >= search_cond.search_n:
                    date_from = date1
                    break

                if date1 <= date_from1:
                    date_from = date1
                    break

            date1 -= datetime.timedelta(1)

            day, hit_count = self._load_day(
                date1, cond, search_re=search_cond.search_re
            )
            search_count += hit_count

            if not day.sde:
                continue

            sched.append(day)

        return sched[::-1], date_from, date_to

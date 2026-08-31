#
# (c) 2026 ytani01
#
"""
SchedLoader
"""

__author__ = "ytani01"
__date__ = "2026/08"

import calendar
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
class MonthCalDay:
    """月間ミニカレンダーの 1 日 (TODO-103)。

    ``load_month_cal()`` が組み立てる ``MonthCal.weeks`` の 1 要素。
    """

    date: datetime.date
    in_month: bool
    has_sched: bool
    has_important: bool
    is_holiday: bool
    has_todo: bool
    has_todo_important: bool


@dataclasses.dataclass
class MonthCal:
    """月間ミニカレンダー 1 か月分 (TODO-103)。

    ``weeks`` は月曜始まりで 7 個ずつ (前後の月の埋めセルを含む)。
    """

    year: int
    month: int
    weeks: list[list[MonthCalDay]]


@dataclasses.dataclass
class MonthBlock:
    """月間表示の 1 ブロック（6 ヶ月ぶん。TODO-137）。

    区切りは 1〜6月・7〜12月の 2 つだけ。``month_cals`` は
    ``start_month`` から 6 か月ぶん (``MainViewBuilder`` が組み立てる)。
    ``base_date`` は月間表示のパネルが持つ基準日（``offset`` が 0 なら
    ``args.date`` そのもの、±1 なら先頭月の 1 日。TODO-137 の設計）。
    """

    offset: int
    year: int
    start_month: int
    base_date: datetime.date
    month_cals: list[MonthCal]


@dataclasses.dataclass
class SchedWeek:
    """``weeks`` の 1 要素 (TODO-091)。

    ``MainHandler.mk_weeks()`` が前後の週も含めて組み立てる。
    ``month_cals`` は週パネルの下に出す月間ミニカレンダー 2 ヶ月分
    (検索モードでは空リスト。TODO-103)。
    """

    offset: int
    monday: datetime.date
    sched: list[SchedDay]
    month_cals: list[MonthCal]


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
        #: 月間ミニカレンダーのキャッシュ ((year, month) をキーに)。
        #: 同じ月が複数の週パネルで要るので、1 リクエスト内で使い回す
        #: (``SchedLoader`` はリクエストごとに作られる。TODO-103)
        self._month_cal_cache: dict[tuple[int, int], MonthCal] = {}
        #: ToDo の締切日の集合と、そのうち重要な ToDo の締切日の集合
        #: (``load_month_cal()`` が使う。フィルタ・検索・``todo_days``
        #: は反映しない。1 リクエスト内で 1 回だけ集める
        #: (TODO-129・TODO-132)。
        self._todo_dates: set[datetime.date] | None = None
        self._todo_important_dates: set[datetime.date] | None = None

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

    def _get_todo_dates(self) -> set[datetime.date]:
        """ToDo の締切日の集合を作る (初回だけ。TODO-129)。

        ``load_month_cal()`` がミニカレンダーの印に使う。フィルタ・
        検索・``todo_days`` は反映しない (ミニカレンダーは元からそう)。

        Returns
        -------
        set[datetime.date]

        """
        if self._todo_dates is None:
            self._build_todo_dates()
        assert self._todo_dates is not None
        return self._todo_dates

    def _get_todo_important_dates(self) -> set[datetime.date]:
        """重要な ToDo の締切日の集合を作る (初回だけ。TODO-132)。

        ``load_month_cal()`` がミニカレンダーの四角の枠色に使う。
        ``_get_todo_dates()`` と同じく ``ToDo.jsonl`` (``get_sdf(None)``)
        だけを見る (フィルタ・検索・``todo_days`` は反映しない)。

        Returns
        -------
        set[datetime.date]

        """
        if self._todo_important_dates is None:
            self._build_todo_dates()
        assert self._todo_important_dates is not None
        return self._todo_important_dates

    def _build_todo_dates(self) -> None:
        """``_todo_dates``/``_todo_important_dates`` を 1 回で組み立てる。

        ``ToDo.jsonl`` を 1 回走査するだけで両方を作る (TODO-132)。
        """
        todo_dates: set[datetime.date] = set()
        todo_important_dates: set[datetime.date] = set()
        for sde in self._sd.get_sdf(None).sde:
            todo_dates.add(sde.date)
            if sde.is_important():
                todo_important_dates.add(sde.date)
        self._todo_dates = todo_dates
        self._todo_important_dates = todo_important_dates

    def load_month_cal(self, year: int, month: int) -> MonthCal:
        """月間ミニカレンダー 1 か月分を組み立てる (TODO-103・TODO-129)。

        予定の有無・重要・祝日は ``SchedData.get_sdf(date).sde`` で
        中身を読んで判定する。``SchedData`` のキャッシュに載るので
        2 回目以降は速いが、初回はファイルを開くぶん重くなる。ToDo の
        締切と、そのうち重要なものは ``_get_todo_dates()`` /
        ``_get_todo_important_dates()`` の集合を引くだけ (TODO-132)。
        フィルタ・検索は反映しない。

        1 リクエスト内で同じ月が複数の週パネルから要求されるので、
        ``self._month_cal_cache`` に積んで使い回す。

        Parameters
        ----------
        year: int
        month: int

        Returns
        -------
        MonthCal
            ``weeks`` は月曜始まりで 7 個ずつ

        """
        key = (year, month)
        cached = self._month_cal_cache.get(key)
        if cached is not None:
            return cached

        todo_dates = self._get_todo_dates()
        todo_important_dates = self._get_todo_important_dates()

        first_day = datetime.date(year, month, 1)
        days_in_month = calendar.monthrange(year, month)[1]
        last_day = datetime.date(year, month, days_in_month)

        monday = first_day - datetime.timedelta(first_day.weekday())
        last_week_monday = last_day - datetime.timedelta(last_day.weekday())

        weeks: list[list[MonthCalDay]] = []
        date1 = monday
        while date1 <= last_week_monday:
            week: list[MonthCalDay] = []
            for _ in range(7):
                day_sde = self._sd.get_sdf(date1).sde
                sde_list = [sde for sde in day_sde if not sde.is_todo()]
                todo_sde_list = [sde for sde in day_sde if sde.is_todo()]
                # 日付ファイル側に ToDo 型の行が混ざっていても印が
                # 消えないよう、四角のほうで拾う (TODO-129 の reviewer
                # の指摘)。正常な操作では ``SchedUpdater`` が ToDo を
                # ``ToDo.jsonl`` へ書くので混ざらないが、``migrate``
                # したデータや手で直したファイルでは起こりうる。重要
                # (赤枠) も同じ経路で拾う (TODO-132)
                has_todo = date1 in todo_dates or len(day_sde) > len(sde_list)
                has_todo_important = date1 in todo_important_dates or any(
                    sde.is_important() for sde in todo_sde_list
                )
                week.append(
                    MonthCalDay(
                        date=date1,
                        in_month=(
                            date1.year == year and date1.month == month
                        ),
                        has_sched=len(sde_list) > 0,
                        has_important=any(
                            sde.is_important() for sde in sde_list
                        ),
                        is_holiday=any(sde.is_holiday() for sde in sde_list),
                        has_todo=has_todo,
                        has_todo_important=has_todo_important,
                    )
                )
                date1 += datetime.timedelta(1)
            weeks.append(week)

        month_cal = MonthCal(year=year, month=month, weeks=weeks)
        self._month_cal_cache[key] = month_cal
        return month_cal

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

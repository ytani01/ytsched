#
# (c) 2026 ytani01
#
"""一覧画面のビュー用データを組み立てる (TODO-106)。"""

import datetime
from typing import ClassVar

from .main_binder import DisplayArgs, MainBinder
from .sched_load import (
    MonthCal,
    SchedLoadCond,
    SchedLoader,
    SchedSearchCond,
    SchedWeek,
)


class MainViewBuilder:
    """``main.html`` へ渡す値を、データ読み込みを含めて組み立てる。"""

    DAYS_PER_MONTH: ClassVar[int] = 30

    def __init__(self, loader: SchedLoader) -> None:
        self._loader = loader

    def build(self, args: DisplayArgs) -> dict[str, object]:
        todo_sde, todo_today_sde = self._loader.load_todo(
            args.filter_re,
            args.filter_neg,
            args.search_re,
            args.conf.todo_days_value,
        )
        cond = SchedLoadCond(
            filter_re=args.filter_re,
            filter_neg=args.filter_neg,
            todo_days_value=args.conf.todo_days_value,
            todo_today_sde=todo_today_sde,
            todo_by_date=self._loader.mk_todo_by_date(
                args.conf.todo_days_value, todo_sde
            ),
        )
        if args.search_re is not None:
            sched, date_from, date_to = self._loader.search(
                args.date,
                cond,
                SchedSearchCond(args.search_re, args.conf.search_n),
            )
        else:
            sched, date_from, date_to = self._loader.load_week(
                args.date, cond
            )
        return {
            "today": datetime.date.today(),
            "date": args.date,
            "date_from": date_from,
            "date_to": date_to,
            "sched": sched,
            "weeks": self._mk_weeks(args, cond, sched, date_from),
            "todo_days_list": MainBinder.TODO_DAYS,
            "todo_days_value": args.conf.todo_days_value,
            "filter_str": args.conf.filter_str,
            "search_str": args.conf.search_str,
            "search_mode": args.search_mode,
            "filter_error": args.filter_error,
            "search_error": args.search_error,
            "search_n": args.conf.search_n,
            "sde_align": args.sde_align,
            "auto_turn_msec": args.auto_turn_msec,
            "month_cal": args.conf.month_cal,
        }

    @classmethod
    def months2weeks(cls, months: int) -> int:
        return round(months * cls.DAYS_PER_MONTH / 7)

    def _mk_weeks(
        self,
        args: DisplayArgs,
        cond: SchedLoadCond,
        sched,
        date_from: datetime.date,
    ) -> list[SchedWeek]:
        if args.search_mode:
            monday = args.date - datetime.timedelta(args.date.weekday())
            return [
                SchedWeek(offset=0, monday=monday, sched=sched, month_cals=[])
            ]
        weeks = []
        for offset in range(
            -self.months2weeks(args.load_months),
            self.months2weeks(args.load_months) + 1,
        ):
            monday = date_from + datetime.timedelta(7 * offset)
            sched_offset = (
                sched
                if offset == 0
                else self._loader.load_week(monday, cond)[0]
            )
            weeks.append(
                SchedWeek(
                    offset=offset,
                    monday=monday,
                    sched=sched_offset,
                    month_cals=self._mk_month_cals(monday)
                    if args.conf.month_cal
                    else [],
                )
            )
        return weeks

    def _mk_month_cals(self, monday: datetime.date) -> list[MonthCal]:
        year1, month1 = monday.year, monday.month
        year2, month2 = (
            (year1 + 1, 1) if month1 == 12 else (year1, month1 + 1)
        )
        return [
            self._loader.load_month_cal(year1, month1),
            self._loader.load_month_cal(year2, month2),
        ]

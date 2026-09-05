#
# (c) 2026 ytani01
#
"""一覧画面のビュー用データを組み立てる (TODO-106)。"""

import datetime
from typing import ClassVar

from .main_binder import DisplayArgs, MainBinder
from .sched_load import (
    MonthBlock,
    MonthCal,
    SchedLoadCond,
    SchedLoader,
    SchedSearchCond,
    SchedWeek,
)


class MainViewBuilder:
    """``main.html`` へ渡す値を、データ読み込みを含めて組み立てる。"""

    #: 1 ブロックに収める月数（TODO-137）。ブロックの区切りは
    #: 1〜6月・7〜12月の 2 つだけなので 6 固定
    MONTHS_PER_BLOCK: ClassVar[int] = 6

    def __init__(self, loader: SchedLoader) -> None:
        self._loader = loader

    def build(self, args: DisplayArgs) -> dict[str, object]:
        # テンプレートが参照する共通の値。週間・月間表示のどちらでも
        # 同じキーで揃える（TODO-137）
        common: dict[str, object] = {
            "today": datetime.date.today(),
            "date": args.date,
            # 検索モードでは、``view=month`` が来ていても週間表示に
            # 倒す (``month_mode``。TODO-137)。テンプレートも
            # JavaScript (``#main`` の ``data-view``) も、この
            # 実際に描いたモードを見る
            "view": "month" if args.month_mode else "week",
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
            "gauge_follow_msec": args.gauge_follow_msec,
            "month_cal": args.conf.month_cal,
        }

        if args.month_mode:
            # 月間表示では load_todo()/load_week() を使わない
            # (TODO-137)。load_month_cal() は _month_cal_cache が効くので
            # 何ヶ月ぶんでも月ごとに 1 回で済む
            return {
                **common,
                "date_from": args.date,
                "date_to": args.date,
                "sched": [],
                "weeks": [],
                "month_blocks": self._mk_month_blocks(args),
            }

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
            **common,
            "date_from": date_from,
            "date_to": date_to,
            "sched": sched,
            "weeks": self._mk_weeks(args, cond, sched, date_from),
            "month_blocks": [],
        }

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
        for offset in range(-args.load_week_pages, args.load_week_pages + 1):
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

    def _mk_month_blocks(self, args: DisplayArgs) -> list[MonthBlock]:
        """月間表示のブロックを組み立てる（前後を先読み。TODO-137）。

        ブロック数は ``load_month_pages``（``n``）で決まり、前後 ``n``
        個ずつ ＝ ``2n + 1`` 個（TODO-166）。ブロックの区切りは
        1〜6月・7〜12月の 2 つだけ。年をまたいでも ``block_index``
        (0 始まりの通し月数を 6 で割ったもの) で扱えば、月の繰り上がり・
        繰り下がりを個別に気にしなくてよい。
        """
        date = args.date
        block_index = (
            date.year * 12 + (date.month - 1)
        ) // self.MONTHS_PER_BLOCK
        blocks = []
        n = args.load_month_pages
        for offset in range(-n, n + 1):
            start_index = (block_index + offset) * self.MONTHS_PER_BLOCK
            year = start_index // 12
            start_month = start_index % 12 + 1
            base_date = (
                date if offset == 0 else datetime.date(year, start_month, 1)
            )
            month_cals = []
            for i in range(self.MONTHS_PER_BLOCK):
                idx = start_index + i
                month_cals.append(
                    self._loader.load_month_cal(idx // 12, idx % 12 + 1)
                )
            blocks.append(
                MonthBlock(
                    offset=offset,
                    year=year,
                    start_month=start_month,
                    base_date=base_date,
                    month_cals=month_cals,
                )
            )
        return blocks

    def _mk_month_cals(self, monday: datetime.date) -> list[MonthCal]:
        year1, month1 = monday.year, monday.month
        year2, month2 = (
            (year1 + 1, 1) if month1 == 12 else (year1, month1 + 1)
        )
        return [
            self._loader.load_month_cal(year1, month1),
            self._loader.load_month_cal(year2, month2),
        ]

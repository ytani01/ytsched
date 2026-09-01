#
# (c) 2026 ytani01
#
"""毎朝の通知用テキストの組み立て (TODO-153)

Slack へ送るところまではやらない。**ytsched は Slack を知らない**ので、
ここではテキストを組み立てるだけにして、標準出力へ出すのは
``ytsched notify``、Slack へ送るのは別の道具（``slack-send.sh``）に
任せる。
"""

from __future__ import annotations

import datetime

from .ytsched import SchedData, SchedDataEnt

__author__ = "ytani01"
__date__ = "2026/09"

#: ``date.weekday()`` (0=月) の並びと揃えた曜日
WEEKDAY_JA = ["月", "火", "水", "木", "金", "土", "日"]

#: 予定が無い日に出す文言
NO_SCHEDULE = "  予定なし"

#: ToDo の節の見出し
TODO_HEADER = "期限が近い ToDo"

#: 時刻欄の幅（``HH:MM-HH:MM`` が収まる幅）
TIME_FIELD_WIDTH = 11


def format_header(date: datetime.date) -> str:
    """``2026-09-02 (水)`` の形にする。"""
    weekday = WEEKDAY_JA[date.weekday()]
    return f"{date.strftime('%Y-%m-%d')} ({weekday})"


def format_schedule_line(sde: SchedDataEnt) -> str:
    """1 件の予定を、通知用の 1 行にする。

    時刻が無い予定は、時刻欄を出さずタイトルだけにする。
    """
    if sde.time_start is None and sde.time_end is None:
        return f"  {sde.title}"

    start = sde.time_start.strftime("%H:%M") if sde.time_start else ""
    end = sde.time_end.strftime("%H:%M") if sde.time_end else ""
    time_field = f"{start}-{end}".ljust(TIME_FIELD_WIDTH)

    return f"  {time_field} {sde.title}"


def format_todo_line(sde: SchedDataEnt) -> str:
    """1 件の ToDo を、通知用の 1 行にする（``MM-DD タイトル``）。"""
    return f"  {sde.date.strftime('%m-%d')} {sde.title}"


def build_schedule_section(sd: SchedData, date: datetime.date) -> list[str]:
    """その日の予定の節（日付の見出し行を含む）を組み立てる。"""
    lines = [format_header(date)]

    sdf = sd.get_sdf(date)
    sde_list = sorted(sdf.sde, key=lambda sde: sde.get_sortkey())

    if not sde_list:
        lines.append(NO_SCHEDULE)
        return lines

    for sde in sde_list:
        lines.append(format_schedule_line(sde))

    return lines


def build_todo_section(sd: SchedData, today: datetime.date) -> list[str]:
    """期限の近い ToDo の節を組み立てる（無ければ空リスト）。"""
    todo_sdf = sd.get_sdf(None)

    urgent_sde = [
        sde
        for sde in todo_sdf.sde
        if sde.is_todo() and sde.todo_urgency(today) in ("over", "near")
    ]

    if not urgent_sde:
        return []

    urgent_sde.sort(key=lambda sde: sde.get_sortkey())

    lines = [TODO_HEADER]
    for sde in urgent_sde:
        lines.append(format_todo_line(sde))

    return lines


def build_notify_text(
    sd: SchedData,
    date: datetime.date,
    include_todo: bool = True,
    days: int = 1,
    memo: str | None = None,
) -> str:
    """通知の本文を組み立てる。

    Parameters
    ----------
    sd: SchedData
    date: datetime.date
        対象の日（``days`` > 1 のときは、その日から数えた最初の日）
    include_todo: bool
        ``False`` なら ToDo の節を出さない
    days: int
        何日ぶんの予定を出すか（``date`` を含む）
    memo: str | None
        指定すると、メッセージの先頭に出す

    Returns
    -------
    str

    """
    sections = []

    if memo:
        sections.append([memo])

    for offset in range(days):
        sections.append(
            build_schedule_section(sd, date + datetime.timedelta(days=offset))
        )

    if include_todo:
        todo_lines = build_todo_section(sd, date)
        if todo_lines:
            sections.append(todo_lines)

    return "\n\n".join("\n".join(lines) for lines in sections)

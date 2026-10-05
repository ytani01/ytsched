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


def slack_escape(text: str) -> str:
    """Slack の mrkdwn で特別な意味を持つ ``&`` ``<`` ``>`` をエスケープする。"""
    return (
        text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    )


def format_header(date: datetime.date) -> str:
    """``2026-09-02 (水)`` の形にする。"""
    weekday = WEEKDAY_JA[date.weekday()]
    return f"{date.strftime('%Y-%m-%d')} ({weekday})"


def format_period_header(date: datetime.date, days: int) -> str:
    """``2026-10-05 (月) 〜 10-11 (日)`` の形にする（1 日なら日付だけ）。"""
    header = format_header(date)
    if days == 1:
        return header

    last = date + datetime.timedelta(days=days - 1)
    weekday = WEEKDAY_JA[last.weekday()]
    return f"{header} 〜 {last.strftime('%m-%d')} ({weekday})"


def format_entry(sde: SchedDataEnt) -> str:
    """``[種別] タイトル @場所`` の形にする（Web 画面の ``sde.html`` と同じ）。

    ToDo の種別は先頭の ``□`` を除いた部分で、``□`` だけなら出さない。
    タイトルが空なら ``__``、場所が空なら ``@場所`` を出さない（TODO-224）。
    """
    sde_type = sde.type[1:] if sde.is_todo() else sde.type
    text = f"[{sde_type}] " if sde_type else ""
    text += sde.title or "__"
    if sde.place:
        text += f" @{sde.place}"
    return text


def format_schedule_line(sde: SchedDataEnt) -> str:
    """1 件の予定を、通知用の 1 行にする。

    時刻が無い予定は、時刻欄を出さず本文だけにする。
    """
    if sde.time_start is None and sde.time_end is None:
        return f"  {format_entry(sde)}"

    start = sde.time_start.strftime("%H:%M") if sde.time_start else ""
    end = sde.time_end.strftime("%H:%M") if sde.time_end else ""
    time_field = f"{start}-{end}".ljust(TIME_FIELD_WIDTH)

    return f"  {time_field} {format_entry(sde)}"


def format_todo_line(sde: SchedDataEnt) -> str:
    """1 件の ToDo を、通知用の 1 行にする（``MM-DD [種別] タイトル @場所``）。"""
    return f"  {sde.date.strftime('%m-%d')} {format_entry(sde)}"


def format_detail_lines(sde: SchedDataEnt) -> list[str]:
    """detail を、予定の行より 1 段深く字下げした行にする（TODO-221）。"""
    return [f"    {line}" for line in sde.detail.rstrip("\n").splitlines()]


def link_header(header: str, date: datetime.date, url: str | None) -> str:
    """``url`` があれば、見出しを ``<URL?date=YYYY-MM-DD|見出し>`` にする。"""
    if url:
        return f"<{url}?date={date.isoformat()}|{header}>"
    return header


def build_schedule_section(
    sd: SchedData,
    date: datetime.date,
    url: str | None = None,
    detail: bool = False,
) -> list[str]:
    """その日の予定の節（日付の見出し行を含む）を組み立てる。

    ``url`` を渡すと Slack の mrkdwn で出す（TODO-222）。日付の見出しを
    ``<URL?date=YYYY-MM-DD|見出し>`` のリンクにし、予定の行は時刻の桁が
    揃うよう `` ` `` で囲む。``detail`` なら予定の行の下に detail を出す。
    """
    lines = [link_header(format_header(date), date, url)]

    sdf = sd.get_sdf(date)
    sde_list = sorted(sdf.sde, key=lambda sde: sde.get_sortkey())

    if not sde_list:
        lines.append(NO_SCHEDULE)
        return lines

    for sde in sde_list:
        line = format_schedule_line(sde)
        if url:
            # タイトル中の ` はインラインコードを途中で切るので ' にする
            line = f"  `{slack_escape(line[2:]).replace('`', "'")}`"
        lines.append(line)

        if detail:
            for detail_line in format_detail_lines(sde):
                if url:
                    # 対にならない ` が次の予定の行のコードを崩さないよう ' にする
                    detail_line = slack_escape(detail_line).replace("`", "'")
                lines.append(detail_line)

    return lines


def build_todo_section(
    sd: SchedData, today: datetime.date, url: str | None = None
) -> list[str]:
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
        line = format_todo_line(sde)
        lines.append(slack_escape(line) if url else line)

    return lines


def build_notify_text(
    sd: SchedData,
    date: datetime.date,
    include_todo: bool = True,
    days: int = 1,
    memo: str | None = None,
    url: str | None = None,
    skip_empty: bool = False,
    detail: bool = False,
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
    url: str | None
        Web 画面の URL。指定すると Slack の mrkdwn で出し、日付を
        その日の画面へのリンクにする（TODO-222）
    skip_empty: bool
        ``True`` なら予定の無い日を出さない。全部の日に予定が無ければ、
        期間の見出しの下に「予定なし」を 1 行出す（TODO-221）
    detail: bool
        ``True`` なら予定の行の下に detail を出す（TODO-221）

    Returns
    -------
    str

    """
    sections = []

    if memo:
        sections.append([slack_escape(memo) if url else memo])

    day_sections = []
    for offset in range(days):
        day = date + datetime.timedelta(days=offset)
        if skip_empty and not sd.get_sdf(day).sde:
            continue
        day_sections.append(
            build_schedule_section(sd, day, url=url, detail=detail)
        )

    if not day_sections:
        day_sections.append(
            [
                link_header(format_period_header(date, days), date, url),
                NO_SCHEDULE,
            ]
        )
    sections.extend(day_sections)

    if include_todo:
        todo_lines = build_todo_section(sd, date, url=url)
        if todo_lines:
            sections.append(todo_lines)

    return "\n\n".join("\n".join(lines) for lines in sections)

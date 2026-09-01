#
# (c) 2026 ytani01
#
"""``notify.py`` のテスト(TODO-153)"""

import datetime

from ytsched.notify import build_notify_text
from ytsched.ytsched import SchedData, SchedDataEnt


def test_no_schedule_no_todo(tmp_path):
    """予定も期限の近い ToDo も無ければ、日付行と「予定なし」だけ。"""
    sd = SchedData(str(tmp_path))
    date = datetime.date(2026, 9, 2)

    text = build_notify_text(sd, date)

    assert text == "2026-09-02 (水)\n  予定なし"


def test_schedule_and_todo(tmp_path):
    """予定と期限の近い ToDo が両方あるときの整形。"""
    sd = SchedData(str(tmp_path))
    date = datetime.date(2026, 9, 2)

    sd.add_sde(
        date,
        SchedDataEnt(
            date=date,
            time_start=datetime.time(10, 0),
            time_end=datetime.time(11, 0),
            title="打ち合わせ",
        ),
    )
    sd.add_sde(
        date,
        SchedDataEnt(
            date=date,
            time_start=datetime.time(14, 0),
            title="買い物",
        ),
    )
    sd.add_sde(
        None,
        SchedDataEnt(
            date=datetime.date(2026, 9, 5),
            sde_type="□",
            title="請求書を出す",
        ),
    )
    sd.save()

    text = build_notify_text(sd, date)

    assert text == (
        "2026-09-02 (水)\n"
        "  10:00-11:00 打ち合わせ\n"
        "  14:00-      買い物\n"
        "\n"
        "期限が近い ToDo\n"
        "  09-05 請求書を出す"
    )


def test_todo_far_away_is_excluded(tmp_path):
    """期限が 7 日より先の ToDo は出さない。"""
    sd = SchedData(str(tmp_path))
    date = datetime.date(2026, 9, 2)

    sd.add_sde(
        None,
        SchedDataEnt(
            date=datetime.date(2026, 12, 31),
            sde_type="□",
            title="遠い先",
        ),
    )
    sd.save()

    text = build_notify_text(sd, date)

    assert "遠い先" not in text
    assert "期限が近い ToDo" not in text


def test_todo_overdue_is_included(tmp_path):
    """期限を過ぎた ToDo も出す。"""
    sd = SchedData(str(tmp_path))
    date = datetime.date(2026, 9, 2)

    sd.add_sde(
        None,
        SchedDataEnt(
            date=datetime.date(2026, 8, 20),
            sde_type="□",
            title="遅れている",
        ),
    )
    sd.save()

    text = build_notify_text(sd, date)

    assert "遅れている" in text


def test_no_todo_flag_hides_todo_section(tmp_path):
    """``include_todo=False`` なら、期限が近くても出さない。"""
    sd = SchedData(str(tmp_path))
    date = datetime.date(2026, 9, 2)

    sd.add_sde(
        None,
        SchedDataEnt(
            date=datetime.date(2026, 9, 5),
            sde_type="□",
            title="請求書を出す",
        ),
    )
    sd.save()

    text = build_notify_text(sd, date, include_todo=False)

    assert text == "2026-09-02 (水)\n  予定なし"


def test_schedule_entry_without_time():
    """時刻の無い予定は、時刻欄を出さずタイトルだけ。"""
    from ytsched.notify import format_schedule_line

    sde = SchedDataEnt(title="終日の予定")
    assert format_schedule_line(sde) == "  終日の予定"

#
# (c) 2026 ytani01
#
"""``holiday.py`` のテスト(TODO-126)

取得(``fetch()``)はネットに出るので呼ばない。``tests/data/`` に置いた
CSV の抜粋(``syukujitsu-sample.csv``)を ``parse()`` に読ませる。
"""

import datetime
import pathlib

from ytsched.holiday import HolidayRegistrar, parse
from ytsched.ytsched import SchedData, SchedDataEnt

DATA_DIR = pathlib.Path(__file__).parent / "data"
SAMPLE_CSV = DATA_DIR / "syukujitsu-sample.csv"


def test_parse_decodes_cp932():
    """CP932 のデコード(``憲法記念日`` などが読める)。"""
    data = SAMPLE_CSV.read_bytes()
    holidays = parse(data)

    titles = [title for _date, title in holidays]
    assert "憲法記念日" in titles


def test_parse_dates():
    """``YYYY/M/D`` の解析。"""
    data = SAMPLE_CSV.read_bytes()
    holidays = parse(data)

    assert (datetime.date(2026, 1, 1), "元日") in holidays
    assert (datetime.date(1955, 1, 1), "元日") in holidays


def test_register_filters_by_year(tmp_path):
    """指定年での絞り込み(2026 を指定したら 2026 の 3 件だけ)。"""
    app = HolidayRegistrar(str(tmp_path), [2026], url="unused")

    data = SAMPLE_CSV.read_bytes()
    holidays = parse(data)

    sched = SchedData(str(tmp_path))
    app.register(sched, holidays)
    sched.save()

    assert app.stat.added == 3
    assert app.stat.skipped == 0
    assert app.stat.no_data_years == []


def test_register_no_data_year_is_skipped(tmp_path):
    """CSV に無い年(例: 2030)を指定したら、飛ばして他は続く。"""
    app = HolidayRegistrar(str(tmp_path), [2026, 2030], url="unused")

    data = SAMPLE_CSV.read_bytes()
    holidays = parse(data)

    sched = SchedData(str(tmp_path))
    app.register(sched, holidays)
    sched.save()

    assert app.stat.added == 3
    assert app.stat.no_data_years == [2030]


def test_register_skips_duplicate_same_title(tmp_path):
    """重なりの判定(同じ日付・同じ title は飛ばす。違えば足す)。"""
    sched = SchedData(str(tmp_path))
    sched.add_sde(
        datetime.date(2026, 1, 1),
        SchedDataEnt(
            date=datetime.date(2026, 1, 1), sde_type="休日", title="元日"
        ),
    )
    sched.save()

    app = HolidayRegistrar(str(tmp_path), [2026], url="unused")
    data = SAMPLE_CSV.read_bytes()
    holidays = parse(data)

    sched2 = SchedData(str(tmp_path))
    app.register(sched2, holidays)
    sched2.save()

    # 元日(重複)は飛ばし、憲法記念日・休日(5/6)は足す
    assert app.stat.added == 2
    assert app.stat.skipped == 1


def test_register_adds_when_title_differs(tmp_path):
    """``title`` が違えば別の予定として足す。"""
    sched = SchedData(str(tmp_path))
    sched.add_sde(
        datetime.date(2026, 1, 1),
        SchedDataEnt(
            date=datetime.date(2026, 1, 1), sde_type="休日", title="元旦"
        ),
    )
    sched.save()

    app = HolidayRegistrar(str(tmp_path), [2026], url="unused")
    data = SAMPLE_CSV.read_bytes()
    holidays = parse(data)

    sched2 = SchedData(str(tmp_path))
    app.register(sched2, holidays)
    sched2.save()

    assert app.stat.added == 3
    assert app.stat.skipped == 0


def test_dry_run_does_not_write(tmp_path):
    """``--dry-run`` でファイルが増えない。"""
    app = HolidayRegistrar(str(tmp_path), [2026], dry_run=True, url="unused")

    data = SAMPLE_CSV.read_bytes()
    holidays = parse(data)

    sched = SchedData(str(tmp_path))
    app.register(sched, holidays)
    if not app.dry_run:
        sched.save()

    assert app.stat.added == 3
    assert not any(tmp_path.rglob("*.jsonl"))

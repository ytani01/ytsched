#
# (c) 2026 ytani01
#
"""``handler_util.py``（引数と設定値の変換・検証）のテスト（TODO-081）

``self`` を使わない純粋な関数になったので、ハンドラを組み立てずに
直接呼んで確かめる。挙動そのものは ``HandlerBase`` にあったころと
変わらない（TODO-027）。
"""

import datetime

import pytest

from ytsched import handler_util


def test_convert_value_ok():
    assert handler_util.convert_value("n", "3", int) == 3


def test_convert_value_invalid_returns_none():
    """変換できない値は、例外にせず ``None``（TODO-027）。"""
    assert handler_util.convert_value("n", "abc", int) is None


def test_date_range_margin_is_search_hard_limit_days():
    date_min, date_max = handler_util.date_range()

    margin = datetime.timedelta(handler_util.SEARCH_HARD_LIMIT_DAYS)
    assert date_min == datetime.date.min + margin
    assert date_max == datetime.date.max - margin


def test_check_date_in_range():
    date_min, _ = handler_util.date_range()
    assert handler_util.check_date(date_min) == date_min


def test_check_date_out_of_range_raises():
    date_min, _ = handler_util.date_range()

    with pytest.raises(ValueError):
        handler_util.check_date(date_min - datetime.timedelta(1))


def test_str2date_ok():
    assert handler_util.str2date("2021-03-01") == datetime.date(2021, 3, 1)


def test_str2date_not_a_date_raises():
    with pytest.raises(ValueError):
        handler_util.str2date("not-a-date")


def test_str2date_out_of_usable_range_raises():
    date_min, _ = handler_util.date_range()

    with pytest.raises(ValueError):
        handler_util.str2date((date_min - datetime.timedelta(1)).isoformat())


def test_check_int_range_in_range():
    assert handler_util.check_int_range("n", 5, 0, 10) == 5


def test_check_int_range_out_of_range_raises():
    with pytest.raises(ValueError):
        handler_util.check_int_range("n", 11, 0, 10)

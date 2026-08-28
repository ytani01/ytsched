#
# (c) 2026 ytani01
#
"""
引数と設定値の変換・検証 (TODO-081)

``HandlerBase`` から出した、``self`` を使わない純粋な関数をまとめる。
``RequestHandler`` を継承していることと関係が無いので、ハンドラを
組み立てずにテストできる (TODO-027)。
"""

__author__ = "ytani01"
__date__ = "2026/08"

import datetime
from collections.abc import Callable

from .mylog import getLogger

_log = getLogger(__name__)

# 検索モードで遡る最大の日数。``date_range()`` が使う (TODO-027)
SEARCH_HARD_LIMIT_DAYS = 365 * 5


def convert_value[T](
    name: str, value: str, convert: Callable[[str], T]
) -> T | None:
    """文字列を ``convert`` で変換する (TODO-027)。

    変換できない値は ``None`` を返して、警告を 1 行出す。
    不正な正規表現の扱い (TODO-012) と揃えて、例外にはしない。

    ``convert`` には、**変換したあとに使える範囲かどうかまで見る**
    関数を渡す (``str2date()``/``str2todo_days()`` など)。範囲を
    見ないまま ``datetime.date()`` や ``datetime.timedelta()`` へ
    渡すと、``ValueError`` ではなく ``OverflowError`` になって、
    ここでは拾えない。

    Parameters
    ----------
    name: str
        警告に出す名前 (引数名か ``conf.json`` のキー)
    value: str
    convert: Callable[[str], T]
        ``int`` や ``str2date()`` など

    Returns
    -------
    T | None
        変換できなければ ``None``

    """
    try:
        return convert(value)
    except ValueError as ex:
        _log.warning(f"{name}={value!a}: {ex} .. ignored")
        return None


def date_range() -> tuple[datetime.date, datetime.date]:
    """表示に使える日付の範囲 (TODO-027)。

    ``load_sched()`` は、指定された日付から前後へ日をずらしながら
    スケジュールを集める。ずらす幅は最大で ``SEARCH_HARD_LIMIT_DAYS``
    日。``datetime.date.min``/``datetime.date.max`` ぎりぎりの日付を
    受け取ると、この足し引きが ``OverflowError`` になるので、
    ずらす幅のぶんだけ内側を「使える範囲」とする。

    Returns
    -------
    tuple[datetime.date, datetime.date]
        使える日付の、最小と最大

    """
    margin = datetime.timedelta(SEARCH_HARD_LIMIT_DAYS)
    return datetime.date.min + margin, datetime.date.max - margin


def check_date(date: datetime.date) -> datetime.date:
    """``date_range()`` の外なら ``ValueError`` (TODO-027)。

    Parameters
    ----------
    date: datetime.date

    Returns
    -------
    datetime.date
        範囲内なら、そのまま返す

    """
    date_min, date_max = date_range()

    if not date_min <= date <= date_max:
        raise ValueError(
            f"date must be in {date_min}..{date_max}, not {date}"
        )

    return date


def str2date(value: str) -> datetime.date:
    """ISO 8601 の文字列を、表示に使える日付にする (TODO-027)。

    ``convert_value()`` に渡す変換関数。日付として読めない値も、
    使える範囲の外の日付も ``ValueError``。

    Parameters
    ----------
    value: str

    Returns
    -------
    datetime.date

    """
    return check_date(datetime.date.fromisoformat(value))


def str2month_cal(value: str) -> bool:
    """``"1"``/``"0"`` を、月間ミニカレンダーを出すかどうかにする
    (TODO-104)。

    ``convert_value()`` に渡す変換関数。``conf.json`` の ``MonthCal``
    と、画面のスイッチの引数 ``month_cal`` の両方に使う。それ以外の
    値は ``ValueError``（``conf.json`` へ保存させないため）。

    Parameters
    ----------
    value: str

    Returns
    -------
    bool

    """
    if value == "1":
        return True
    if value == "0":
        return False

    raise ValueError(f"month_cal must be '0' or '1', not {value!r}")


def check_int_range(
    name: str, value: int, value_min: int, value_max: int
) -> int:
    """範囲外の整数なら ``ValueError`` (TODO-027)。

    ``datetime.date()`` や ``datetime.timedelta()`` は、C の
    ``int`` に収まらない値を渡されると ``OverflowError``
    (``ValueError`` のサブクラスではない) を投げる。渡す前に
    ここで弾いて、他の範囲外と同じ ``ValueError`` に揃える。

    Parameters
    ----------
    name: str
        警告に出す名前
    value: int
    value_min: int
    value_max: int

    Returns
    -------
    int
        範囲内なら、そのまま返す

    """
    if not value_min <= value <= value_max:
        raise ValueError(
            f"{name} must be in {value_min}..{value_max}, not {value}"
        )

    return value

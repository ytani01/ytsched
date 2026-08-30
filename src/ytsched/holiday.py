#
# (c) 2026 ytani01
#
"""日本の祝日を内閣府の CSV から取得して登録する (TODO-126)

取得と解析、登録をそれぞれ関数・クラスに分ける書き方は ``migrate.py``
に揃える。

取得元: ``https://www8.cao.go.jp/chosei/shukujitsu/syukujitsu.csv``

CSV は CP932・CRLF・``YYYY/M/D,名称`` の 2 列で、1 行目は見出し。
範囲は 1955 年から翌年分まで。指定した年が CSV に無ければ、その年は
警告を出して飛ばす。
"""

from __future__ import annotations

import csv
import dataclasses
import datetime
import io
import urllib.request

from .mylog import getLogger
from .ytsched import SchedData, SchedDataEnt

__author__ = "ytani01"
__date__ = "2026/08"

_log = getLogger(__name__)

#: 取得元の URL(既定)
DEF_URL = "https://www8.cao.go.jp/chosei/shukujitsu/syukujitsu.csv"

#: CSV のエンコーディング
ENCODING = "cp932"


def fetch(url: str) -> bytes:
    """URL から CSV を取得する(bytes のまま返す)。

    Parameters
    ----------
    url: str

    Returns
    -------
    bytes

    """
    with urllib.request.urlopen(url) as res:
        return res.read()


def parse(data: bytes) -> list[tuple[datetime.date, str]]:
    """CSV(bytes)を解析して ``(日付, 名称)`` のリストにする。

    CP932 でデコードし、CRLF・1 行目の見出しを踏まえて ``csv`` モジュールで
    読む。**壊れた行は警告を出して飛ばし、例外にしない**
    (``migrate.py`` の方針と揃える)。

    Parameters
    ----------
    data: bytes

    Returns
    -------
    list[tuple[datetime.date, str]]

    """
    text = data.decode(ENCODING, errors="replace")

    result: list[tuple[datetime.date, str]] = []
    reader = csv.reader(io.StringIO(text))
    for i, row in enumerate(reader, start=1):
        if i == 1:
            # 1 行目は見出し
            continue

        if len(row) < 2:
            _log.warning(f"line {i}: {row!r}: invalid .. skipped")
            continue

        date_str, title = row[0].strip(), row[1].strip()

        try:
            year, month, day = (int(f) for f in date_str.split("/"))
            date = datetime.date(year, month, day)
        except ValueError:
            _log.warning(f"line {i}: date={date_str!r}: invalid .. skipped")
            continue

        result.append((date, title))

    return result


@dataclasses.dataclass
class HolidayStat:
    """登録の結果"""

    added: int = 0
    """足した件数"""

    skipped: int = 0
    """重なっていて飛ばした件数"""

    no_data_years: list[int] = dataclasses.field(default_factory=list)
    """CSV に無かった年"""


class HolidayRegistrar:
    """祝日を ``SchedData`` へ登録する"""

    __log = getLogger(__qualname__)

    TYPE_HOLIDAY = "休日"

    def __init__(
        self,
        topdir: str,
        years: list[int],
        dry_run: bool = False,
        url: str = DEF_URL,
    ):
        """Constructor

        Parameters
        ----------
        topdir: str
            データディレクトリ
        years: list[int]
            登録する年
        dry_run: bool
            True なら ``save()`` を呼ばない
        url: str
            取得元の URL

        """
        self.__log.debug(
            f"topdir={topdir}, years={years}, dry_run={dry_run}, url={url}"
        )

        self.topdir = topdir
        self.years = years
        self.dry_run = dry_run
        self.url = url

        self.stat = HolidayStat()

    def is_duplicate(
        self, sched: SchedData, date: datetime.date, title: str
    ) -> bool:
        """その日に、同じ ``title`` の予定が既にあるか。"""
        sdf = sched.get_sdf(date)
        return any(sde.title == title for sde in sdf.sde)

    def register(
        self, sched: SchedData, holidays: list[tuple[datetime.date, str]]
    ) -> None:
        """解析済みの祝日を、対象の年ぶんだけ登録する。"""
        years = set(self.years)
        found_years = {date.year for date, _title in holidays}

        for year in self.years:
            if year not in found_years:
                self.__log.warning(f"{year}: no data in CSV .. skipped")
                self.stat.no_data_years.append(year)

        for date, title in holidays:
            if date.year not in years:
                continue

            if self.is_duplicate(sched, date, title):
                self.stat.skipped += 1
                continue

            sde = SchedDataEnt(
                date=date,
                sde_type=self.TYPE_HOLIDAY,
                title=title,
            )
            sched.add_sde(date, sde)
            self.stat.added += 1

    def main(self) -> HolidayStat:
        """取得・解析・登録をまとめて行う。"""
        data = fetch(self.url)
        holidays = parse(data)

        sched = SchedData(self.topdir)
        self.register(sched, holidays)

        if not self.dry_run:
            sched.save()

        if self.dry_run:
            print("===== dry run: 書き出していません =====")

        print(f"足した予定      : {self.stat.added}")
        print(f"飛ばした予定    : {self.stat.skipped}")
        if self.stat.no_data_years:
            years_str = ", ".join(str(y) for y in self.stat.no_data_years)
            print(f"データが無い年  : {years_str}")

        return self.stat

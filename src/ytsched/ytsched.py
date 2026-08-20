#
# (c) Yoichi Tanibayashi
#
"""
YTスケジューラ
"""

__author__ = "Yoichi Tanibayashi"
__date__ = "2021/01"

import collections
import datetime
import os
import re
import shutil
import uuid
from typing import ClassVar

from .mylog import getLogger


def htmlstr2text(intext: str) -> str:
    """
    Parameters
    ----------
    intext: str

    Returns
    -------
    outtext: str

    """
    resub_tbl = {
        r"&amp;#160;": " ",
        r"&gt;": ">",
        r"&lt;": "<",
        # r'&amp;': '&',
        r"&nbsp;": " ",
        r"&#160;": " ",
        r"\<BR *\/*\>": "\n",
    }

    outtext = intext
    # outtext = html2text.html2text(intext)

    outtext = outtext.replace("&nbsp;", " ")
    outtext = outtext.replace("（", "(")
    outtext = outtext.replace("）", ")")

    for k, v in resub_tbl.items():
        # outtext = outtext.replace(k, v)
        outtext = re.sub(k, v, outtext, flags=re.IGNORECASE)

    return outtext


def text2htmlstr(intext: str) -> str:
    """
    Parameters
    ----------
    intext: str
        normal text string

    Returns
    -------
    outtext: str
        HTML text
    """
    outtext = intext.rstrip("\n")

    #    outtext = outtext.replace('&', '&amp;')
    #    outtext = outtext.replace('>', '&gt;')
    #    outtext = outtext.replace('<', '&lt;')
    #    outtext = outtext.replace(' ', '&nbsp;')

    outtext = outtext.replace("\t", " ")
    outtext = outtext.replace("\r", "")
    outtext = outtext.replace("\n", "<br />")
    return outtext


class SchedDataEnt:
    """
    スケジュール・データ・エンティティ
    """

    __log = getLogger(__qualname__)

    TIME_NULL = ":-:"
    TITLE_NULL = ""

    TYPE_PREFIX_TODO = "□"
    TYPE_HOLYDAY: ClassVar[list[str]] = ["休日", "祝日"]

    TITLE_PREFIX_IMPORTANT: ClassVar[list[str]] = [
        "(重要)",
        "!",
        "！",
        "★",
        "☆",
    ]
    TITLE_PREFIX_CANCELED: ClassVar[list[str]] = [
        "(キャンセル",
        "(欠",
        "(中止",
        "(休",
        "(無効",
        "(不要",
        "x",
    ]

    def __init__(
        self,
        sde_id: str | None = None,
        date: datetime.date | None = None,
        time_start: datetime.time | None = None,
        time_end: datetime.time | None = None,
        sde_type: str = "",
        title: str = TITLE_NULL,
        place: str = "",
        detail: str = "",
    ):
        """Constructor"""
        self.__log.debug(
            f"({sde_id}){date} {time_start}-{time_end}"
            f" [{sde_type}] {title} @{place}:'{detail}'"
        )

        # ``sde_id`` が空なら、新しい ID を発行する
        self.sde_id = sde_id if sde_id else SchedDataEnt.new_id()

        self.date = date if date is not None else datetime.date.today()

        self.time_start = time_start
        self.time_end = time_end
        self.type = sde_type
        self.title = title
        self.place = place
        self.detail = htmlstr2text(detail)

        if not self.title:
            self.title = self.TITLE_NULL

    def __str__(self):
        """str(self)"""
        out_str = f"({self.sde_id}) "
        out_str += self.date.strftime("%Y/%m/%d ")

        if self.time_start:
            out_str += self.time_start.strftime("%H:%M-")
        else:
            out_str += ":-"

        if self.time_end:
            out_str += self.time_end.strftime("%H:%M ")
        else:
            out_str += ": "

        out_str += f"[{htmlstr2text(self.type)}]"
        out_str += f"{htmlstr2text(self.title)}"
        out_str += f"@{htmlstr2text(self.place)}: "
        out_str += htmlstr2text(self.detail)

        return out_str

    def mk_dataline(self):
        """
        ファイル保存用の文字列を生成
        """
        date_str = self.date.strftime("%Y/%m/%d")

        time_start_str = ":"
        if self.time_start:
            time_start_str = self.time_start.strftime("%H:%M")

        time_end_str = ":"
        if self.time_end:
            time_end_str = self.time_end.strftime("%H:%M")

        time_str = time_start_str + "-" + time_end_str
        text_htmlstr = text2htmlstr(self.detail)

        # タブ区切りの項目の並びが見えるよう、f-string にせず
        # join のまま残す（TODO-015）
        return "\t".join(  # noqa: FLY002
            [
                self.sde_id,
                date_str,
                time_str,
                self.type,
                self.title,
                self.place,
                text_htmlstr,
            ]
        )

    def search_str(self):
        """
        Returns
        -------
        search_str: str

        """
        detail = self.detail.replace("\n", " ")
        search_str = (
            f"#{self.type} +{self.title} @{self.place} detail:{detail}"
        )

        return search_str.lower()

    @classmethod
    def new_id(cls):
        sde_id = str(uuid.uuid4())
        cls.__log.debug(f"sde_id={sde_id}")
        return sde_id

    @classmethod
    def type_is_todo(cls, sde_type: str | None) -> bool:
        """
        Parameters
        ----------
        sde_type: str | None

        """
        cls.__log.debug(f"sde_type={sde_type}")
        if sde_type:
            return sde_type.startswith(cls.TYPE_PREFIX_TODO)

        return False

    def is_todo(self):
        """ToDo かどうか（``type`` の先頭で判定する）。"""
        # self.__log.debug("")
        if self.type:
            return self.type.startswith(self.TYPE_PREFIX_TODO)

        return False

    def is_holiday(self):
        """休日かどうか（``type`` で判定する）。"""
        # self.__log.debug("")
        if self.type == "":
            return False
        return self.type in self.TYPE_HOLYDAY

    def is_important(self):
        """「重要」かどうか（``title`` の先頭で判定する）。"""
        if self.title == "":
            return False
        for start_str in self.TITLE_PREFIX_IMPORTANT:
            if self.title.lower().startswith(start_str):
                return True

        return False

    def is_canceled(self):
        """「取り消し」かどうか（``title`` の先頭で判定する）。"""
        if self.title == "":
            return False

        for start_str in self.TITLE_PREFIX_CANCELED:
            if self.title.lower().startswith(start_str):
                return True

        return False

    def get_sortkey(self):
        """並べ替え用のキー文字列を返す。"""
        sort_key = (
            f"{self.date.year:02d}{self.date.month:02d}"
            f"{self.date.day:02d} {self.get_timestr()}"
        )
        if sort_key.endswith(":-:"):
            if self.is_holiday():
                sort_key = sort_key.replace(":-:", "  :  -  :  ")
            elif self.title.startswith("("):
                sort_key = sort_key.replace(":-:", "99:99-99:99")
            else:
                sort_key = sort_key.replace(":-:", "33:33-33:33")
        # self.__log.debug(f"sort_key='{sort_key}'")
        return sort_key

    def get_date(self):
        """
        Returns
        -------
        (year, month, day)
        """
        return (self.date.year, self.date.month, self.date.day)

    def set_date(self, d: datetime.date | None = None) -> None:
        """
        Parameters
        ----------
        d: datetime.date | None

        """
        self.__log.debug(f"d={d}")

        if d is None:
            self.date = datetime.date.today()
            return

        self.date = d

    def get_timestr(self) -> str:
        """
        Returns
        -------
        'HH:MM-HH:MM' : str
        ':-:', ':-HH:MM', 'HH:MM-'

        """
        time_start_str = ":"
        if self.time_start:
            time_start_str = self.time_start.strftime("%H:%M")

        time_end_str = ":"
        if self.time_end:
            time_end_str = self.time_end.strftime("%H:%M")

        time_str = f"{time_start_str}-{time_end_str}"

        return time_str


class SchedDataFile:
    """
    スケジュール・データ・ファイル
    """

    __log = getLogger(__qualname__)

    DEF_TOP_DIR = "~/ytsched/data"
    PATH_FORMAT = "%s/%04s/%02s/%02s.cgi"
    TODO_PATH_FORMAT = "%s/ToDo.cgi"

    BACKUP_EXT = ".bak"
    ENCODE: ClassVar[list[str]] = ["utf-8", "euc_jp"]

    def __init__(
        self,
        date: datetime.date | None = None,
        topdir: str = DEF_TOP_DIR,
    ):
        """
        date: datetime.date | None
            None: ToDo
        topdir: str

        """
        self.__log.debug(f"date={date}, topdir={topdir}")

        self.date = date
        self.topdir = os.path.expanduser(topdir)

        self.pathname = self.date2path(self.date, self.topdir)

        pl = self.pathname.split("/")
        self.filename = pl.pop()
        self.dirname = "/".join(pl)

        self.is_holiday = False
        self.sde = self.load()

    def __str__(self):
        """__str__"""
        out_str = (
            f"file:{self.pathname}, sde:{len(self.sde)}, "
            f"holiday:{self.is_holiday}"
        )
        return out_str

    def date2path(
        self, date: datetime.date | None = None, topdir: str = DEF_TOP_DIR
    ) -> str:
        """
        Parameters
        ----------
        date: datetime.date | None
            None: ToDo
        Returns
        -------
        path: str

        """
        if date:
            pathname = self.PATH_FORMAT % (
                topdir,
                date.strftime("%Y"),
                date.strftime("%m"),
                date.strftime("%d"),
            )
        else:
            pathname = self.TODO_PATH_FORMAT % (topdir)

        return pathname

    def load(self):
        """
        データファイルの読み込み

        Notes
        -----
        初期化時に自動的に実行される

        休日・祝日が含まれる場合は、``is_holiday``をTrueにする
        """
        # self.__log.debug("")

        self.is_holiday = False
        ok = False
        for enc in self.ENCODE:
            # self.__log.debug(f"enc={enc}")
            try:
                with open(self.pathname, encoding=enc) as f:
                    lines = f.readlines()
                    ok = True
                    break
            except FileNotFoundError:
                self.__log.debug(f"{self.pathname}: not found .. ignored")
                return []
            except UnicodeDecodeError:
                self.__log.debug(f"{enc}: decode error .. try next ..")

        if not ok:
            self.__log.warning(f"{self.pathname}: invalid encoding")
            return []

        # self.__log.debug(f"lines={lines}")
        out = []
        for l in lines:
            d = [htmlstr2text(d1) for d1 in l.split("\t")]
            if len(d) < 7:
                # 項目が足りない行は、空文字で埋めて読む。
                # 行末の改行が最終項目に残らないようにする
                d[-1] = d[-1].rstrip("\n")
                d += [""] * (7 - len(d))

            d = d[:7]
            # self.__log.debug(f"d={d}")

            date1 = d[1].split("/")
            date2 = datetime.date(int(date1[0]), int(date1[1]), int(date1[2]))

            time1 = d[2].split("-")
            if len(time1) < 2:
                # `-` が無い時刻欄は、開始・終了とも空として扱う
                time1 = ["", ""]

            time_start1 = time1[0].split(":")
            # self.__log.debug(f"time_start1={time_start1}")

            time_end1 = time1[1].split(":")
            # self.__log.debug(f"time_end1={time_end1}")

            if time_start1[0]:
                time_start2 = datetime.time(
                    int(time_start1[0]) % 24, int(time_start1[1]) % 60
                )
            else:
                time_start2 = None

            if time_end1[0]:
                time_end2 = datetime.time(
                    int(time_end1[0]) % 24, int(time_end1[1]) % 60
                )
            else:
                time_end2 = None

            sde = SchedDataEnt(
                d[0],
                date2,
                time_start2,
                time_end2,
                d[3],
                d[4],
                d[5],
                d[6],
            )
            if not self.is_holiday:
                self.is_holiday = sde.is_holiday()
                if self.is_holiday:
                    self.__log.debug(f"is_holiday={self.is_holiday}")

            out.append(sde)

        out2 = sorted(out, key=lambda x: x.get_sortkey())
        return out2

    def save(self):
        """
        データファイルへ保存

        Notes
        -----
        全て上書きされる。
        ファイルが存在し、空でない場合は、バックアップされる。

        スケジュールが 1 件も無い場合は、空のファイルを書く。
        空のファイルをバックアップしないのは、``.bak`` にしか残って
        いないデータを空で上書きしないため。
        """
        self.__log.debug("")

        if (
            os.path.exists(self.pathname)
            and os.path.getsize(self.pathname) > 0
        ):
            backup_pathname = self.pathname + self.BACKUP_EXT
            shutil.move(self.pathname, backup_pathname)

        os.makedirs(os.path.dirname(self.pathname), exist_ok=True)

        # 読み込み時の第一候補(utf-8)で書く
        with open(self.pathname, mode="w", encoding=self.ENCODE[0]) as f:
            for sde in self.sde:
                line = sde.mk_dataline()
                f.write(line + "\n")

    def add_sde(self, sde: SchedDataEnt) -> None:
        """
        Parameters
        ----------
        sde: SchedDataEnt

        """
        self.__log.debug(f"sde={sde}")
        self.sde.append(sde)
        self.sde = sorted(self.sde, key=lambda x: x.get_sortkey())

    def del_sde(self, sde_id: str | None = None) -> None:
        """
        Parameters
        ----------
        sde_id: str | None

        """
        self.__log.debug(f"sde_id={sde_id}")
        for sde in self.sde:
            if sde.sde_id == sde_id:
                self.__log.debug(f"DEL:{sde}")
                self.sde.remove(sde)
                break

        for sde in self.sde:
            self.__log.debug(f"{sde}")

    def get_sde(self, sde_id: str | None = None) -> SchedDataEnt | None:
        """
        Parameters
        ----------
        sde_id: str | None

        Returns
        -------
        sde: SchedDataEnt | None
            見つからない場合は None

        """
        self.__log.debug(f"sde_id={sde_id}")

        for sde in self.sde:
            if sde_id == sde.sde_id:
                return sde

        return None


class SchedData:
    """スケジュール・データ

    SchedDataFile をキャッシングする

    _sdf_cache = {
        date1: sdf1,
        date2: sdf2,
        :
    }

    date1, date2, .. : datetime.date | None  (None は ToDo)
    sdf1, sf2, ..    : SchedDataFile

    """

    __log = getLogger(__qualname__)

    DEF_CACHE_SIZE = 20000
    CACHE_DISCARD_RATE = 0.1

    def __init__(
        self,
        topdir: str = SchedDataFile.DEF_TOP_DIR,
        cache_size: int = DEF_CACHE_SIZE,
    ):
        """Constructor
        Parameters
        ----------
        cache_size: int

        """
        self.__log.debug(f"cache_size={cache_size}, topdir={topdir}")

        self._cache_size = cache_size
        self._topdir = topdir

        # ToDo は ``date`` が None のキーで扱う
        self._sdf_cache: collections.OrderedDict[
            datetime.date | None, SchedDataFile
        ] = collections.OrderedDict()

    def __str__(self):
        """__str__"""
        out_str = f"topdir:{self._topdir}, cache_size:{len(self._sdf_cache)}"
        return out_str

    def get_keys(self):
        """
        Returns
        -------
        date_list: list of str ['2021-01-01', '2021-01-02', .. ]

        """
        date_list = []
        for k in self._sdf_cache:
            date_list.append(f"{k}")

        return date_list

    def get_cache_size(self):
        return len(self._sdf_cache)

    def get_sdf(self, date: datetime.date | None = None) -> SchedDataFile:
        """
        キャッシュがヒットすれば、そのデータを返す。
        ヒットしなければ、読み込む。

        Parameters
        ----------
        date: datetime.date | None

        topdir: str

        Returns
        -------
        sdf: SchedDataFile

        """
        # self.__log.debug(f"date={date}")

        try:
            # self.__log.debug(f"_sdf.keys={self.get_keys()}")
            sdf = self._sdf_cache.pop(date)
            self._sdf_cache[date] = sdf
            # self.__log.debug(f"_sdf.keys={self.get_keys()}")
        except KeyError:
            self.__log.debug(f"cache miss: date={date}")

            if self.get_cache_size() >= self._cache_size:
                discard_size = int(self._cache_size * self.CACHE_DISCARD_RATE)
                for i in range(discard_size):
                    _discarded = self._sdf_cache.popitem(last=False)
                    # self.__log.debug(
                    #     f"discard[{i + 1}/{discard_size}]:"
                    #     f" date={_discarded[0]}"
                    # )

            sdf = SchedDataFile(date, self._topdir)
            self._sdf_cache[date] = sdf
            # self.__log.debug(f"_sdf.keys={self.get_keys()}")

        # if not sdf.sde:
        # self.__log.warning(f"{date} sdf.sde={sdf.sde}")

        return sdf

    def get_sde(
        self, date: datetime.date | None = None, sde_id: str = ""
    ) -> SchedDataEnt | None:
        """
        Parameters
        ----------
        date: datetime.date | None

        topdir: str

        sde_id: str


        Returns
        -------
        sde: SchedDataEnt | None
            見つからない場合は None

        """
        self.__log.debug(f"date={date}, sde_id={sde_id}")

        sdf = self.get_sdf(date)
        sde = sdf.get_sde(sde_id)
        self.__log.debug(f"sde={sde}")
        return sde

    def add_sde(self, date: datetime.date | None, sde: SchedDataEnt) -> None:
        """
        Parameters
        ----------
        date: datetime.date | None

        sde: SchedDataEnt

        """
        self.__log.debug(f"date={date}, sde={sde}")

        sdf = self.get_sdf(date)
        sdf.add_sde(sde)
        sdf.save()

    def del_sde(
        self, date: datetime.date | None = None, sde_id: str = ""
    ) -> None:
        """del_sde

        Parameters
        ----------
        date: datetime.date | None

        topdir: str

        sde_id: str

        """
        self.__log.debug(f"date={date}, sde_id={sde_id}")

        sdf = self.get_sdf(date)
        sdf.del_sde(sde_id)
        sdf.save()

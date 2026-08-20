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
import json
import os
import shutil
import uuid
from typing import Any, ClassVar

from .mylog import getLogger


def normalize(text: str) -> str:
    """判定・検索の照合に使う形へ揃える（保存する文字列は変えない）。

    揃えるのは 2 つだけ。全角括弧を半角にして、小文字にする。
    ``unicodedata.normalize("NFKC", ...)`` は使わない
    （``㍿`` や ``①`` まで変えてしまうため。docs/data-format.md 参照）。

    Parameters
    ----------
    text: str

    Returns
    -------
    normalized: str

    """
    return text.replace("（", "(").replace("）", ")").lower()


class SchedDataEnt:
    """
    スケジュール・データ・エンティティ
    """

    __log = getLogger(__qualname__)

    TIME_NULL = ":-:"
    TITLE_NULL = ""

    DATE_FORMAT = "%Y-%m-%d"
    TIME_FORMAT = "%H:%M"

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
        self.detail = detail

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

        out_str += f"[{self.type}]"
        out_str += f"{self.title}"
        out_str += f"@{self.place}: "
        out_str += self.detail

        return out_str

    def to_dict(self) -> dict[str, str | None]:
        """ファイルに書く形の dict を返す。

        キーの並びは ``docs/data-format.md`` のとおり。
        書くときは全部のキーを出す。
        """
        return {
            "sde_id": self.sde_id,
            "date": self.date.strftime(self.DATE_FORMAT),
            "time_start": self.time2str(self.time_start),
            "time_end": self.time2str(self.time_end),
            "type": self.type,
            "title": self.title,
            "place": self.place,
            "detail": self.detail,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SchedDataEnt:
        """dict から作る。

        欠けたキーは、``type`` ``title`` ``place`` ``detail`` が空文字、
        ``time_start`` ``time_end`` が None になる。

        Parameters
        ----------
        data: dict[str, Any]

        Returns
        -------
        sde: SchedDataEnt

        Raises
        ------
        ValueError
            ``date`` が無い、または日付として読めない場合

        """
        try:
            date = datetime.date.fromisoformat(data["date"])
        except (KeyError, TypeError) as e:
            raise ValueError(f"date={data.get('date')!r}: invalid") from e

        return cls(
            cls.dict_str(data, "sde_id"),
            date,
            cls.dict_time(data, "time_start"),
            cls.dict_time(data, "time_end"),
            cls.dict_str(data, "type"),
            cls.dict_str(data, "title"),
            cls.dict_str(data, "place"),
            cls.dict_str(data, "detail"),
        )

    @classmethod
    def dict_str(cls, data: dict[str, Any], key: str) -> str:
        """``data[key]`` を文字列として取り出す（無ければ空文字）。"""
        value = data.get(key)
        if value is None:
            return ""
        if isinstance(value, str):
            return value

        cls.__log.warning(f"{key}={value!r}: not a string")
        return str(value)

    @classmethod
    def dict_time(
        cls, data: dict[str, Any], key: str
    ) -> datetime.time | None:
        """``data[key]`` を時刻として取り出す（無ければ None）。"""
        value = data.get(key)
        if not value:
            return None

        try:
            return datetime.time.fromisoformat(str(value))
        except (ValueError, TypeError) as e:
            cls.__log.warning(f"{key}={value!r}: {e} .. ignored")
            return None

    @staticmethod
    def time2str(time: datetime.time | None) -> str | None:
        """時刻を ``HH:MM`` にする（None は None のまま）。"""
        if time is None:
            return None
        return time.strftime(SchedDataEnt.TIME_FORMAT)

    def mk_dataline(self) -> str:
        """
        ファイル保存用の文字列(JSON Lines の 1 行)を生成
        """
        return json.dumps(self.to_dict(), ensure_ascii=False)

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

        return normalize(search_str)

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

        Notes
        -----
        debug ログは出さない。``is_todo()`` がここへ委譲するようになり
        （TODO-021）、一覧の描画で 1 件につき何度も呼ばれるため。

        """
        if sde_type:
            return sde_type.startswith(cls.TYPE_PREFIX_TODO)

        return False

    def is_todo(self):
        """ToDo かどうか（``type`` の先頭で判定する）。"""
        return self.type_is_todo(self.type)

    def is_holiday(self):
        """休日かどうか（``type`` で判定する）。"""
        # self.__log.debug("")
        if self.type == "":
            return False
        return self.type in self.TYPE_HOLYDAY

    def title_starts_with(self, prefix_list: list[str]) -> bool:
        """``title`` が ``prefix_list`` のどれかで始まるか。

        照合は ``normalize()`` した文字列で行う
        （保存する文字列そのものは変えない）。

        Parameters
        ----------
        prefix_list: list[str]

        Returns
        -------
        bool

        """
        return normalize(self.title).startswith(tuple(prefix_list))

    def is_important(self):
        """「重要」かどうか（``title`` の先頭で判定する）。"""
        return self.title_starts_with(self.TITLE_PREFIX_IMPORTANT)

    def is_canceled(self):
        """「取り消し」かどうか（``title`` の先頭で判定する）。"""
        return self.title_starts_with(self.TITLE_PREFIX_CANCELED)

    def get_sortkey(self):
        """並べ替え用のキー文字列を返す。"""
        sort_key = (
            f"{self.date.year:02d}{self.date.month:02d}"
            f"{self.date.day:02d} {self.get_timestr()}"
        )
        if sort_key.endswith(":-:"):
            if self.is_holiday():
                sort_key = sort_key.replace(":-:", "  :  -  :  ")
            elif normalize(self.title).startswith("("):
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
        time_start_str = self.time2str(self.time_start) or ":"
        time_end_str = self.time2str(self.time_end) or ":"

        return f"{time_start_str}-{time_end_str}"


class SchedDataFile:
    """
    スケジュール・データ・ファイル
    """

    __log = getLogger(__qualname__)

    DEF_TOP_DIR = "~/ytsched/data"
    PATH_FORMAT = "%s/%04s/%02s/%02s.jsonl"
    TODO_PATH_FORMAT = "%s/ToDo.jsonl"

    BACKUP_EXT = ".bak"
    ENCODING = "utf-8"

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

        # 読めずに飛ばした行を、生のバイト列のまま持つ。
        # ``save()`` がこれを末尾へ書き戻す（TODO-020）
        self.skipped_lines: list[bytes] = []

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

    def load(self) -> list[SchedDataEnt]:
        """
        データファイル(JSON Lines)の読み込み

        Notes
        -----
        初期化時に自動的に実行される

        休日・祝日が含まれる場合は、``is_holiday``をTrueにする

        読めない行は、その行だけを飛ばして警告する
        （ファイル全体は捨てない）。
        飛ばした行は ``skipped_lines`` に生のバイト列のまま残し、
        ``save()`` が書き戻す。ただし**空行は書き戻さない**
        (飛ばしても失うデータが無いため)。
        """
        # self.__log.debug("")

        self.is_holiday = False
        self.skipped_lines = []

        try:
            with open(self.pathname, mode="rb") as f:
                data = f.read()
        except FileNotFoundError:
            self.__log.debug(f"{self.pathname}: not found .. ignored")
            return []

        out = []
        for i, raw_line in enumerate(self.split_lines(data), start=1):
            sde = self.load_line(raw_line, i)
            if sde is None:
                if not self.is_empty_line(raw_line):
                    # 捨てずに残して、``save()`` で書き戻す。
                    # 空行だけは書き戻さない(飛ばしても失うデータが
                    # 無いため)
                    self.skipped_lines.append(raw_line)
                continue

            if not self.is_holiday:
                self.is_holiday = sde.is_holiday()
                if self.is_holiday:
                    self.__log.debug(f"is_holiday={self.is_holiday}")

            out.append(sde)

        return sorted(out, key=lambda x: x.get_sortkey())

    @staticmethod
    def split_lines(data: bytes) -> list[bytes]:
        """バイト列を行に分ける。

        ``str.splitlines()`` は使わない。U+2028 (LINE SEPARATOR) でも
        切ってしまい、``detail`` に U+2028 を含む 1 件が 2 行に割れる
        （実データに 1 件あった）。

        Parameters
        ----------
        data: bytes

        Returns
        -------
        lines: list[bytes]

        """
        if data.endswith(b"\n"):
            # 行末の改行で空行が 1 つ増えないようにする
            data = data[:-1]

        if not data:
            return []

        return data.split(b"\n")

    @staticmethod
    def is_empty_line(raw_line: bytes) -> bool:
        """空行(空白だけの行を含む)かどうか。

        飛ばした行のうち、空行だけは ``save()`` で書き戻さないので、
        判定をここ 1 か所にまとめておく。
        """
        return not raw_line.strip()

    def load_line(self, raw_line: bytes, lineno: int) -> SchedDataEnt | None:
        """1 行を読む。読めない行は警告して None を返す。

        Parameters
        ----------
        raw_line: bytes
        lineno: int
            警告に出す行番号(1 始まり)

        Returns
        -------
        sde: SchedDataEnt | None

        """
        where = f"{self.pathname}:{lineno}"

        if self.is_empty_line(raw_line):
            self.__log.warning(f"{where}: empty line .. ignored")
            return None

        try:
            line = raw_line.decode(self.ENCODING)
        except UnicodeDecodeError as e:
            self.__log.warning(f"{where}: {e} .. ignored")
            return None

        try:
            data = json.loads(line)
        except json.JSONDecodeError as e:
            self.__log.warning(f"{where}: {e} .. ignored")
            return None

        if not isinstance(data, dict):
            self.__log.warning(f"{where}: not an object .. ignored")
            return None

        try:
            sde = SchedDataEnt.from_dict(data)
        except ValueError as e:
            self.__log.warning(f"{where}: {e} .. ignored")
            return None

        if self.date is not None and sde.date != self.date:
            # ファイル名から決まる日付を信じて黙って書き換えたりはせず、
            # 行の ``date`` を使う
            self.__log.warning(
                f"{where}: date={sde.date} != {self.date}"
                " .. use the date in the line"
            )

        return sde

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

        読み込みで飛ばした行(``skipped_lines``)は、末尾へ
        **元のバイトのまま**書き戻す。デコードできない行もあるので、
        書き出しはバイナリで行う。空行は ``skipped_lines`` に
        入らないので、書き戻されない。
        """
        self.__log.debug("")

        if (
            os.path.exists(self.pathname)
            and os.path.getsize(self.pathname) > 0
        ):
            backup_pathname = self.pathname + self.BACKUP_EXT
            shutil.move(self.pathname, backup_pathname)

        os.makedirs(os.path.dirname(self.pathname), exist_ok=True)

        with open(self.pathname, mode="wb") as f:
            for sde in self.sde:
                line = sde.mk_dataline()
                f.write(line.encode(self.ENCODING) + b"\n")

            f.writelines(raw_line + b"\n" for raw_line in self.skipped_lines)

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

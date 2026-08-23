#
# (c) Yoichi Tanibayashi
#
"""旧形式(タブ区切りテキスト)から JSON Lines への移行 (TODO-020)

変換の手順は ``docs/data-format.md`` の「変換の手順」1〜6 のとおり。

対象は ``{年}/{月}/{日}.cgi`` と ``ToDo.cgi`` だけ。
``{日}-backup.cgi`` ``{日}.cgi.bak`` ``iappli_log.cgi`` は対象にしない。
"""

__author__ = "Yoichi Tanibayashi"
__date__ = "2026/08"

import dataclasses
import datetime
import html
import json
import os
import pathlib
import re
from typing import Any, ClassVar

from .mylog import getLogger
from .ytsched import SchedDataFile

_log = getLogger(__name__)

#: ``<br>`` ``<BR>`` ``<br />`` など(大小・スラッシュの有無を問わない)
BR_PATTERN = re.compile(r"<br\s*/?>", re.IGNORECASE)

#: NBSP
NBSP = "\u00a0"

#: 旧形式の項目数
N_FIELD = 7

#: 行ごとに試すエンコーディング(この順)
ENCODINGS = ("utf-8", "euc_jp")

#: 最後の砦。読めないバイトだけを U+FFFD にして、行は残す
FALLBACK_ENCODING = "euc_jp"


def decode_line(raw_line: bytes) -> str:
    """1 行をデコードする。

    utf-8 → euc_jp の順に試し、どちらでも読めなければ euc_jp の
    ``errors="replace"`` で読む(**行は捨てない**)。

    ファイル単位でデコードしないのは、1 行だけ壊れたファイルの
    残りの行を失わないため(``docs/data-format.md`` の手順 1)。

    Parameters
    ----------
    raw_line: bytes

    Returns
    -------
    line: str

    """
    for enc in ENCODINGS:
        try:
            return raw_line.decode(enc)
        except UnicodeDecodeError:
            continue

    _log.warning(f"{raw_line!r}: invalid encoding .. use U+FFFD")
    return raw_line.decode(FALLBACK_ENCODING, errors="replace")


def split_fields(line: str) -> list[str]:
    """タブで 7 つに分ける(``docs/data-format.md`` の手順 2)。

    7 個に満たなければ空文字で埋め、8 個以上あれば 8 個目から先を
    ``detail`` の続きとしてタブでつなぎ直す(**捨てない**)。
    """
    field = line.split("\t")

    if len(field) < N_FIELD:
        field += [""] * (N_FIELD - len(field))
    elif len(field) > N_FIELD:
        field = [
            *field[: N_FIELD - 1],
            "\t".join(field[N_FIELD - 1 :]),
        ]

    return field


def conv_date(date_str: str) -> str:
    """``YYYY/MM/DD`` を ``YYYY-MM-DD`` にする(手順 3)。

    Raises
    ------
    ValueError
        日付として読めない場合

    """
    field = date_str.strip().split("/")
    if len(field) != 3:
        raise ValueError(f"date={date_str!r}: invalid")

    year, month, day = (int(f) for f in field)
    return datetime.date(year, month, day).isoformat()


def conv_time1(time_str: str) -> str | None:
    """``HH:MM`` を直す。空なら None(手順 4)。

    範囲外の値は旧コードと同じく、時を 24、分を 60 で割った余りにする
    (実データの ``28:00`` が ``04:00`` になる)。
    """
    field = time_str.strip().split(":")
    if len(field) < 2 or not field[0]:
        return None

    try:
        hour = int(field[0]) % 24
        minute = int(field[1]) % 60
    except ValueError:
        _log.warning(f"time={time_str!r}: invalid .. ignored")
        return None

    return f"{hour:02d}:{minute:02d}"


def conv_time(time_str: str) -> tuple[str | None, str | None]:
    """``HH:MM-HH:MM`` を ``time_start`` と ``time_end`` に分ける(手順 4)。"""
    field = time_str.split("-")
    if len(field) < 2:
        # ``-`` が無い時刻欄は、開始・終了とも空として扱う
        return (None, None)

    return (conv_time1(field[0]), conv_time1(field[1]))


def html2text(text: str) -> str:
    """HTML 文字列を素のテキストに戻す(手順 5)。

    **順番が大事。**``<br />`` を改行に → ``html.unescape()`` を 2 回 →
    NBSP を半角空白に。``<br />`` 以外の HTML タグはそのまま残す。

    2 回かけるのは、実データが二重にエスケープされているため
    (``&amp;#160;``)。**3 回以上はかけない。**

    旧コードの ``htmlstr2text()`` は使わない(全角括弧の半角化まで
    やってしまい、手順 6「全角括弧はそのままにする」を破る)。
    """
    out_text = BR_PATTERN.sub("\n", text)
    out_text = html.unescape(html.unescape(out_text))
    return out_text.replace(NBSP, " ")


def line2dict(line: str) -> dict[str, Any]:
    """旧形式の 1 行を、新形式の dict にする。

    Raises
    ------
    ValueError
        日付が読めない場合

    """
    field = split_fields(line)

    date_str = conv_date(field[1])
    time_start, time_end = conv_time(field[2])

    return {
        "sde_id": field[0],
        "date": date_str,
        "time_start": time_start,
        "time_end": time_end,
        "type": html2text(field[3]),
        "title": html2text(field[4]),
        "place": html2text(field[5]),
        "detail": html2text(field[6]),
    }


@dataclasses.dataclass
class MigrateStat:
    """変換の結果"""

    files: int = 0
    """変換したファイル数"""

    skipped_files: int = 0
    """既に ``.jsonl`` があって飛ばしたファイル数"""

    lines: int = 0
    """変換した行数"""

    empty_lines: int = 0
    """空行(飛ばした)"""

    error_lines: int = 0
    """変換できなかった行数(捨てずに書き出す)"""

    @property
    def skipped_lines(self) -> int:
        """飛ばした行数"""
        return self.empty_lines + self.error_lines


class Migrator:
    """旧形式のデータディレクトリを JSON Lines へ変換する"""

    __log = getLogger(__qualname__)

    OLD_EXT = ".cgi"
    NEW_EXT = ".jsonl"

    TODO_NAME = "ToDo"

    DEF_ERROR_FILE = "migrate-errors.txt"

    #: ``{年}/{月}/{日}.cgi`` だけに当てる
    #: (``{日}-backup.cgi`` ``{日}.cgi.bak`` は当たらない)
    DAILY_GLOB: ClassVar[str] = (
        "[0-9][0-9][0-9][0-9]/[0-9][0-9]/[0-9][0-9].cgi"
    )

    def __init__(
        self,
        topdir: str,
        dry_run: bool = False,
        error_file: str = DEF_ERROR_FILE,
    ):
        """Constructor

        Parameters
        ----------
        topdir: str
            データディレクトリ
        dry_run: bool
            True なら書かずに数えるだけ
        error_file: str
            変換できなかった行の書き出し先

        """
        self.__log.debug(
            f"topdir={topdir}, dry_run={dry_run}, error_file={error_file}"
        )

        self.topdir = pathlib.Path(os.path.expanduser(topdir))
        self.dry_run = dry_run
        self.error_file = pathlib.Path(os.path.expanduser(error_file))

        self.stat = MigrateStat()
        self.error_lines: list[str] = []

    def find_files(self) -> list[pathlib.Path]:
        """変換の対象になるファイルを探す。"""
        files = sorted(self.topdir.glob(self.DAILY_GLOB))

        todo_file = self.topdir / (self.TODO_NAME + self.OLD_EXT)
        if todo_file.is_file():
            files.append(todo_file)

        self.__log.debug(f"files={len(files)}")
        return files

    def conv_file(self, path: pathlib.Path) -> list[str]:
        """1 ファイルを変換して、書き出す行のリストを返す。"""
        raw_data = path.read_bytes()

        out_lines: list[str] = []
        # 行の分け方(U+2028 で切らない)は読み込み側と同じものを使う
        raw_lines = SchedDataFile.split_lines(raw_data)
        for i, raw_line in enumerate(raw_lines, start=1):
            # CRLF の旧データで、行末の ``\r`` が最後の項目(``detail``)に
            # 残らないようにする (TODO-029)。旧形式ではテキストモードの
            # ``readlines()`` で消えていたので、移行で新しく入れない
            line_bytes = raw_line.removesuffix(b"\r")

            if SchedDataFile.is_empty_line(line_bytes):
                self.stat.empty_lines += 1
                continue

            line = decode_line(line_bytes)

            try:
                data = line2dict(line)
            except ValueError as e:
                self.__log.warning(f"{path}:{i}: {e} .. not converted")
                self.stat.error_lines += 1
                self.error_lines.append(f"{path}:{i}\t{line}")
                continue

            out_lines.append(json.dumps(data, ensure_ascii=False))

        self.stat.lines += len(out_lines)
        return out_lines

    def migrate_file(self, path: pathlib.Path) -> None:
        """1 ファイルを変換して保存する。元の ``.cgi`` は消さない。"""
        new_path = path.with_suffix(self.NEW_EXT)
        if new_path.exists():
            self.__log.warning(f"{new_path}: already exists .. skipped")
            self.stat.skipped_files += 1
            return

        out_lines = self.conv_file(path)
        self.stat.files += 1

        if self.dry_run:
            return

        with open(new_path, mode="w", encoding=SchedDataFile.ENCODING) as f:
            f.writelines(line + "\n" for line in out_lines)

    def save_error_lines(self) -> None:
        """変換できなかった行を書き出す。"""
        if not self.error_lines or self.dry_run:
            return

        with open(
            self.error_file, mode="w", encoding=SchedDataFile.ENCODING
        ) as f:
            f.writelines(line + "\n" for line in self.error_lines)

    def main(self) -> MigrateStat:
        """変換を実行して、結果を返す。"""
        files = self.find_files()

        if not files:
            self.__log.warning(
                f"{self.topdir}: no target file .. check --datadir"
            )

        for path in files:
            self.migrate_file(path)

        self.save_error_lines()

        if self.dry_run:
            print("===== dry run: 書き出していません =====")

        print(f"変換したファイル: {self.stat.files}")
        print(f"飛ばしたファイル: {self.stat.skipped_files}")
        print(f"変換した行      : {self.stat.lines}")
        print(
            f"飛ばした行      : {self.stat.skipped_lines}"
            f" (空行 {self.stat.empty_lines},"
            f" 変換できず {self.stat.error_lines})"
        )

        if self.error_lines and not self.dry_run:
            print(f"変換できなかった行: {self.error_file}")

        return self.stat

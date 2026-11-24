#
# (c) 2026 ytani01
#
"""予定の添付ファイル（``attachments/{UUID}/``）の読み書き（TODO-237）。

版を除いた UUID ごとにフォルダを分ける。編集しても UUID は変わらない
ので、どの版から見ても同じ添付が見える。tornado を知らない。
"""

from __future__ import annotations

__author__ = "ytani01"
__date__ = "2026/11"

import contextlib
import itertools
import mimetypes
import re
import shutil
import urllib.parse
from pathlib import Path

from .fix_id import is_uuid
from .mylog import getLogger
from .ytsched import SchedDataEnt

#: その場に表示する画像の種類。SVG はスクリプトを含められるので入れない
IMAGE_TYPES = frozenset(
    {
        "image/png",
        "image/jpeg",
        "image/gif",
        "image/webp",
        "image/bmp",
        "image/avif",
    }
)


class AttachStore:
    """``{データディレクトリ}/attachments/{UUID}/`` を扱う。"""

    __log = getLogger(__qualname__)

    DIRNAME = "attachments"
    #: ファイル名の上限（UTF-8 のバイト数）。ext4 などの上限に合わせる
    MAX_NAME_BYTES = 255
    #: これより長い ``Path.suffix`` は拡張子とみなさない（縮めるときに残さない）
    MAX_SUFFIX_BYTES = 32

    def __init__(self, topdir: str | Path):
        """Constructor

        Parameters
        ----------
        topdir: str | Path
            データディレクトリ。``~`` は展開する。

        """
        self.rootdir = Path(topdir).expanduser() / self.DIRNAME

    @staticmethod
    def uuid_of(sde_id: str) -> str | None:
        """``sde_id`` の UUID 部分。``{UUID}-{版}`` の形でなければ ``None``。"""
        split = SchedDataEnt.split_id(sde_id)
        return split[0] if split else None

    @classmethod
    def safe_name(cls, filename: str) -> str | None:
        """アップロードされたファイル名から、置いてよい名前を返す。

        パスの部分を捨て、先頭の ``.`` と空白、末尾の空白を除く（隠し
        ファイルと ``..`` を作らない）。長すぎれば拡張子を残して
        ``MAX_NAME_BYTES`` に縮める。制御文字を含むか、空になれば
        ``None``。2 回通しても結果は変わらない（``is_valid_name()``
        がこれに頼る）。
        """
        name = filename.replace("\\", "/").rsplit("/", 1)[-1]
        name = re.sub(r"^[\s.]+", "", name)
        if not name or any(ord(c) < 0x20 or ord(c) == 0x7F for c in name):
            return None
        return cls._fit(name).rstrip()

    @classmethod
    def _fit(cls, name: str, n: int = 0) -> str:
        """``n`` が 0 でなければ ``-{n}`` を拡張子の前に付け、UTF-8 で
        ``MAX_NAME_BYTES`` 以内に収まるよう、拡張子の前を縮める。
        """
        stem, suffix = Path(name).stem, Path(name).suffix
        if len(suffix.encode()) > cls.MAX_SUFFIX_BYTES:
            stem, suffix = name, ""
        tail = (f"-{n}" if n else "") + suffix
        room = cls.MAX_NAME_BYTES - len(tail.encode())
        return stem.encode()[:room].decode(errors="ignore") + tail

    @classmethod
    def is_valid_name(cls, name: str) -> bool:
        """``name`` が ``safe_name()`` を通したままの形か。"""
        return cls.safe_name(name) == name

    @staticmethod
    def is_image(name: str) -> bool:
        """その場に表示する画像か（拡張子で判定する）。"""
        return mimetypes.guess_type(name)[0] in IMAGE_TYPES

    @classmethod
    def url_path(cls, sde_id: str, name: str) -> str:
        """``url_prefix`` に続ける、添付ファイルの URL のパス。"""
        uuid_part = cls.uuid_of(sde_id) or ""
        return f"attach/{uuid_part}/{urllib.parse.quote(name, safe='')}"

    def _dir(self, uuid_part: str) -> Path:
        if not is_uuid(uuid_part):
            raise ValueError(f"not a UUID: {uuid_part!r}")
        return self.rootdir / uuid_part

    def list_files(self, sde_id: str) -> list[str]:
        """``sde_id`` の UUID に付いているファイル名を、名前順に返す。"""
        uuid_part = self.uuid_of(sde_id)
        if uuid_part is None:
            return []
        try:
            return sorted(
                p.name for p in self._dir(uuid_part).iterdir() if p.is_file()
            )
        except FileNotFoundError, NotADirectoryError:
            return []

    def add(self, sde_id: str, filename: str, body: bytes) -> str | None:
        """ファイルを置き、置いた名前を返す。

        同じ名前があれば上書きせず、``名前-1.拡張子`` のように番号を
        付ける。``sde_id`` が ``{UUID}-{版}`` の形でないか、名前が
        使えなければ置かずに ``None`` を返す。
        """
        uuid_part = self.uuid_of(sde_id)
        name = self.safe_name(filename)
        if uuid_part is None or name is None:
            self.__log.warning(
                f"attachment ignored: sde_id={sde_id!r}, filename={filename!r}"
            )
            return None

        dirpath = self._dir(uuid_part)
        dirpath.mkdir(parents=True, exist_ok=True)
        for n in itertools.count():
            candidate = name if n == 0 else self._fit(name, n)
            path = dirpath / candidate
            try:
                f = path.open("xb")
            except FileExistsError:
                continue
            try:
                with f:
                    f.write(body)
            except BaseException:
                path.unlink(missing_ok=True)
                raise
            self.__log.info(f"added: {path}")
            return candidate
        raise AssertionError("unreachable")

    def remove(self, sde_id: str, name: str) -> None:
        """ファイルを 1 つ消す。フォルダが空になればフォルダも消す。"""
        uuid_part = self.uuid_of(sde_id)
        if uuid_part is None or not self.is_valid_name(name):
            return
        dirpath = self._dir(uuid_part)
        (dirpath / name).unlink(missing_ok=True)
        self.__log.info(f"removed: {dirpath / name}")
        with contextlib.suppress(OSError):  # 空でない、または無い
            dirpath.rmdir()

    def has_dir(self, uuid_part: str) -> bool:
        return is_uuid(uuid_part) and self._dir(uuid_part).is_dir()

    def remove_dir(self, uuid_part: str) -> None:
        """``uuid_part`` のフォルダを中身ごと消す。"""
        dirpath = self._dir(uuid_part)
        shutil.rmtree(dirpath, ignore_errors=True)
        self.__log.info(f"removed: {dirpath}")

#
# (c) 2026 ytani01
#
"""
ゴミ箱(trash.jsonl)への追記
"""

from __future__ import annotations

__author__ = "ytani01"
__date__ = "2026/08"

import dataclasses
import datetime
import json
import os
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

from .mylog import getLogger

if TYPE_CHECKING:
    from .ytsched import SchedDataEnt


@dataclasses.dataclass(frozen=True)
class TrashEntry:
    """ゴミ箱の 1 行。``trashed_at`` はファイルに書いた文字列のまま持つ。"""

    trashed_at: str
    sde: SchedDataEnt


class TrashFile:
    """削除・編集で消える予定を ``trash.jsonl`` へ追記するクラス。

    追記のときは全件書き直しをしない。``delete_many()`` は
    ゴミ箱から完全に消すための操作なので、全件を書き直す。これは
    ``SchedDataFile`` と違い ``.bak`` への退避はしない（ゴミ箱の
    ゴミ箱になって意味が無いため）。
    """

    __log = getLogger(__qualname__)

    FILENAME = "trash.jsonl"
    ENCODING = "utf-8"

    def __init__(self, topdir: str | Path):
        """Constructor

        Parameters
        ----------
        topdir: str | Path
            データディレクトリ。``~`` は展開する。

        """
        self.topdir = Path(topdir).expanduser()
        self.pathname = self.topdir / self.FILENAME

        self.__log.debug(f"pathname={self.pathname}")

    def add(self, sde: SchedDataEnt) -> None:
        """``sde`` の内容を、消したタイムスタンプ付きで末尾へ追記する。

        Parameters
        ----------
        sde: SchedDataEnt

        """
        entry = {
            # ``trashed_at`` は復活する 1 行を指定する値でもある。同じ
            # ``sde_id`` を短時間に何度も削除しても区別できるよう、秒では
            # なくマイクロ秒まで残す。
            "trashed_at": datetime.datetime.now().isoformat(
                timespec="microseconds"
            ),
            **sde.to_dict(),
        }
        line = json.dumps(entry, ensure_ascii=False)

        self.pathname.parent.mkdir(parents=True, exist_ok=True)

        with self.pathname.open(mode="ab") as f:
            f.write(line.encode(self.ENCODING) + b"\n")

    def entries(
        self, sde_id: str | None = None, max_entries: int = 100
    ) -> list[TrashEntry]:
        """新しい順に最大 ``max_entries`` 件を返す。

        壊れた行は、通常データの読み出しと同様に警告して飛ばす。画面から
        開くときだけ ``sde_id`` で絞り込める。
        """
        if max_entries <= 0 or not self.pathname.exists():
            return []

        entries: list[TrashEntry] = []
        with self.pathname.open(encoding=self.ENCODING) as f:
            for lineno, line in enumerate(f, start=1):
                try:
                    data = json.loads(line)
                    trashed_at = data["trashed_at"]
                    if not isinstance(trashed_at, str):
                        raise TypeError("trashed_at is not a string")
                    if sde_id is not None and data.get("sde_id") != sde_id:
                        continue
                    from .ytsched import SchedDataEnt

                    entries.append(
                        TrashEntry(trashed_at, SchedDataEnt.from_dict(data))
                    )
                except (
                    json.JSONDecodeError,
                    TypeError,
                    ValueError,
                    KeyError,
                ) as e:
                    self.__log.warning(
                        f"{self.pathname}:{lineno}: {e} .. ignored"
                    )

        entries.sort(key=lambda entry: entry.trashed_at, reverse=True)
        return entries[:max_entries]

    def count(self) -> int:
        """有効な行数を返す。``entries()`` と違い頭打ちにしない。

        壊れた行は ``entries()`` と同じ考え方で飛ばす（数に入れない）。
        ただし ``SchedDataEnt.from_dict()`` までは呼ばず、軽く済ませる。
        """
        if not self.pathname.exists():
            return 0

        count = 0
        with self.pathname.open(encoding=self.ENCODING) as f:
            for lineno, line in enumerate(f, start=1):
                try:
                    data = json.loads(line)
                    trashed_at = data["trashed_at"]
                    if not isinstance(trashed_at, str):
                        raise TypeError("trashed_at is not a string")
                except (json.JSONDecodeError, TypeError, KeyError) as e:
                    self.__log.warning(
                        f"{self.pathname}:{lineno}: {e} .. ignored"
                    )
                    continue
                count += 1

        return count

    def get(self, sde_id: str, trashed_at: str) -> TrashEntry | None:
        """``sde_id`` と ``trashed_at`` が一致する 1 行を返す。"""
        for entry in self.entries(sde_id, max_entries=2**31 - 1):
            if entry.trashed_at == trashed_at:
                return entry
        return None

    def delete_many(self, entries: set[tuple[str, str]]) -> int:
        """指定された ``(sde_id, trashed_at)`` の行を取り除いて消す。

        同じ ``sde_id``/``trashed_at`` の行が複数あることは無い想定だが、
        あれば全て取り除く。壊れていて ``entries()`` が警告して飛ばす
        行は、復旧の手がかりを残すため書き直しでも消さずそのまま残す。

        同じ組の行が複数あればすべて取り除き、実際に消した行数を返す。
        一致がなければ（ファイルが無い場合を含む）書き直さずに 0 を返す。
        """
        if not entries or not self.pathname.exists():
            return 0

        with self.pathname.open(encoding=self.ENCODING) as f:
            lines = f.readlines()

        kept: list[str] = []
        deleted = 0
        for line in lines:
            try:
                data = json.loads(line)
                trashed_at = data["trashed_at"]
                if not isinstance(trashed_at, str):
                    raise TypeError("trashed_at is not a string")
                from .ytsched import SchedDataEnt

                sde = SchedDataEnt.from_dict(data)
            except (
                json.JSONDecodeError,
                TypeError,
                ValueError,
                KeyError,
            ):
                kept.append(line)
                continue
            if (sde.sde_id, trashed_at) in entries:
                deleted += 1
                continue
            kept.append(line)

        if not deleted:
            return 0

        self._write_lines(kept)
        return deleted

    def delete(self, sde_id: str, trashed_at: str) -> bool:
        """1 組を削除する ``delete_many()`` の互換用ラッパ。"""
        return self.delete_many({(sde_id, trashed_at)}) > 0

    def _write_lines(self, lines: list[str]) -> None:
        """``lines`` で ``trash.jsonl`` を書き直す。

        同じディレクトリの一時ファイルへ書いてから ``Path.replace()`` で
        差し替える（途中で落ちたときに全部失わないため）。
        ``tempfile.mkstemp()`` が作る一時ファイルは既定で 0600 になるため、
        差し替える前に元の ``trash.jsonl`` のパーミッションを引き継ぐ。
        元のファイルが無いとき（呼び出し元は必ずファイルがある前提だが、
        念のため）は、一時ファイルの既定のパーミッションのまま書く。
        """
        fd, tmp_name = tempfile.mkstemp(
            dir=self.pathname.parent, prefix=f".{self.FILENAME}."
        )
        try:
            if self.pathname.exists():
                os.fchmod(fd, self.pathname.stat().st_mode)
            with os.fdopen(fd, mode="w", encoding=self.ENCODING) as f:
                f.writelines(lines)
            Path(tmp_name).replace(self.pathname)
        except BaseException:
            Path(tmp_name).unlink(missing_ok=True)
            raise

#
# (c) 2026 ytani01
#
"""
ゴミ箱(trash.jsonl)への追記
"""

from __future__ import annotations

__author__ = "ytani01"
__date__ = "2026/08"

import datetime
import json
from pathlib import Path
from typing import TYPE_CHECKING

from .mylog import getLogger

if TYPE_CHECKING:
    from .ytsched import SchedDataEnt


class TrashFile:
    """削除・編集で消える予定を ``trash.jsonl`` へ追記するだけのクラス。

    ``SchedDataFile`` と違い、全件書き直しも ``.bak`` への退避もしない。
    追記のみ（``open(mode="ab")``）。読み出し・復活は扱わない
    （TODO-085。復活の UI は TODO-086）。
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
            "trashed_at": datetime.datetime.now().isoformat(
                timespec="seconds"
            ),
            **sde.to_dict(),
        }
        line = json.dumps(entry, ensure_ascii=False)

        self.pathname.parent.mkdir(parents=True, exist_ok=True)

        with self.pathname.open(mode="ab") as f:
            f.write(line.encode(self.ENCODING) + b"\n")

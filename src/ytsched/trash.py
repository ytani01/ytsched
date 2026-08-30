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
    """削除・編集で消える予定を ``trash.jsonl`` へ追記するだけのクラス。

    ``SchedDataFile`` と違い、全件書き直しも ``.bak`` への退避もしない。
    追記と、ゴミ箱画面用の読み出しを扱う。
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

    def get(self, sde_id: str, trashed_at: str) -> TrashEntry | None:
        """``sde_id`` と ``trashed_at`` が一致する 1 行を返す。"""
        for entry in self.entries(sde_id, max_entries=2**31 - 1):
            if entry.trashed_at == trashed_at:
                return entry
        return None

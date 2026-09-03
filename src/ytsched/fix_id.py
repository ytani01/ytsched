#
# (c) 2026 ytani01
#
"""予定の ``sde_id`` を ``{UUID}-{版}`` の形へ振り直す (TODO-171)

版が付く前の ``sde_id`` が UUID のもの・旧形式のものが混在している。
全データを走査して、新しい形式でない ``sde_id`` を差し替える。

対象は ``{年}/{月}/{日}.jsonl``・``ToDo.jsonl``・``trash.jsonl`` の 3 つ
（``trash.jsonl`` は TODO-170 では対象外にしていたが、TODO-171 から
対象に加えた）。``.cgi``・``.bak`` は対象外のまま。

1 行ずつ JSON として読み、``sde_id`` を次のとおり判定して差し替える。

- 既に ``{UUID}-{版}`` の形（``SchedDataEnt.split_id()`` が通る）
  → そのまま
- UUID の形（``is_uuid()``）→ UUID は保って ``-1`` を付ける
- それ以外 → 新しい UUID の ``-1``

``trash.jsonl`` の行も 1 行ずつ独立に振り直す。旧形式だった予定は、
ゴミ箱の行と現在の予定が繋がらなくなる。既に UUID が一致していた行も、
両方が ``-1`` になって版では区別できなくなる。ここは割り切る
（``docs/data-format.md`` ではなく ``TODO.md`` の TODO-171 を参照）。

他のキーは値も並び順も変えない（``json.loads`` の結果は挿入順を保つ
ので、``sde_id`` だけ代入して ``json.dumps(..., ensure_ascii=False)``
で書き直せばよい）。``trash.jsonl`` は ``trashed_at`` が先頭にあるが、
同じやり方でキーの並びは保たれる。JSON として読めない行、``sde_id``
キーが無い行、``sde_id`` が文字列でない行は、そのまま書き戻して数える
（``SchedDataFile.load()`` が読めない行を ``skipped_lines`` に残すのと
同じ考え方。行は捨てない）。空行はそのまま書き戻し、「読めなかった行」
には数えない（``SchedDataFile.load()`` も空行は警告もカウントもしない）。

書き戻しは同じディレクトリの一時ファイルへ書いてから ``os.replace()``。
バックアップ（``.bak``）は作らない。書き換える行が 1 行も無いファイルは
書かない（更新時刻を動かさない）。
"""

from __future__ import annotations

import dataclasses
import json
import os
import pathlib
import re
import tempfile
from typing import Any

from .mylog import getLogger
from .ytsched import SchedDataEnt, SchedDataFile

__author__ = "ytani01"
__date__ = "2026/09"

#: 小文字ハイフン付き 36 文字。``uuid.UUID()`` は波括弧付きや
#: ハイフン無しも通してしまうので、正規表現で厳密に見る
UUID_PATTERN = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
)


def is_uuid(sde_id: str) -> bool:
    """``sde_id`` が版の付いていない UUID の形かどうか。"""
    return bool(UUID_PATTERN.match(sde_id))


@dataclasses.dataclass
class FixIdStat:
    """振り直しの結果"""

    files_scanned: int = 0
    """走査したファイル数"""

    files_changed: int = 0
    """書き換えたファイル数"""

    lines_changed: int = 0
    """書き換えた行数"""

    lines_already_ok: int = 0
    """元から ``{UUID}-{版}`` の形だった行数"""

    lines_unreadable: int = 0
    """読めなかった(そのまま残した)行数"""


class IdFixer:
    """予定の ``sde_id`` を ``{UUID}-{版}`` の形へ振り直す"""

    __log = getLogger(__qualname__)

    def __init__(self, topdir: str, dry_run: bool = False):
        """Constructor

        Parameters
        ----------
        topdir: str
            データディレクトリ
        dry_run: bool
            True なら書き換えずに件数だけ数える

        """
        self.__log.debug(f"topdir={topdir}, dry_run={dry_run}")

        self.topdir = pathlib.Path(topdir).expanduser()
        self.dry_run = dry_run

        self.stat = FixIdStat()

    def find_files(self) -> list[pathlib.Path]:
        """対象になるファイルを探す。

        列挙そのものは ``SchedDataFile.list_all_files()`` に持たせて
        ある（``SchedData.max_version()`` と共用するため。TODO-171）。
        """
        files = SchedDataFile.list_all_files(self.topdir)
        self.__log.debug(f"files={len(files)}")
        return files

    def fix_line(self, raw_line: bytes) -> tuple[bytes, bool]:
        """1 行を見て、必要なら ``sde_id`` を差し替える。

        Returns
        -------
        (new_raw_line, changed): tuple[bytes, bool]

        """
        if SchedDataFile.is_empty_line(raw_line):
            # 空行は「読めなかった行」に数えない
            # (``SchedDataFile.load()`` も空行は警告もカウントもしない)
            return raw_line, False

        try:
            line_str = raw_line.decode(SchedDataFile.ENCODING)
            data: Any = json.loads(line_str)
        except (UnicodeDecodeError, json.JSONDecodeError):  # fmt: skip
            self.stat.lines_unreadable += 1
            return raw_line, False

        if not isinstance(data, dict) or not isinstance(
            data.get("sde_id"), str
        ):
            self.stat.lines_unreadable += 1
            return raw_line, False

        sde_id = data["sde_id"]

        if SchedDataEnt.split_id(sde_id) is not None:
            self.stat.lines_already_ok += 1
            return raw_line, False

        if is_uuid(sde_id):
            new_sde_id = SchedDataEnt.format_id(sde_id, 1)
        else:
            new_sde_id = SchedDataEnt.new_id()

        data["sde_id"] = new_sde_id
        self.stat.lines_changed += 1
        new_line = json.dumps(data, ensure_ascii=False)
        return new_line.encode(SchedDataFile.ENCODING), True

    def fix_file(self, path: pathlib.Path) -> None:
        """1 ファイルを走査して、必要なら書き戻す。

        書き戻すときは、どの行にも無条件で ``\\n`` を付ける。
        そのため、**元のファイルが改行で終わっていなくても、
        書き戻したファイルは必ず改行で終わる**。JSON Lines は
        改行で終わるのが正しい形で、``SchedDataFile.save()``
        （通常の保存経路）も必ず改行を付けるため、これに揃えている。
        """
        raw_data = path.read_bytes()
        raw_lines = SchedDataFile.split_lines(raw_data)

        out_lines: list[bytes] = []
        changed = False
        for raw_line in raw_lines:
            new_line, line_changed = self.fix_line(raw_line)
            out_lines.append(new_line)
            changed = changed or line_changed

        self.stat.files_scanned += 1

        if not changed:
            return

        self.stat.files_changed += 1

        if self.dry_run:
            return

        out_data = b"".join(line + b"\n" for line in out_lines)

        fd, tmp_name = tempfile.mkstemp(
            dir=path.parent, prefix=f".{path.name}.", suffix=".tmp"
        )
        os.close(fd)
        tmp_path = pathlib.Path(tmp_name)
        try:
            tmp_path.write_bytes(out_data)
            tmp_path.replace(path)
        except BaseException:
            tmp_path.unlink(missing_ok=True)
            raise

    def main(self) -> FixIdStat:
        """全ファイルを走査して、結果を返す。"""
        files = self.find_files()

        if not files:
            self.__log.warning(
                f"{self.topdir}: no target file .. check --datadir"
            )

        for path in files:
            self.fix_file(path)

        if self.dry_run:
            print("===== dry run: 書き出していません =====")

        print(f"走査したファイル: {self.stat.files_scanned}")
        print(f"書き換えたファイル: {self.stat.files_changed}")
        print(f"書き換えた行    : {self.stat.lines_changed}")
        print(f"元から新形式の行: {self.stat.lines_already_ok}")
        print(f"読めなかった行  : {self.stat.lines_unreadable}")

        return self.stat

#
# (c) 2026 ytani01
#
"""ytsched.trash（ゴミ箱）のユニットテスト（TODO-085）"""

import datetime
import json
from typing import Any

from ytsched.sched_update import SchedUpdater
from ytsched.trash import TrashFile
from ytsched.ytsched import SchedData, SchedDataEnt

DATE1 = datetime.date(2021, 3, 1)


def mk_sde(**kwargs):
    """テスト用の SchedDataEnt を作る。"""
    param: dict[str, Any] = {
        "sde_id": "id-1",
        "date": DATE1,
        "time_start": datetime.time(9, 5),
        "time_end": datetime.time(10, 30),
        "sde_type": "予定",
        "title": "タイトル",
        "place": "場所",
        "detail": "詳細",
    }
    param.update(kwargs)
    return SchedDataEnt(**param)


def read_lines(pathname):
    return [
        json.loads(line)
        for line in pathname.read_text(encoding="utf-8").splitlines()
    ]


#
# TrashFile 単体
#
def test_add_appends_line(tmp_path):
    trash = TrashFile(tmp_path)
    sde = mk_sde()

    trash.add(sde)

    lines = read_lines(tmp_path / "trash.jsonl")
    assert len(lines) == 1
    entry = lines[0]
    assert list(entry.keys()) == [
        "trashed_at",
        "sde_id",
        "date",
        "time_start",
        "time_end",
        "type",
        "title",
        "place",
        "detail",
    ]
    # trashed_at 以外は to_dict() の内容と一致する
    entry_without_ts = {k: v for k, v in entry.items() if k != "trashed_at"}
    assert entry_without_ts == sde.to_dict()


def test_add_creates_parent_dir(tmp_path):
    topdir = tmp_path / "data"
    trash = TrashFile(topdir)

    trash.add(mk_sde())

    assert (topdir / "trash.jsonl").is_file()


def test_add_records_microseconds_to_distinguish_same_id(tmp_path):
    trash = TrashFile(tmp_path)
    sde = mk_sde()

    trash.add(sde)
    trash.add(sde)

    entries = read_lines(tmp_path / "trash.jsonl")
    assert all("." in entry["trashed_at"] for entry in entries)
    assert entries[0]["trashed_at"] != entries[1]["trashed_at"]


def test_expands_topdir(tmp_path, monkeypatch):
    """``~`` 付きの ``topdir`` でも展開してから使う。"""
    monkeypatch.setenv("HOME", str(tmp_path))

    trash = TrashFile("~/data")

    assert trash.pathname == tmp_path / "data" / "trash.jsonl"


def test_entries_filters_sorts_and_limits(tmp_path):
    path = tmp_path / "trash.jsonl"
    path.write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "trashed_at": "2026-08-30T10:00:00",
                        **mk_sde(sde_id="a").to_dict(),
                    },
                    ensure_ascii=False,
                ),
                json.dumps(
                    {
                        "trashed_at": "2026-08-30T12:00:00",
                        **mk_sde(sde_id="b").to_dict(),
                    },
                    ensure_ascii=False,
                ),
                json.dumps(
                    {
                        "trashed_at": "2026-08-30T11:00:00",
                        **mk_sde(sde_id="a").to_dict(),
                    },
                    ensure_ascii=False,
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    trash = TrashFile(tmp_path)

    assert [entry.trashed_at for entry in trash.entries()] == [
        "2026-08-30T12:00:00",
        "2026-08-30T11:00:00",
        "2026-08-30T10:00:00",
    ]
    assert [entry.trashed_at for entry in trash.entries("a", 1)] == [
        "2026-08-30T11:00:00"
    ]
    assert trash.get("a", "2026-08-30T10:00:00") is not None


#
# SchedData.del_sde() 経由（削除・編集の両方が通る）
#
def test_del_sde_adds_to_trash(tmp_path):
    """削除でゴミ箱に 1 行増える。"""
    sd = SchedData(str(tmp_path))
    sde = mk_sde()
    sd.add_sde(DATE1, sde)
    sd.save()

    sd.del_sde(DATE1, sde.sde_id)

    lines = read_lines(tmp_path / "trash.jsonl")
    assert len(lines) == 1
    assert lines[0]["sde_id"] == sde.sde_id
    assert lines[0]["title"] == "タイトル"


def test_del_sde_unknown_id_does_not_touch_trash(tmp_path):
    sd = SchedData(str(tmp_path))

    sd.del_sde(DATE1, "no-such-id")

    assert not (tmp_path / "trash.jsonl").exists()


def test_del_sde_twice_keeps_order(tmp_path):
    """2 回消すと 2 行になり、順序が保たれる。"""
    sd = SchedData(str(tmp_path))
    sde1 = mk_sde(sde_id="id-1", title="1件目")
    sde2 = mk_sde(sde_id="id-2", title="2件目")
    sd.add_sde(DATE1, sde1)
    sd.add_sde(DATE1, sde2)
    sd.save()

    sd.del_sde(DATE1, "id-1")
    sd.del_sde(DATE1, "id-2")

    lines = read_lines(tmp_path / "trash.jsonl")
    assert [line["sde_id"] for line in lines] == ["id-1", "id-2"]


def test_fix_puts_original_content_in_trash(tmp_path):
    """編集（fix）で編集前の内容がゴミ箱に入る。"""
    sd = SchedData(str(tmp_path))
    orig = mk_sde(title="編集前")
    sd.add_sde(DATE1, orig)
    sd.save()

    updater = SchedUpdater(sd)
    updater.cmd_del(DATE1, orig.sde_id)
    updater.cmd_add(
        orig.sde_id,
        DATE1,
        orig.time_start,
        orig.time_end,
        orig.type,
        "編集後",
        orig.place,
        orig.detail,
    )
    sd.save()

    lines = read_lines(tmp_path / "trash.jsonl")
    assert len(lines) == 1
    assert lines[0]["title"] == "編集前"

#
# (c) 2026 ytani01
#
"""ytsched.trash（ゴミ箱）のユニットテスト（TODO-085）"""

import datetime
import json
import stat
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
# TrashFile: 版を除いた UUID 部分での絞り込み（TODO-171）
#
UUID_A = "3f2a1b0c-4d5e-6f70-8192-a3b4c5d6e7f8"
UUID_B = "11111111-1111-1111-1111-111111111111"


def test_entries_filters_by_uuid_part_ignoring_version(tmp_path):
    path = tmp_path / "trash.jsonl"
    path.write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "trashed_at": "2026-08-30T10:00:00",
                        **mk_sde(sde_id=f"{UUID_A}-1").to_dict(),
                    },
                    ensure_ascii=False,
                ),
                json.dumps(
                    {
                        "trashed_at": "2026-08-30T11:00:00",
                        **mk_sde(sde_id=f"{UUID_A}-2").to_dict(),
                    },
                    ensure_ascii=False,
                ),
                json.dumps(
                    {
                        "trashed_at": "2026-08-30T12:00:00",
                        **mk_sde(sde_id=f"{UUID_B}-1").to_dict(),
                    },
                    ensure_ascii=False,
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    trash = TrashFile(tmp_path)

    # 版付きの ID で問い合わせても、版を除いた UUID 部分が同じ行が出る
    entries = trash.entries(f"{UUID_A}-1")
    assert [entry.sde.sde_id for entry in entries] == [
        f"{UUID_A}-2",
        f"{UUID_A}-1",
    ]

    # UUID 部分だけで問い合わせても同じ
    entries = trash.entries(UUID_A)
    assert len(entries) == 2


def test_get_requires_exact_id_match(tmp_path):
    path = tmp_path / "trash.jsonl"
    path.write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "trashed_at": "2026-08-30T10:00:00",
                        **mk_sde(sde_id=f"{UUID_A}-1").to_dict(),
                    },
                    ensure_ascii=False,
                ),
                json.dumps(
                    {
                        "trashed_at": "2026-08-30T11:00:00",
                        **mk_sde(sde_id=f"{UUID_A}-2").to_dict(),
                    },
                    ensure_ascii=False,
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    trash = TrashFile(tmp_path)

    # 版まで一致しないと取得できない
    assert trash.get(UUID_A, "2026-08-30T10:00:00") is None
    entry = trash.get(f"{UUID_A}-1", "2026-08-30T10:00:00")
    assert entry is not None
    assert entry.sde.sde_id == f"{UUID_A}-1"


def test_max_version_no_matching_lines_is_zero(tmp_path):
    trash = TrashFile(tmp_path)
    assert trash.max_version(UUID_A) == 0


def test_max_version_returns_highest_version(tmp_path):
    path = tmp_path / "trash.jsonl"
    path.write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "trashed_at": "2026-08-30T10:00:00",
                        **mk_sde(sde_id=f"{UUID_A}-1").to_dict(),
                    },
                    ensure_ascii=False,
                ),
                json.dumps(
                    {
                        "trashed_at": "2026-08-30T11:00:00",
                        **mk_sde(sde_id=f"{UUID_A}-3").to_dict(),
                    },
                    ensure_ascii=False,
                ),
                json.dumps(
                    {
                        "trashed_at": "2026-08-30T12:00:00",
                        **mk_sde(sde_id=f"{UUID_B}-5").to_dict(),
                    },
                    ensure_ascii=False,
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    trash = TrashFile(tmp_path)

    assert trash.max_version(UUID_A) == 3
    assert trash.max_version(UUID_B) == 5


def test_count_no_file_is_zero(tmp_path):
    trash = TrashFile(tmp_path)

    assert trash.count() == 0


def test_count_counts_entries(tmp_path):
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
                        "trashed_at": "2026-08-30T11:00:00",
                        **mk_sde(sde_id="b").to_dict(),
                    },
                    ensure_ascii=False,
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    trash = TrashFile(tmp_path)

    assert trash.count() == 2


def test_count_ignores_broken_lines(tmp_path):
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
                "{ this is not valid json",
                json.dumps({"sde_id": "b"}, ensure_ascii=False),
                json.dumps(
                    {"trashed_at": 12345, "sde_id": "c"}, ensure_ascii=False
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    trash = TrashFile(tmp_path)

    assert trash.count() == 1


def test_count_exceeds_entries_max(tmp_path):
    path = tmp_path / "trash.jsonl"
    lines = [
        json.dumps(
            {
                "trashed_at": f"2026-08-30T10:00:{i:02d}",
                **mk_sde(sde_id=f"id-{i}").to_dict(),
            },
            ensure_ascii=False,
        )
        for i in range(120)
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    trash = TrashFile(tmp_path)

    assert len(trash.entries()) == 100
    assert trash.count() == 120


def test_delete_many_keeps_unselected_and_broken_lines(tmp_path):
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
                "{ this is not valid json",
                json.dumps(
                    {
                        "sde_id": ["壊れた ID"],
                        "trashed_at": "2026-08-30T10:00:00",
                    },
                    ensure_ascii=False,
                ),
                json.dumps(
                    {
                        "sde_id": "a",
                        "trashed_at": "2026-08-30T10:00:00",
                        "title": "日付が無い壊れた行",
                    },
                    ensure_ascii=False,
                ),
                json.dumps(
                    {
                        "trashed_at": "2026-08-30T11:00:00",
                        **mk_sde(sde_id="b").to_dict(),
                    },
                    ensure_ascii=False,
                ),
                json.dumps(
                    {
                        "trashed_at": "2026-08-30T10:00:00",
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

    deleted = trash.delete_many({("a", "2026-08-30T10:00:00")})

    assert deleted == 2
    remaining = path.read_text(encoding="utf-8").splitlines()
    assert len(remaining) == 4
    assert "not valid json" in remaining[0]
    assert json.loads(remaining[1])["sde_id"] == ["壊れた ID"]
    assert json.loads(remaining[2])["title"] == "日付が無い壊れた行"
    assert json.loads(remaining[3])["sde_id"] == "b"


def test_delete_unknown_trashed_at_returns_false(tmp_path):
    path = tmp_path / "trash.jsonl"
    path.write_text(
        json.dumps(
            {
                "trashed_at": "2026-08-30T10:00:00",
                **mk_sde(sde_id="a").to_dict(),
            },
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    trash = TrashFile(tmp_path)

    assert trash.delete("a", "no-such-timestamp") is False
    # 書き直されず内容もそのまま
    assert path.read_text(encoding="utf-8").count("\n") == 1


def test_delete_keeps_original_permissions(tmp_path):
    """書き直しの前後でパーミッションが変わらない（0600 に落ちない）。"""
    path = tmp_path / "trash.jsonl"
    path.write_text(
        json.dumps(
            {
                "trashed_at": "2026-08-30T10:00:00",
                **mk_sde(sde_id="a").to_dict(),
            },
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    path.chmod(0o644)
    trash = TrashFile(tmp_path)

    trash.delete("a", "2026-08-30T10:00:00")

    assert stat.S_IMODE(path.stat().st_mode) == 0o644


def test_delete_no_file_returns_false(tmp_path):
    trash = TrashFile(tmp_path)

    assert trash.delete("a", "2026-08-30T10:00:00") is False


def test_delete_many_empty_or_unknown_does_not_rewrite(tmp_path):
    trash = TrashFile(tmp_path)
    trash.add(mk_sde())
    path = tmp_path / "trash.jsonl"
    before = path.read_bytes()

    assert trash.delete_many(set()) == 0
    assert trash.delete_many({("unknown", "2026-08-30T10:00:00")}) == 0
    assert path.read_bytes() == before


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

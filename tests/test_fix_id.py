#
# (c) 2026 ytani01
#
"""``sde_id`` を UUID へ振り直すツールのテスト (TODO-170)"""

import datetime
import json
import re
import time

import click.testing
import pytest

from ytsched.__main__ import cli
from ytsched.fix_id import UUID_PATTERN, IdFixer, is_uuid
from ytsched.ytsched import SchedDataFile

UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
)

OLD_ID = "abc123def456"
OLD_UUID = "11111111-1111-1111-1111-111111111111"


def write_jsonl(path, lines):
    """行(str のリスト)をそのまま ``\\n`` で連結して書く。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(("\n".join(lines) + "\n").encode("utf-8"))


def read_lines(path):
    """ファイルを行(bytes のリスト)に分けて返す(末尾の空要素は除く)。"""
    data = path.read_bytes()
    return SchedDataFile.split_lines(data)


@pytest.fixture
def datadir(tmp_path):
    return tmp_path / "data"


def mk_daily(datadir, y="2026", m="01", d="02"):
    return datadir / y / m / f"{d}.jsonl"


def test_is_uuid():
    assert is_uuid(OLD_UUID)
    assert not is_uuid(OLD_ID)
    assert not is_uuid("{11111111-1111-1111-1111-111111111111}")
    assert not is_uuid("11111111111111111111111111111111")


def test_uuid_pattern_matches_helper():
    assert UUID_PATTERN.match(OLD_UUID)


def test_fix_replaces_non_uuid_id(datadir):
    path = mk_daily(datadir)
    write_jsonl(
        path,
        [
            json.dumps(
                {
                    "sde_id": OLD_ID,
                    "date": "2026-01-02",
                    "title": "a",
                    "detail": "d",
                },
                ensure_ascii=False,
            )
        ],
    )

    stat = IdFixer(str(datadir)).main()

    assert stat.files_scanned == 1
    assert stat.files_changed == 1
    assert stat.lines_changed == 1
    assert stat.lines_already_uuid == 0
    assert stat.lines_unreadable == 0

    lines = read_lines(path)
    assert len(lines) == 1
    data = json.loads(lines[0])
    assert data["sde_id"] != OLD_ID
    assert UUID_RE.match(data["sde_id"])


def test_already_uuid_line_unchanged(datadir):
    path = mk_daily(datadir)
    original = json.dumps(
        {"sde_id": OLD_UUID, "date": "2026-01-02", "title": "a"},
        ensure_ascii=False,
    )
    write_jsonl(path, [original])

    stat = IdFixer(str(datadir)).main()

    assert stat.files_changed == 0
    assert stat.lines_changed == 0
    assert stat.lines_already_uuid == 1

    lines = read_lines(path)
    assert lines[0].decode("utf-8") == original


def test_other_keys_values_and_order_unchanged(datadir):
    path = mk_daily(datadir)
    write_jsonl(
        path,
        [
            json.dumps(
                {
                    "sde_id": OLD_ID,
                    "date": "2026-01-02",
                    "time_start": "10:00",
                    "time_end": None,
                    "type": "会議",
                    "title": "打ち合わせ",
                    "place": "会議室",
                    "detail": "詳細",
                },
                ensure_ascii=False,
            )
        ],
    )

    IdFixer(str(datadir)).main()

    lines = read_lines(path)
    data = json.loads(lines[0])
    keys = list(data.keys())
    assert keys == [
        "sde_id",
        "date",
        "time_start",
        "time_end",
        "type",
        "title",
        "place",
        "detail",
    ]
    assert data["date"] == "2026-01-02"
    assert data["time_start"] == "10:00"
    assert data["time_end"] is None
    assert data["type"] == "会議"
    assert data["title"] == "打ち合わせ"
    assert data["place"] == "会議室"
    assert data["detail"] == "詳細"


def test_duplicate_old_ids_become_distinct_uuids(datadir):
    path = mk_daily(datadir)
    write_jsonl(
        path,
        [
            json.dumps(
                {"sde_id": OLD_ID, "date": "2026-01-02", "title": "a"},
                ensure_ascii=False,
            ),
            json.dumps(
                {"sde_id": OLD_ID, "date": "2026-01-02", "title": "b"},
                ensure_ascii=False,
            ),
        ],
    )

    stat = IdFixer(str(datadir)).main()
    assert stat.lines_changed == 2

    lines = read_lines(path)
    ids = [json.loads(line)["sde_id"] for line in lines]
    assert len(set(ids)) == 2
    for sde_id in ids:
        assert UUID_RE.match(sde_id)


def test_unreadable_lines_are_kept(datadir):
    path = mk_daily(datadir)
    write_jsonl(
        path,
        [
            "not json at all",
            json.dumps({"date": "2026-01-02", "title": "no id"}),
            json.dumps({"sde_id": 123, "title": "not a string"}),
            json.dumps(
                {"sde_id": OLD_ID, "date": "2026-01-02", "title": "ok"}
            ),
        ],
    )

    stat = IdFixer(str(datadir)).main()

    assert stat.lines_unreadable == 3
    assert stat.lines_changed == 1

    lines = read_lines(path)
    assert lines[0] == b"not json at all"
    assert json.loads(lines[1]) == {"date": "2026-01-02", "title": "no id"}
    assert json.loads(lines[2]) == {"sde_id": 123, "title": "not a string"}


def test_missing_trailing_newline_is_added(datadir):
    path = mk_daily(datadir)
    path.parent.mkdir(parents=True, exist_ok=True)
    original = json.dumps(
        {"sde_id": OLD_ID, "date": "2026-01-02", "title": "a"},
        ensure_ascii=False,
    ).encode("utf-8")
    path.write_bytes(original)  # 末尾に改行を付けない

    stat = IdFixer(str(datadir)).main()

    assert stat.lines_changed == 1
    assert path.read_bytes().endswith(b"\n")
    lines = read_lines(path)
    assert len(lines) == 1
    data = json.loads(lines[0])
    assert UUID_RE.match(data["sde_id"])


def test_empty_file(datadir):
    path = mk_daily(datadir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"")

    stat = IdFixer(str(datadir)).main()

    assert stat.files_scanned == 1
    assert stat.files_changed == 0
    assert stat.lines_unreadable == 0
    assert path.read_bytes() == b""


def test_blank_line_in_body_not_counted_as_unreadable(datadir):
    path = mk_daily(datadir)
    write_jsonl(
        path,
        [
            json.dumps(
                {"sde_id": OLD_ID, "date": "2026-01-02", "title": "a"},
                ensure_ascii=False,
            ),
            "",
            json.dumps(
                {"sde_id": OLD_UUID, "date": "2026-01-02", "title": "b"},
                ensure_ascii=False,
            ),
        ],
    )

    stat = IdFixer(str(datadir)).main()

    assert stat.lines_unreadable == 0
    assert stat.lines_changed == 1
    assert stat.lines_already_uuid == 1

    lines = read_lines(path)
    assert len(lines) == 3
    assert lines[1] == b""


def test_only_last_line_unreadable(datadir):
    path = mk_daily(datadir)
    write_jsonl(
        path,
        [
            json.dumps(
                {"sde_id": OLD_ID, "date": "2026-01-02", "title": "a"},
                ensure_ascii=False,
            ),
            "not json at all",
        ],
    )

    stat = IdFixer(str(datadir)).main()

    assert stat.lines_changed == 1
    assert stat.lines_unreadable == 1

    lines = read_lines(path)
    assert len(lines) == 2
    data = json.loads(lines[0])
    assert UUID_RE.match(data["sde_id"])
    assert lines[1] == b"not json at all"


def test_trash_file_not_touched(datadir):
    trash_path = datadir / "trash.jsonl"
    write_jsonl(
        trash_path,
        [
            json.dumps(
                {"sde_id": OLD_ID, "date": "2026-01-02", "title": "a"},
                ensure_ascii=False,
            )
        ],
    )
    original = trash_path.read_bytes()

    IdFixer(str(datadir)).main()

    assert trash_path.read_bytes() == original


def test_dry_run_does_not_write(datadir):
    path = mk_daily(datadir)
    write_jsonl(
        path,
        [
            json.dumps(
                {"sde_id": OLD_ID, "date": "2026-01-02", "title": "a"},
                ensure_ascii=False,
            )
        ],
    )
    original = path.read_bytes()

    stat = IdFixer(str(datadir), dry_run=True).main()

    assert stat.lines_changed == 1
    assert path.read_bytes() == original


def test_unchanged_file_mtime_not_touched(datadir):
    path = mk_daily(datadir)
    original = json.dumps(
        {"sde_id": OLD_UUID, "date": "2026-01-02", "title": "a"},
        ensure_ascii=False,
    )
    write_jsonl(path, [original])
    mtime_before = path.stat().st_mtime_ns

    time.sleep(0.01)
    IdFixer(str(datadir)).main()

    assert path.stat().st_mtime_ns == mtime_before


def test_fixed_file_readable_by_scheddatafile(datadir):
    path = mk_daily(datadir, y="2026", m="03", d="04")
    write_jsonl(
        path,
        [
            json.dumps(
                {
                    "sde_id": OLD_ID,
                    "date": "2026-03-04",
                    "title": "a",
                    "type": "",
                    "place": "",
                    "detail": "",
                    "time_start": None,
                    "time_end": None,
                },
                ensure_ascii=False,
            )
        ],
    )

    IdFixer(str(datadir)).main()

    sdf = SchedDataFile(date=datetime.date(2026, 3, 4), topdir=str(datadir))
    assert len(sdf.sde) == 1
    assert UUID_RE.match(sdf.sde[0].sde_id)
    assert not sdf.skipped_lines


def test_cli_fix_id_dry_run(datadir):
    path = mk_daily(datadir)
    write_jsonl(
        path,
        [
            json.dumps(
                {"sde_id": OLD_ID, "date": "2026-01-02", "title": "a"},
                ensure_ascii=False,
            )
        ],
    )
    original = path.read_bytes()

    runner = click.testing.CliRunner()
    result = runner.invoke(
        cli, ["fix-id", "--datadir", str(datadir), "--dry-run"]
    )

    assert result.exit_code == 0
    assert path.read_bytes() == original
    assert "書き換えた行" in result.output


def test_cli_fix_id_writes(datadir):
    path = mk_daily(datadir)
    write_jsonl(
        path,
        [
            json.dumps(
                {"sde_id": OLD_ID, "date": "2026-01-02", "title": "a"},
                ensure_ascii=False,
            )
        ],
    )

    runner = click.testing.CliRunner()
    result = runner.invoke(cli, ["fix-id", "--datadir", str(datadir)])

    assert result.exit_code == 0
    lines = read_lines(path)
    data = json.loads(lines[0])
    assert UUID_RE.match(data["sde_id"])

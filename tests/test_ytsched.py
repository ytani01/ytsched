#
# (c) 2026 ytani01
#
"""ytsched.ytsched のユニットテスト"""

import datetime
import inspect
import json
import uuid
from typing import Any
from unittest import mock

import pytest
from helpers import run_in_c_locale

from ytsched.ytsched import (
    SchedData,
    SchedDataEnt,
    SchedDataFile,
    normalize,
)

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


#
# normalize()
#
@pytest.mark.parametrize(
    ("intext", "expected"),
    [
        ("（かっこ）", "(かっこ)"),
        ("(かっこ)", "(かっこ)"),
        ("ABC", "abc"),
        ("（重要）打合せ", "(重要)打合せ"),
        ("", ""),
    ],
)
def test_normalize(intext, expected):
    assert normalize(intext) == expected


@pytest.mark.parametrize("intext", ["㍿", "①", "ｱ", "Ａ"])
def test_normalize_is_not_nfkc(intext):
    """NFKC のような広い正規化はしない（TODO-018）。"""
    assert normalize(intext) == intext.lower()


def test_normalize_keeps_html_and_newline():
    """タグや改行はそのまま（読み込み時の置換はもう無い）。"""
    assert normalize("a<br />b\n&nbsp;") == "a<br />b\n&nbsp;"


#
# SchedDataEnt
#
def test_sde_init_detail_is_kept():
    """``detail`` は入力されたまま持つ（変換しない）。"""
    sde = mk_sde(detail="a<br />b")
    assert sde.detail == "a<br />b"


def test_sde_init_detail_keeps_newline():
    sde = mk_sde(detail="a\nb")
    assert sde.detail == "a\nb"


def test_sde_init_empty_title():
    sde = mk_sde(title="")
    assert sde.title == SchedDataEnt.TITLE_NULL


def test_sde_init_id_is_generated():
    sde = mk_sde(sde_id=None)
    assert sde.sde_id


def test_new_id_is_unique():
    ids = [SchedDataEnt.new_id() for _ in range(100)]
    assert len(set(ids)) == len(ids)


def test_new_id_is_uuid():
    """``sde_id`` は uuid4。"""
    sde_id = SchedDataEnt.new_id()
    assert str(uuid.UUID(sde_id)) == sde_id
    assert uuid.UUID(sde_id).version == 4


def test_new_id_has_no_tab_and_no_dot():
    sde_id = SchedDataEnt.new_id()
    assert "\t" not in sde_id
    assert "." not in sde_id


def test_sde_str():
    sde = mk_sde()
    assert str(sde) == (
        "(id-1) 2021/03/01 09:05-10:30 [予定]タイトル@場所: 詳細"
    )


def test_sde_str_no_time():
    sde = mk_sde(time_start=None, time_end=None)
    assert str(sde) == "(id-1) 2021/03/01 :-: [予定]タイトル@場所: 詳細"


def test_mk_dataline():
    sde = mk_sde(detail="a\nb")
    assert json.loads(sde.mk_dataline()) == {
        "sde_id": "id-1",
        "date": "2021-03-01",
        "time_start": "09:05",
        "time_end": "10:30",
        "type": "予定",
        "title": "タイトル",
        "place": "場所",
        "detail": "a\nb",
    }


def test_mk_dataline_key_order():
    """キーの並びは docs/data-format.md の順（書くときは全部出す）。"""
    keys = list(json.loads(mk_sde().mk_dataline(), object_pairs_hook=list))
    assert [k for k, _ in keys] == [
        "sde_id",
        "date",
        "time_start",
        "time_end",
        "type",
        "title",
        "place",
        "detail",
    ]


def test_mk_dataline_is_one_line():
    """改行・タブ・U+2028 を含んでも 1 行になる。"""
    sde = mk_sde(detail="a\nb\tc\u2028d")
    dataline = sde.mk_dataline()

    assert "\n" not in dataline
    assert dataline.encode("utf-8").count(b"\n") == 0
    assert json.loads(dataline)["detail"] == "a\nb\tc\u2028d"


def test_mk_dataline_is_not_ascii_escaped():
    """日本語はエスケープせずそのまま書く。"""
    assert "タイトル" in mk_sde().mk_dataline()


def test_mk_dataline_no_time():
    sde = mk_sde(time_start=None, time_end=None)
    data = json.loads(sde.mk_dataline())
    assert data["time_start"] is None
    assert data["time_end"] is None


def test_to_dict_and_from_dict():
    sde = mk_sde(detail="a\nb")
    sde2 = SchedDataEnt.from_dict(sde.to_dict())

    assert sde2.to_dict() == sde.to_dict()


@pytest.mark.parametrize(
    "key", ["time_start", "time_end", "type", "title", "place", "detail"]
)
def test_from_dict_missing_key(key):
    """``date`` 以外のキーは欠けていてもよい。"""
    data = mk_sde().to_dict()
    del data[key]

    sde = SchedDataEnt.from_dict(data)

    if key in ("time_start", "time_end"):
        assert getattr(sde, key) is None
    else:
        assert getattr(sde, key) == ""


def test_from_dict_missing_sde_id():
    """``sde_id`` が欠けていたら、新しい ID を発行する。"""
    data = mk_sde().to_dict()
    del data["sde_id"]

    assert SchedDataEnt.from_dict(data).sde_id


@pytest.mark.parametrize(
    "date_value", [None, "", "2021/03/01", "xxx", 20210301]
)
def test_from_dict_invalid_date(date_value):
    data = mk_sde().to_dict()
    data["date"] = date_value

    with pytest.raises(ValueError, match=r".*"):
        SchedDataEnt.from_dict(data)


def test_from_dict_no_date():
    data = mk_sde().to_dict()
    del data["date"]

    with pytest.raises(ValueError, match=r".*"):
        SchedDataEnt.from_dict(data)


def test_from_dict_invalid_time_is_ignored():
    """時刻として読めない値は None にする（行は捨てない）。"""
    data = mk_sde().to_dict()
    data["time_start"] = "25:00"

    assert SchedDataEnt.from_dict(data).time_start is None


def test_search_str():
    sde = mk_sde(title="Title", detail="a\nb")
    assert sde.search_str() == "#予定 +title @場所 detail:a b"


def test_search_str_is_normalized():
    """照合対象では全角括弧が半角になる（保存する文字列は変えない）。"""
    sde = mk_sde(title="（重要）打合せ")

    assert "(重要)打合せ" in sde.search_str()
    assert sde.title == "（重要）打合せ"


@pytest.mark.parametrize(
    ("t_start", "t_end", "expected"),
    [
        (datetime.time(9, 5), datetime.time(10, 30), "09:05-10:30"),
        (datetime.time(9, 5), None, "09:05-:"),
        (None, datetime.time(10, 30), ":-10:30"),
        (None, None, ":-:"),
    ],
)
def test_get_timestr(t_start, t_end, expected):
    sde = mk_sde(time_start=t_start, time_end=t_end)
    assert sde.get_timestr() == expected


def test_get_sortkey_with_time():
    sde = mk_sde()
    assert sde.get_sortkey() == "20210301 09:05-10:30"


def test_get_sortkey_holiday():
    sde = mk_sde(sde_type="休日", time_start=None, time_end=None)
    assert sde.get_sortkey() == "20210301   :  -  :  "


def test_get_sortkey_paren_title():
    sde = mk_sde(title="(中止)会議", time_start=None, time_end=None)
    assert sde.get_sortkey() == "20210301 99:99-99:99"


def test_get_sortkey_other():
    sde = mk_sde(time_start=None, time_end=None)
    assert sde.get_sortkey() == "20210301 33:33-33:33"


def test_get_sortkey_order():
    """休日が先頭、``(`` 始まりが最後に並ぶ。"""
    holiday = mk_sde(sde_type="休日", time_start=None, time_end=None)
    timed = mk_sde(time_start=datetime.time(9, 5), time_end=None)
    other = mk_sde(time_start=None, time_end=None)
    canceled = mk_sde(title="(中止)会議", time_start=None, time_end=None)

    sde_list = sorted(
        [other, canceled, timed, holiday], key=lambda x: x.get_sortkey()
    )
    assert sde_list == [holiday, timed, other, canceled]


def test_get_date():
    assert mk_sde().get_date() == (2021, 3, 1)


def test_set_date():
    sde = mk_sde()
    sde.set_date(datetime.date(2022, 12, 31))
    assert sde.date == datetime.date(2022, 12, 31)


def test_set_date_none_is_today():
    sde = mk_sde()
    sde.set_date(None)
    assert sde.date == datetime.date.today()


@pytest.mark.parametrize(
    ("sde_type", "expected"),
    [
        ("□買い物", True),
        ("□", True),
        ("予定", False),
        ("", False),
    ],
)
def test_is_todo(sde_type, expected):
    assert mk_sde(sde_type=sde_type).is_todo() is expected


@pytest.mark.parametrize(
    ("sde_type", "expected"),
    [
        ("□買い物", True),
        ("予定", False),
        ("", False),
    ],
)
def test_type_is_todo(sde_type, expected):
    assert SchedDataEnt.type_is_todo(sde_type) is expected


def test_type_is_todo_none():
    assert SchedDataEnt.type_is_todo(None) is False


@pytest.mark.parametrize(
    ("sde_type", "expected"),
    [
        ("休日", True),
        ("祝日", True),
        ("予定", False),
        ("", False),
    ],
)
def test_is_holiday(sde_type, expected):
    assert mk_sde(sde_type=sde_type).is_holiday() is expected


@pytest.mark.parametrize(
    ("title", "expected"),
    [
        ("(重要)会議", True),
        ("!会議", True),
        ("！会議", True),
        ("★会議", True),
        ("☆会議", True),
        ("会議", False),
        ("", False),
    ],
)
def test_is_important(title, expected):
    assert mk_sde(title=title).is_important() is expected


@pytest.mark.parametrize(
    ("title", "expected"),
    [
        ("(キャンセル)会議", True),
        ("(欠席)会議", True),
        ("(中止)会議", True),
        ("(休み)", True),
        ("(無効)", True),
        ("(不要)", True),
        ("x会議", True),
        ("X会議", True),
        ("会議", False),
        ("", False),
    ],
)
def test_is_canceled(title, expected):
    assert mk_sde(title=title).is_canceled() is expected


@pytest.mark.parametrize(
    ("title", "expected"),
    [
        ("（重要）会議", True),
        ("(重要)会議", True),
        ("（重要 会議", False),
    ],
)
def test_is_important_zenkaku(title, expected):
    """全角括弧でも「重要」と判定される（TODO-020）。"""
    assert mk_sde(title=title).is_important() is expected


@pytest.mark.parametrize(
    ("title", "expected"),
    [
        ("（中止）会議", True),
        ("（キャンセル）会議", True),
        ("(中止)会議", True),
    ],
)
def test_is_canceled_zenkaku(title, expected):
    """全角括弧でも「取り消し」と判定される（TODO-020）。"""
    assert mk_sde(title=title).is_canceled() is expected


def test_get_sortkey_zenkaku_paren_title():
    """並べ替えのキーも、全角括弧で同じに効く。"""
    sde = mk_sde(title="（中止）会議", time_start=None, time_end=None)
    assert sde.get_sortkey() == "20210301 99:99-99:99"


def test_title_is_not_modified():
    """保存する文字列は入力されたまま（判定のときだけ揃える）。"""
    sde = mk_sde(title="（重要）打合せ")

    assert sde.is_important() is True
    assert sde.title == "（重要）打合せ"
    assert json.loads(sde.mk_dataline())["title"] == "（重要）打合せ"


def test_sde_init_date_default_is_not_fixed():
    """``date`` の既定値が import 時の日付に固定されていない。"""
    default = (
        inspect.signature(SchedDataEnt.__init__).parameters["date"].default
    )
    assert not isinstance(default, datetime.date)


def test_sde_init_date_none_is_today():
    """``date=None`` は今日の日付になる。"""
    assert mk_sde(date=None).date == datetime.date.today()


#
# SchedDataFile
#
def test_date2path(tmp_path):
    sdf = SchedDataFile(DATE1, topdir=str(tmp_path))
    assert sdf.pathname == f"{tmp_path}/2021/03/01.jsonl"
    assert sdf.dirname == f"{tmp_path}/2021/03"
    assert sdf.filename == "01.jsonl"


def test_date2path_todo(tmp_path):
    sdf = SchedDataFile(None, topdir=str(tmp_path))
    assert sdf.pathname == f"{tmp_path}/ToDo.jsonl"


def test_topdir_is_expanded():
    sdf = SchedDataFile(DATE1, topdir="~/no_such_dir")
    assert not sdf.topdir.startswith("~")


def test_date2path_expands_topdir(tmp_path, monkeypatch):
    """``date2path()`` を単独で呼んでも ``~`` は展開される (TODO-034)。"""
    monkeypatch.setenv("HOME", str(tmp_path))

    pathname = SchedDataFile.date2path(DATE1, "~/data")

    assert pathname == f"{tmp_path}/data/2021/03/01.jsonl"


def test_date2path_todo_expands_topdir(tmp_path, monkeypatch):
    """ToDo のパスでも同じ (TODO-034)。"""
    monkeypatch.setenv("HOME", str(tmp_path))

    assert (
        SchedDataFile.date2path(None, "~/data")
        == f"{tmp_path}/data/ToDo.jsonl"
    )


def test_load_no_file(tmp_path):
    sdf = SchedDataFile(DATE1, topdir=str(tmp_path))
    assert sdf.sde == []
    assert sdf.is_holiday is False


def write_data(tmp_path, date, lines, encoding="utf-8"):
    """データファイルを書いて、パスを返す。"""
    path = tmp_path / date.strftime("%Y") / date.strftime("%m")
    path.mkdir(parents=True, exist_ok=True)
    path = path / (date.strftime("%d") + ".jsonl")
    path.write_text("".join(l + "\n" for l in lines), encoding=encoding)
    return path


def mk_dataline(**kwargs):
    """テスト用の 1 行（JSON Lines）を作る。"""
    data = {
        "sde_id": "id-1",
        "date": "2021-03-01",
        "time_start": "09:05",
        "time_end": "10:30",
        "type": "予定",
        "title": "タイトル",
        "place": "場所",
        "detail": "a\nb",
    }
    data.update(kwargs)
    return json.dumps(data, ensure_ascii=False)


DATALINE1 = mk_dataline()
DATALINE2 = mk_dataline(
    sde_id="id-2",
    time_start=None,
    time_end=None,
    type="休日",
    title="振替休日",
    place="",
    detail="",
)


def test_load(tmp_path):
    write_data(tmp_path, DATE1, [DATALINE1])

    sdf = SchedDataFile(DATE1, topdir=str(tmp_path))

    assert len(sdf.sde) == 1
    sde = sdf.sde[0]
    assert sde.sde_id == "id-1"
    assert sde.date == DATE1
    assert sde.time_start == datetime.time(9, 5)
    assert sde.time_end == datetime.time(10, 30)
    assert sde.type == "予定"
    assert sde.title == "タイトル"
    assert sde.place == "場所"
    assert sde.detail == "a\nb"


def test_load_no_time(tmp_path):
    write_data(tmp_path, DATE1, [DATALINE2])

    sde = SchedDataFile(DATE1, topdir=str(tmp_path)).sde[0]

    assert not sde.time_start
    assert not sde.time_end


def test_load_holiday(tmp_path):
    write_data(tmp_path, DATE1, [DATALINE1, DATALINE2])

    sdf = SchedDataFile(DATE1, topdir=str(tmp_path))

    assert sdf.is_holiday is True


def test_load_not_holiday(tmp_path):
    write_data(tmp_path, DATE1, [DATALINE1])

    sdf = SchedDataFile(DATE1, topdir=str(tmp_path))

    assert sdf.is_holiday is False


def test_load_is_sorted(tmp_path):
    """読み込み後は ``get_sortkey()`` 順に並ぶ。"""
    write_data(tmp_path, DATE1, [DATALINE1, DATALINE2])

    sdf = SchedDataFile(DATE1, topdir=str(tmp_path))

    assert [sde.sde_id for sde in sdf.sde] == ["id-2", "id-1"]


def test_load_missing_keys(tmp_path):
    """``date`` 以外のキーが欠けていても読める。"""
    write_data(tmp_path, DATE1, [json.dumps({"date": "2021-03-01"})])

    sde = SchedDataFile(DATE1, topdir=str(tmp_path)).sde[0]

    assert sde.sde_id
    assert sde.time_start is None
    assert sde.time_end is None
    assert sde.type == ""
    assert sde.title == ""
    assert sde.place == ""
    assert sde.detail == ""


def test_load_keeps_newline_and_u2028(tmp_path):
    """``detail`` の改行と U+2028 が、そのまま往復する。"""
    detail = "1 行目\n2 行目\u20283 行目"
    write_data(tmp_path, DATE1, [mk_dataline(detail=detail)])

    sdf = SchedDataFile(DATE1, topdir=str(tmp_path))

    assert len(sdf.sde) == 1
    assert sdf.sde[0].detail == detail


def test_load_is_utf8_only(tmp_path):
    """euc_jp のファイルは読めない（その行を飛ばす）。"""
    write_data(tmp_path, DATE1, [DATALINE1], encoding="euc_jp")

    assert SchedDataFile(DATE1, topdir=str(tmp_path)).sde == []


#
# 壊れた行（その行だけ飛ばし、ファイル全体は捨てない）
#
@pytest.mark.parametrize(
    ("bad_line", "reason"),
    [
        ("", "空行"),
        ("[1, 2, 3]", "オブジェクトでない"),
        ("123", "オブジェクトでない"),
        ("{" + '"date": "2021-03-01"', "JSON として読めない"),
        (json.dumps({"sde_id": "id-x"}), "date が無い"),
        (json.dumps({"sde_id": "id-x", "date": "2021/03/01"}), "date が変"),
    ],
)
def test_load_broken_line_is_skipped(tmp_path, bad_line, reason):
    """壊れた行だけが飛ばされ、同じファイルの他の行は読める。"""
    write_data(tmp_path, DATE1, [DATALINE1, bad_line, DATALINE2])

    sdf = SchedDataFile(DATE1, topdir=str(tmp_path))

    assert [sde.sde_id for sde in sdf.sde] == ["id-2", "id-1"], reason


def test_load_broken_encoding_line_is_skipped(tmp_path):
    """utf-8 でデコードできない行だけが飛ばされる。"""
    path = write_data(tmp_path, DATE1, [DATALINE1, DATALINE2])
    with open(path, mode="ab") as f:
        f.write(
            b'{"sde_id": "id-x", "date": "2021-03-01",'
            b' "title": "\xb2\xf1\xb5\xc4"}\n'
        )

    sdf = SchedDataFile(DATE1, topdir=str(tmp_path))

    assert [sde.sde_id for sde in sdf.sde] == ["id-2", "id-1"]


def test_load_broken_line_warns(tmp_path):
    """飛ばしたら警告を出す。"""
    write_data(tmp_path, DATE1, [DATALINE1, "{"])

    with mock.patch.object(SchedDataFile, "_SchedDataFile__log") as log:
        SchedDataFile(DATE1, topdir=str(tmp_path))

    assert log.warning.called


def test_load_date_mismatch_uses_line_date(tmp_path):
    """ファイル名と行の ``date`` が食い違ったら、行の ``date`` を使う。"""
    write_data(tmp_path, DATE1, [mk_dataline(date="2021-03-02")])

    with mock.patch.object(SchedDataFile, "_SchedDataFile__log") as log:
        sdf = SchedDataFile(DATE1, topdir=str(tmp_path))

    assert sdf.sde[0].date == datetime.date(2021, 3, 2)
    assert log.warning.called


def test_load_todo_date_is_not_checked(tmp_path):
    """ToDo のファイルでは、日付の食い違いを確かめない。"""
    (tmp_path / "ToDo.jsonl").write_text(
        mk_dataline(type="□買い物") + "\n", encoding="utf-8"
    )

    with mock.patch.object(SchedDataFile, "_SchedDataFile__log") as log:
        sdf = SchedDataFile(None, topdir=str(tmp_path))

    assert len(sdf.sde) == 1
    assert not log.warning.called


def test_load_trailing_newline_is_not_a_broken_line(tmp_path):
    """行末の改行だけでは、警告を出さない。"""
    write_data(tmp_path, DATE1, [DATALINE1])

    with mock.patch.object(SchedDataFile, "_SchedDataFile__log") as log:
        SchedDataFile(DATE1, topdir=str(tmp_path))

    assert not log.warning.called


def test_load_empty_file(tmp_path):
    """空のファイルは 0 件（警告も出さない）。"""
    write_data(tmp_path, DATE1, [])

    with mock.patch.object(SchedDataFile, "_SchedDataFile__log") as log:
        sdf = SchedDataFile(DATE1, topdir=str(tmp_path))

    assert sdf.sde == []
    assert not log.warning.called


def test_load_broken_line_is_written_back(tmp_path):
    """飛ばした行は、保存し直すと末尾へ書き戻される（TODO-020）。"""
    path = write_data(tmp_path, DATE1, [DATALINE1, "{"])

    sdf = SchedDataFile(DATE1, topdir=str(tmp_path))
    sdf.save()

    lines = path.read_bytes().rstrip(b"\n").split(b"\n")
    assert lines[-1] == b"{"
    assert json.loads(lines[0])["sde_id"] == "id-1"


def test_load_broken_line_survives_two_saves(tmp_path):
    """保存を 2 回しても、壊れた行は消えない。

    旧形式では、読めない行があるファイルに追加して 2 回保存すると、
    元のデータが本体からも ``.bak`` からも消えた。
    """
    path = write_data(tmp_path, DATE1, [DATALINE1, "{"])

    for i in range(2):
        sdf = SchedDataFile(DATE1, topdir=str(tmp_path))
        sdf.add_sde(mk_sde(sde_id=f"id-add{i}"))
        sdf.save()

    lines = path.read_bytes().rstrip(b"\n").split(b"\n")
    assert lines[-1] == b"{"
    assert len(lines) == 4

    backup = path.parent / (path.name + SchedDataFile.BACKUP_EXT)
    assert b"{\n" in backup.read_bytes()


#: 書き戻される 4 種類
BROKEN_RAW_LINES = [
    pytest.param("会議".encode("euc_jp"), id="cannot-decode"),
    pytest.param(b'{"date": ', id="not-json"),
    pytest.param(b"[1, 2, 3]", id="not-object"),
    pytest.param(b'{"sde_id": "id-x"}', id="no-date"),
]

#: 書き戻さない（飛ばしても失うデータが無い）
EMPTY_RAW_LINES = [
    pytest.param(b"", id="empty"),
    pytest.param(b"   ", id="blank"),
]


@pytest.mark.parametrize("raw_line", BROKEN_RAW_LINES)
def test_broken_line_bytes_are_kept(tmp_path, raw_line):
    """飛ばした行は、元のバイトのまま書き戻される。"""
    path = write_data(tmp_path, DATE1, [DATALINE1])
    with open(path, mode="ab") as f:
        f.write(raw_line + b"\n")

    sdf = SchedDataFile(DATE1, topdir=str(tmp_path))
    assert sdf.skipped_lines == [raw_line]

    sdf.save()

    assert path.read_bytes() == (
        DATALINE1.encode("utf-8") + b"\n" + raw_line + b"\n"
    )


@pytest.mark.parametrize("raw_line", BROKEN_RAW_LINES)
def test_broken_line_is_skipped_again(tmp_path, raw_line):
    """書き戻した行は、読み直すとまた飛ばされる（警告も出続ける）。"""
    path = write_data(tmp_path, DATE1, [DATALINE1])
    with open(path, mode="ab") as f:
        f.write(raw_line + b"\n")

    SchedDataFile(DATE1, topdir=str(tmp_path)).save()

    with mock.patch.object(SchedDataFile, "_SchedDataFile__log") as log:
        sdf2 = SchedDataFile(DATE1, topdir=str(tmp_path))

    assert [sde.sde_id for sde in sdf2.sde] == ["id-1"]
    assert sdf2.skipped_lines == [raw_line]
    assert log.warning.called


@pytest.mark.parametrize("raw_line", EMPTY_RAW_LINES)
def test_empty_line_is_not_written_back(tmp_path, raw_line):
    """空行は書き戻さない（飛ばしても失うデータが無いため）。"""
    path = write_data(tmp_path, DATE1, [DATALINE1])
    with open(path, mode="ab") as f:
        f.write(raw_line + b"\n")

    sdf = SchedDataFile(DATE1, topdir=str(tmp_path))
    assert sdf.skipped_lines == []

    sdf.save()

    assert path.read_bytes() == DATALINE1.encode("utf-8") + b"\n"


@pytest.mark.parametrize("raw_line", EMPTY_RAW_LINES)
def test_empty_line_warning_stops_after_save(tmp_path, raw_line):
    """空行を保存で落とせば、次の読み込みで警告が出なくなる。"""
    path = write_data(tmp_path, DATE1, [DATALINE1])
    with open(path, mode="ab") as f:
        f.write(raw_line + b"\n")

    with mock.patch.object(SchedDataFile, "_SchedDataFile__log") as log:
        sdf = SchedDataFile(DATE1, topdir=str(tmp_path))
    assert log.warning.called

    sdf.save()

    with mock.patch.object(SchedDataFile, "_SchedDataFile__log") as log:
        sdf2 = SchedDataFile(DATE1, topdir=str(tmp_path))

    assert [sde.sde_id for sde in sdf2.sde] == ["id-1"]
    assert not log.warning.called


def test_all_lines_broken_survives_two_saves(tmp_path):
    """全行が壊れているファイルでも、保存 2 回でデータを失わない。

    旧形式では、この形のファイルに追加して 2 回保存すると、元の
    データが本体からも ``.bak`` からも消えた
    （``docs/data-format.md`` の「壊れた行の扱い」）。
    """
    raw = b"[1, 2]\n{ x\n"
    path = write_data(tmp_path, DATE1, [])
    path.write_bytes(raw)

    sdf = SchedDataFile(DATE1, topdir=str(tmp_path))
    assert sdf.sde == []
    assert sdf.skipped_lines == [b"[1, 2]", b"{ x"]

    for i in range(2):
        sdf = SchedDataFile(DATE1, topdir=str(tmp_path))
        sdf.add_sde(mk_sde(sde_id=f"id-add{i}"))
        sdf.save()

    backup = path.parent / (path.name + SchedDataFile.BACKUP_EXT)

    assert path.read_bytes().endswith(raw)
    assert backup.read_bytes().endswith(raw)
    assert len(path.read_bytes().rstrip(b"\n").split(b"\n")) == 4


def test_no_broken_line_writes_nothing_extra(tmp_path):
    """飛ばした行が無ければ、余計なものは書かれない。"""
    path = write_data(tmp_path, DATE1, [DATALINE1, DATALINE2])

    sdf = SchedDataFile(DATE1, topdir=str(tmp_path))
    assert sdf.skipped_lines == []

    sdf.save()

    assert path.read_bytes() == (
        DATALINE2.encode("utf-8") + b"\n" + DATALINE1.encode("utf-8") + b"\n"
    )


def test_skipped_lines_of_new_file(tmp_path):
    """ファイルが無いときは、飛ばした行も無い。"""
    sdf = SchedDataFile(DATE1, topdir=str(tmp_path))

    assert sdf.skipped_lines == []


def test_save_and_load_round_trip(tmp_path):
    """保存して読み直すと、同じ内容になる。"""
    sde = mk_sde(detail="a\nb")
    sdf = SchedDataFile(DATE1, topdir=str(tmp_path))
    sdf.add_sde(sde)
    sdf.save()

    sdf2 = SchedDataFile(DATE1, topdir=str(tmp_path))

    assert len(sdf2.sde) == 1
    sde2 = sdf2.sde[0]
    assert sde2.mk_dataline() == sde.mk_dataline()
    assert sde2.sde_id == sde.sde_id
    assert sde2.date == sde.date
    assert sde2.time_start == sde.time_start
    assert sde2.time_end == sde.time_end
    assert sde2.type == sde.type
    assert sde2.title == sde.title
    assert sde2.place == sde.place
    assert sde2.detail == sde.detail


def test_save_and_load_round_trip_todo(tmp_path):
    """ToDo（date=None のファイル）も往復できる。"""
    sde = mk_sde(sde_type="□買い物", time_start=None, time_end=None)
    sdf = SchedDataFile(None, topdir=str(tmp_path))
    sdf.add_sde(sde)
    sdf.save()

    sdf2 = SchedDataFile(None, topdir=str(tmp_path))

    assert [s.mk_dataline() for s in sdf2.sde] == [sde.mk_dataline()]
    assert sdf2.sde[0].is_todo() is True


def test_save_makes_dir(tmp_path):
    sdf = SchedDataFile(DATE1, topdir=str(tmp_path / "new"))
    sdf.add_sde(mk_sde())
    sdf.save()

    assert (tmp_path / "new/2021/03/01.jsonl").exists()


def test_save_makes_backup(tmp_path):
    path = write_data(tmp_path, DATE1, [DATALINE1])
    sdf = SchedDataFile(DATE1, topdir=str(tmp_path))
    sdf.add_sde(mk_sde(sde_id="id-9", title="追加"))
    sdf.save()

    backup = path.parent / (path.name + SchedDataFile.BACKUP_EXT)
    assert backup.read_text(encoding="utf-8") == DATALINE1 + "\n"
    assert len(path.read_text(encoding="utf-8").splitlines()) == 2


def test_save_empty_writes_empty_file(tmp_path):
    """空になっても、ファイルは空で書かれる（消さない）。"""
    path = write_data(tmp_path, DATE1, [DATALINE1])
    sdf = SchedDataFile(DATE1, topdir=str(tmp_path))
    sdf.del_sde("id-1")
    sdf.save()

    assert path.exists()
    assert path.read_text(encoding="utf-8") == ""

    backup = path.parent / (path.name + SchedDataFile.BACKUP_EXT)
    assert backup.read_text(encoding="utf-8") == DATALINE1 + "\n"


def test_save_empty_keeps_backup(tmp_path):
    """空のファイルは ``.bak`` へ退避しない。

    退避してしまうと、``.bak`` にしか残っていないデータを空で
    上書きしてしまう。
    """
    path = write_data(tmp_path, DATE1, [DATALINE1])
    sdf = SchedDataFile(DATE1, topdir=str(tmp_path))
    sdf.del_sde("id-1")

    sdf.save()  # 1 回目: 元データが `.bak` へ移る
    sdf.save()  # 2 回目: 空のファイルは移さない

    backup = path.parent / (path.name + SchedDataFile.BACKUP_EXT)
    assert backup.read_text(encoding="utf-8") == DATALINE1 + "\n"
    assert path.read_text(encoding="utf-8") == ""


def test_save_empty_and_load(tmp_path):
    """空のファイルは、そのまま読み直せる。"""
    write_data(tmp_path, DATE1, [DATALINE1])
    sdf = SchedDataFile(DATE1, topdir=str(tmp_path))
    sdf.del_sde("id-1")
    sdf.save()

    assert SchedDataFile(DATE1, topdir=str(tmp_path)).sde == []


def test_add_sde_is_sorted(tmp_path):
    sdf = SchedDataFile(DATE1, topdir=str(tmp_path))
    sdf.add_sde(mk_sde(sde_id="id-1"))
    sdf.add_sde(
        mk_sde(sde_id="id-2", sde_type="休日", time_start=None, time_end=None)
    )

    assert [sde.sde_id for sde in sdf.sde] == ["id-2", "id-1"]


def test_del_sde(tmp_path):
    sdf = SchedDataFile(DATE1, topdir=str(tmp_path))
    sdf.add_sde(mk_sde(sde_id="id-1"))
    sdf.add_sde(mk_sde(sde_id="id-2"))
    sdf.del_sde("id-1")

    assert [sde.sde_id for sde in sdf.sde] == ["id-2"]


def test_del_sde_unknown_id(tmp_path):
    sdf = SchedDataFile(DATE1, topdir=str(tmp_path))
    sdf.add_sde(mk_sde(sde_id="id-1"))
    sdf.del_sde("id-x")

    assert [sde.sde_id for sde in sdf.sde] == ["id-1"]


def test_get_sde(tmp_path):
    sdf = SchedDataFile(DATE1, topdir=str(tmp_path))
    sde = mk_sde(sde_id="id-1")
    sdf.add_sde(sde)

    assert sdf.get_sde("id-1") is sde
    assert sdf.get_sde("id-x") is None


C_LOCALE_SAVE_SCRIPT = """\
import datetime
import sys

from ytsched.ytsched import SchedDataEnt, SchedDataFile

topdir = sys.argv[1]

sdf = SchedDataFile(datetime.date(2021, 3, 1), topdir=topdir)
sdf.add_sde(SchedDataEnt('id-1', datetime.date(2021, 3, 1),
                         None, None, '予定', 'タイトル', '場所', '詳細'))
sdf.save()
"""


def test_save_is_not_locale_dependent(tmp_path):
    """``LC_ALL=C`` でも日本語を保存できる。"""
    topdir = tmp_path / "data"

    res = run_in_c_locale(tmp_path, C_LOCALE_SAVE_SCRIPT, topdir)

    assert res.returncode == 0, res.stderr
    line = (topdir / "2021/03/01.jsonl").read_text(encoding="utf-8")
    assert json.loads(line)["title"] == "タイトル"


#
# SchedData
#
def test_get_sdf_cache_miss_and_hit(tmp_path):
    sd = SchedData(str(tmp_path))
    assert sd.get_cache_size() == 0

    sdf1 = sd.get_sdf(DATE1)
    assert sd.get_cache_size() == 1

    sdf2 = sd.get_sdf(DATE1)
    assert sdf2 is sdf1
    assert sd.get_cache_size() == 1


def test_get_sdf_lru_order(tmp_path):
    """ヒットしたものが末尾（最近使った側）へ移る。"""
    sd = SchedData(str(tmp_path))
    date2 = DATE1 + datetime.timedelta(1)

    sd.get_sdf(DATE1)
    sd.get_sdf(date2)
    assert sd.get_keys() == [str(DATE1), str(date2)]

    sd.get_sdf(DATE1)
    assert sd.get_keys() == [str(date2), str(DATE1)]


def test_get_sdf_discard(tmp_path):
    """``_cache_size`` を超えたら、古い方から捨てる。"""
    sd = SchedData(str(tmp_path), cache_size=10)
    for i in range(10):
        sd.get_sdf(DATE1 + datetime.timedelta(i))

    assert sd.get_cache_size() == 10

    sd.get_sdf(DATE1 + datetime.timedelta(10))

    # 10 * CACHE_DISCARD_RATE = 1 件が捨てられてから、1 件追加される
    assert sd.get_cache_size() == 10
    assert str(DATE1) not in sd.get_keys()
    assert str(DATE1 + datetime.timedelta(1)) in sd.get_keys()


def test_sched_data_get_sde(tmp_path):
    write_data(tmp_path, DATE1, [DATALINE1])
    sd = SchedData(str(tmp_path))

    sde = sd.get_sde(DATE1, "id-1")
    assert sde is not None
    assert sde.title == "タイトル"
    assert sd.get_sde(DATE1, "id-x") is None


def test_sched_data_add_sde(tmp_path):
    sd = SchedData(str(tmp_path))
    sd.add_sde(DATE1, mk_sde())

    # add_sde() は保存しない(TODO-077)
    assert not (tmp_path / "2021/03/01.jsonl").exists()
    assert sd.get_sde(DATE1, "id-1") is not None

    sd.save()
    assert (tmp_path / "2021/03/01.jsonl").exists()


def test_sched_data_add_sde_todo(tmp_path):
    sd = SchedData(str(tmp_path))
    sd.add_sde(None, mk_sde(sde_type="□買い物"))

    assert not (tmp_path / "ToDo.jsonl").exists()
    assert sd.get_sde(None, "id-1") is not None

    sd.save()
    assert (tmp_path / "ToDo.jsonl").exists()


def test_sched_data_del_sde(tmp_path):
    sd = SchedData(str(tmp_path))
    sd.add_sde(DATE1, mk_sde())
    sd.del_sde(DATE1, "id-1")

    assert sd.get_sde(DATE1, "id-1") is None

    sd.save()
    # 空になってもファイルは残る
    assert (tmp_path / "2021/03/01.jsonl").read_text(encoding="utf-8") == ""


def test_sched_data_save_writes_once_per_date(tmp_path):
    """同じ日に複数回 add_sde() しても save() は 1 回で済む(TODO-077)。"""
    sd = SchedData(str(tmp_path))
    sd.add_sde(DATE1, mk_sde(sde_id="id-1"))
    sd.add_sde(DATE1, mk_sde(sde_id="id-2"))

    sdf = sd.get_sdf(DATE1)

    with mock.patch.object(sdf, "save", wraps=sdf.save) as save:
        sd.save()

    save.assert_called_once()


def test_sched_data_save_after_cache_discard(tmp_path):
    """キャッシュから捨てられた日の変更も、save() で保存される。

    変更を「日付」で覚えると、捨てられたあとに日付から引き直した
    ときに、変更の乗っていない別のインスタンスになる。
    ``SchedDataFile`` そのものを覚えているので、そうならない
    (TODO-077)。
    """
    # 捨てる件数は int(cache_size * CACHE_DISCARD_RATE) なので、
    # 10 未満だと 1 件も捨てられない
    sd = SchedData(str(tmp_path), cache_size=10)

    for i in range(11):
        date = DATE1 + datetime.timedelta(i)
        sd.add_sde(date, mk_sde(sde_id=f"id-{i}", date=date))

    # 最初の日は、途中でキャッシュから捨てられている
    assert sd.get_cache_size() < 11

    sd.save()

    path = tmp_path / "2021/03/01.jsonl"
    assert "id-0" in path.read_text(encoding="utf-8")


def test_sdf_exists(tmp_path):
    """ファイルがあるかどうかを、開かずに見る（TODO-028）。"""
    write_data(tmp_path, DATE1, [DATALINE1])
    sd = SchedData(str(tmp_path))

    assert sd.sdf_exists(DATE1) is True
    assert sd.sdf_exists(DATE1 + datetime.timedelta(1)) is False
    # 見るだけなので、キャッシュには積まれない
    assert sd.get_cache_size() == 0


def test_sdf_exists_todo(tmp_path):
    """``date`` が None なら ``ToDo.jsonl`` を見る。"""
    sd = SchedData(str(tmp_path))
    assert sd.sdf_exists(None) is False

    (tmp_path / "ToDo.jsonl").write_text("", encoding="utf-8")
    assert sd.sdf_exists(None) is True


def test_sdf_exists_cached(tmp_path):
    """ファイルが無くても、キャッシュに載っていれば ``True``。

    書き込む前のデータを、開いたときのまま返すため。
    """
    sd = SchedData(str(tmp_path))
    assert sd.sdf_exists(DATE1) is False

    sd.get_sdf(DATE1)
    assert sd.sdf_exists(DATE1) is True


def test_sdf_exists_expands_topdir(tmp_path, monkeypatch):
    """``~`` 付きの ``topdir`` でも、展開してから見に行く。"""
    monkeypatch.setenv("HOME", str(tmp_path))
    write_data(tmp_path / "data", DATE1, [DATALINE1])

    sd = SchedData("~/data")

    assert sd.sdf_exists(DATE1) is True


def test_get_sdf_cache_miss_is_not_warning(tmp_path):
    """正常系のキャッシュミスで warning を出さない。"""
    # ``self.__log`` は ``_SchedData__log`` にマングリングされる
    with mock.patch.object(SchedData, "_SchedData__log") as log:
        sd = SchedData(str(tmp_path))
        sd.get_sdf(DATE1)

    log.warning.assert_not_called()

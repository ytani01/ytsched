#
# (c) 2026 Yoichi Tanibayashi
#
"""ytsched.ytsched のユニットテスト"""

import datetime
import inspect
import uuid
from typing import Any
from unittest import mock

import pytest
from helpers import run_in_c_locale

from ytsched.ytsched import (
    SchedData,
    SchedDataEnt,
    SchedDataFile,
    htmlstr2text,
    text2htmlstr,
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
# htmlstr2text() / text2htmlstr()
#
@pytest.mark.parametrize(
    ("intext", "expected"),
    [
        ("a&amp;#160;b", "a b"),
        ("a&gt;b", "a>b"),
        ("a&lt;b", "a<b"),
        ("a&NBSP;b", "a b"),
        ("a&#160;b", "a b"),
        ("a&nbsp;b", "a b"),
        ("（かっこ）", "(かっこ)"),
        ("a<BR>b", "a\nb"),
        ("a<br />b", "a\nb"),
        ("a<BR/>b", "a\nb"),
    ],
)
def test_htmlstr2text(intext, expected):
    assert htmlstr2text(intext) == expected


def test_htmlstr2text_amp_is_kept():
    """``&amp;`` の変換はコメントアウトされたままになっている。"""
    assert htmlstr2text("a&amp;b") == "a&amp;b"


@pytest.mark.parametrize(
    ("intext", "expected"),
    [
        ("a\nb", "a<br />b"),
        ("a\tb", "a b"),
        ("a\r\nb", "a<br />b"),
        ("a\n", "a"),
        ("a\n\n", "a"),
    ],
)
def test_text2htmlstr(intext, expected):
    assert text2htmlstr(intext) == expected


def test_text_htmlstr_round_trip():
    """改行と ``<br />`` の往復。末尾の改行だけは落ちる。"""
    text = "line1\nline2\nline3"
    assert htmlstr2text(text2htmlstr(text)) == text


#
# SchedDataEnt
#
def test_sde_init_detail_is_converted():
    sde = mk_sde(detail="a<br />b")
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
    assert sde.mk_dataline() == "\t".join(  # noqa: FLY002
        [
            "id-1",
            "2021/03/01",
            "09:05-10:30",
            "予定",
            "タイトル",
            "場所",
            "a<br />b",
        ]
    )


def test_mk_dataline_no_time():
    sde = mk_sde(time_start=None, time_end=None)
    assert sde.mk_dataline().split("\t")[2] == SchedDataEnt.TIME_NULL


def test_search_str():
    sde = mk_sde(title="Title", detail="a\nb")
    assert sde.search_str() == "#予定 +title @場所 detail:a b"


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
    assert sdf.pathname == f"{tmp_path}/2021/03/01.cgi"
    assert sdf.dirname == f"{tmp_path}/2021/03"
    assert sdf.filename == "01.cgi"


def test_date2path_todo(tmp_path):
    sdf = SchedDataFile(None, topdir=str(tmp_path))
    assert sdf.pathname == f"{tmp_path}/ToDo.cgi"


def test_topdir_is_expanded():
    sdf = SchedDataFile(DATE1, topdir="~/no_such_dir")
    assert not sdf.topdir.startswith("~")


def test_load_no_file(tmp_path):
    sdf = SchedDataFile(DATE1, topdir=str(tmp_path))
    assert sdf.sde == []
    assert sdf.is_holiday is False


def write_data(tmp_path, date, lines, encoding="utf-8"):
    """データファイルを書いて、パスを返す。"""
    path = tmp_path / date.strftime("%Y") / date.strftime("%m")
    path.mkdir(parents=True, exist_ok=True)
    path = path / (date.strftime("%d") + ".cgi")
    path.write_text("".join(l + "\n" for l in lines), encoding=encoding)
    return path


# タブ区切りの項目の並びが見えるよう、f-string にせず
# join のまま残す（TODO-015）
DATALINE1 = "\t".join(  # noqa: FLY002
    [
        "id-1",
        "2021/03/01",
        "09:05-10:30",
        "予定",
        "タイトル",
        "場所",
        "a<br />b",
    ]
)
DATALINE2 = "\t".join(  # noqa: FLY002
    [
        "id-2",
        "2021/03/01",
        ":-:",
        "休日",
        "振替休日",
        "",
        "",
    ]
)


@pytest.mark.parametrize("encoding", ["utf-8", "euc_jp"])
def test_load(tmp_path, encoding):
    write_data(tmp_path, DATE1, [DATALINE1], encoding=encoding)

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
    # 保存 → 読み直しで、末尾に `\n` が 1 つ増えるのが現状
    assert sde.detail == "a\nb\n"


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


def test_load_hour_and_minute_are_normalized(tmp_path):
    """時分は ``% 24`` / ``% 60`` される。"""
    line = DATALINE1.replace("09:05-10:30", "25:05-10:70")
    write_data(tmp_path, DATE1, [line])

    sde = SchedDataFile(DATE1, topdir=str(tmp_path)).sde[0]

    assert sde.time_start == datetime.time(1, 5)
    assert sde.time_end == datetime.time(10, 10)


def test_load_short_line(tmp_path):
    """項目が足りない行も読める（足りない分は空文字）。"""
    line = "\t".join(  # noqa: FLY002
        ["id-1", "2021/03/01", "09:05-10:30", "予定"]
    )
    write_data(tmp_path, DATE1, [line])

    sde = SchedDataFile(DATE1, topdir=str(tmp_path)).sde[0]

    assert sde.sde_id == "id-1"
    assert sde.time_start == datetime.time(9, 5)
    assert sde.type == "予定"
    assert sde.title == ""
    assert sde.place == ""
    assert sde.detail == ""


def test_load_short_line_is_not_lost(tmp_path):
    """項目が足りない行も、保存し直したときに消えない。"""
    line = "\t".join(  # noqa: FLY002
        ["id-1", "2021/03/01", "09:05-10:30", "予定"]
    )
    write_data(tmp_path, DATE1, [line])

    sdf = SchedDataFile(DATE1, topdir=str(tmp_path))
    sdf.save()

    assert [
        s.sde_id for s in SchedDataFile(DATE1, topdir=str(tmp_path)).sde
    ] == ["id-1"]


def test_load_time_without_hyphen(tmp_path):
    """時刻欄に ``-`` が無い行も読める（開始・終了とも空）。"""
    line = DATALINE1.replace("09:05-10:30", "09:05")
    write_data(tmp_path, DATE1, [line])

    sde = SchedDataFile(DATE1, topdir=str(tmp_path)).sde[0]

    assert not sde.time_start
    assert not sde.time_end


def test_load_empty_time_field(tmp_path):
    """時刻欄が空の行も読める。"""
    line = DATALINE1.replace("09:05-10:30", "")
    write_data(tmp_path, DATE1, [line])

    sde = SchedDataFile(DATE1, topdir=str(tmp_path)).sde[0]

    assert not sde.time_start
    assert not sde.time_end


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
    # `detail` だけは、末尾に `\n` が 1 つ増えるのが現状
    assert sde2.detail == sde.detail + "\n"


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

    assert (tmp_path / "new/2021/03/01.cgi").exists()


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
    assert (topdir / "2021/03/01.cgi").read_text(encoding="utf-8").split(
        "\t"
    )[4] == "タイトル"


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

    assert (tmp_path / "2021/03/01.cgi").exists()
    assert sd.get_sde(DATE1, "id-1") is not None


def test_sched_data_add_sde_todo(tmp_path):
    sd = SchedData(str(tmp_path))
    sd.add_sde(None, mk_sde(sde_type="□買い物"))

    assert (tmp_path / "ToDo.cgi").exists()
    assert sd.get_sde(None, "id-1") is not None


def test_sched_data_del_sde(tmp_path):
    sd = SchedData(str(tmp_path))
    sd.add_sde(DATE1, mk_sde())
    sd.del_sde(DATE1, "id-1")

    assert sd.get_sde(DATE1, "id-1") is None
    # 空になってもファイルは残る
    assert (tmp_path / "2021/03/01.cgi").read_text(encoding="utf-8") == ""


def test_get_sdf_cache_miss_is_not_warning(tmp_path):
    """正常系のキャッシュミスで warning を出さない。"""
    # ``self.__log`` は ``_SchedData__log`` にマングリングされる
    with mock.patch.object(SchedData, "_SchedData__log") as log:
        sd = SchedData(str(tmp_path))
        sd.get_sdf(DATE1)

    log.warning.assert_not_called()

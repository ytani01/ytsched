#
# (c) 2026 Yoichi Tanibayashi
#
"""移行ツール（旧形式 → JSON Lines）のテスト (TODO-020)

変換元は ``tests/data/old_format/``（TODO-019 で用意した合成データ）。
一時ディレクトリへコピーしてから変換する。
"""

import datetime
import json
import pathlib
import shutil
from unittest import mock

import pytest

from ytsched.migrate import (
    Migrator,
    conv_date,
    conv_time,
    decode_line,
    html2text,
    line2dict,
    split_fields,
)
from ytsched.ytsched import SchedDataFile

OLD_FORMAT_DIR = pathlib.Path(__file__).parent / "data" / "old_format"


@pytest.fixture
def datadir(tmp_path):
    """``tests/data/old_format`` をコピーした一時ディレクトリ"""
    path = tmp_path / "data"
    shutil.copytree(OLD_FORMAT_DIR, path)
    return path


def mk_migrator(datadir, **kwargs):
    """``Migrator`` を作る。

    ``--error-file`` の既定（カレントディレクトリ）を使わないよう、
    必ず一時ディレクトリの下を渡す。
    """
    kwargs.setdefault("error_file", str(pathlib.Path(datadir) / "errors.txt"))
    return Migrator(str(datadir), **kwargs)


@pytest.fixture
def migrated(datadir):
    """変換したあとのデータディレクトリ"""
    mk_migrator(datadir).main()
    return datadir


def load_jsonl(path):
    """``.jsonl`` を読んで dict のリストを返す。"""
    data = path.read_bytes()
    if data.endswith(b"\n"):
        data = data[:-1]
    if not data:
        return []
    return [json.loads(line) for line in data.split(b"\n")]


#
# 部品
#
@pytest.mark.parametrize(
    ("raw_line", "expected"),
    [
        ("会議".encode(), "会議"),
        ("会議".encode("euc_jp"), "会議"),
        (b"ascii", "ascii"),
    ],
)
def test_decode_line(raw_line, expected):
    assert decode_line(raw_line) == expected


def test_decode_line_broken_byte():
    """どちらでも読めない行も、U+FFFD にして残す（手順 1）。"""
    raw_line = "会議".encode("euc_jp") + b"\xad" + "室".encode("euc_jp")

    out = decode_line(raw_line)

    assert out.startswith("会議")
    assert out.endswith("室")
    assert "�" in out


def test_split_lines_u2028():
    """U+2028 では切らない（読み込み側と同じものを使う）。"""
    data = "a\u2028b\nc\n".encode()

    assert SchedDataFile.split_lines(data) == ["a\u2028b".encode(), b"c"]


def test_split_lines_empty():
    assert SchedDataFile.split_lines(b"") == []


@pytest.mark.parametrize(
    ("line", "expected"),
    [
        ("a\tb\tc\td\te\tf\tg", ["a", "b", "c", "d", "e", "f", "g"]),
        ("a\tb\tc\td\te\tf", ["a", "b", "c", "d", "e", "f", ""]),
        ("a", ["a", "", "", "", "", "", ""]),
        ("a\tb\tc\td\te\tf\tg\th", ["a", "b", "c", "d", "e", "f", "g\th"]),
    ],
)
def test_split_fields(line, expected):
    """7 個に満たなければ埋め、8 個目から先はつなぎ直す（手順 2）。"""
    assert split_fields(line) == expected


def test_conv_date():
    assert conv_date("2005/07/13") == "2005-07-13"


@pytest.mark.parametrize("date_str", ["", "2005-07-13", "2005/13/45", "x"])
def test_conv_date_invalid(date_str):
    with pytest.raises(ValueError, match=r".*"):
        conv_date(date_str)


@pytest.mark.parametrize(
    ("time_str", "expected"),
    [
        ("09:30-17:15", ("09:30", "17:15")),
        ("09:00-:", ("09:00", None)),
        (":-18:00", (None, "18:00")),
        (":-:", (None, None)),
        ("", (None, None)),
        ("09:00", (None, None)),
        ("28:00-:", ("04:00", None)),
        ("10:70-:", ("10:10", None)),
    ],
)
def test_conv_time(time_str, expected):
    assert conv_time(time_str) == expected


@pytest.mark.parametrize(
    ("intext", "expected"),
    [
        ("a<br />b", "a\nb"),
        ("a<BR>b", "a\nb"),
        ("a<BR/>b", "a\nb"),
        ("a&nbsp;b", "a b"),
        ("a&#160;b", "a b"),
        ("a&amp;#160;b", "a b"),
        ("a&quot;b", 'a"b'),
        ("3 &lt; x &gt; 1", "3 < x > 1"),
        ("a\u00a0b", "a b"),
    ],
)
def test_html2text(intext, expected):
    assert html2text(intext) == expected


def test_html2text_keeps_other_tags():
    """``<br />`` 以外の HTML タグはそのまま残す（手順 5）。"""
    intext = '<b>重要</b>な連絡<br />詳細は <a href="x">こちら</a>'

    assert html2text(intext) == (
        '<b>重要</b>な連絡\n詳細は <a href="x">こちら</a>'
    )


def test_html2text_keeps_zenkaku_paren():
    """全角括弧はそのままにする（手順 6）。"""
    assert html2text("（重要）打合せ") == "（重要）打合せ"


def test_html2text_unescape_is_only_twice():
    """``html.unescape()`` は 2 回まで（3 回以上はかけない）。"""
    assert html2text("&amp;amp;amp;") == "&amp;"


def test_line2dict():
    line = "\t".join(  # noqa: FLY002
        [
            "id-1",
            "2021/08/01",
            "10:00-11:00",
            "予定",
            "★打合せ",
            "第1会議室",
            "議題<br />・進捗",
        ]
    )

    assert line2dict(line) == {
        "sde_id": "id-1",
        "date": "2021-08-01",
        "time_start": "10:00",
        "time_end": "11:00",
        "type": "予定",
        "title": "★打合せ",
        "place": "第1会議室",
        "detail": "議題\n・進捗",
    }


def test_line2dict_invalid_date():
    with pytest.raises(ValueError, match=r".*"):
        line2dict("id-1\txxxx\t:-:\t予定\t表題\t\t")


#
# Migrator
#
def test_find_files(datadir):
    """対象は ``{年}/{月}/{日}.cgi`` と ``ToDo.cgi`` だけ。"""
    files = mk_migrator(datadir).find_files()

    assert [str(f.relative_to(datadir)) for f in files] == [
        "2005/07/13.cgi",
        "2005/07/14.cgi",
        "2012/01/09.cgi",
        "2021/08/01.cgi",
        "2021/08/02.cgi",
        "2021/08/03.cgi",
        "2021/08/04.cgi",
        "ToDo.cgi",
    ]


@pytest.mark.parametrize(
    "name",
    ["2021/08/01-backup.cgi", "2021/08/01.cgi.bak", "iappli_log.cgi"],
)
def test_out_of_scope_files_are_not_converted(migrated, name):
    """対象外の 3 ファイルは変換しない。"""
    path = migrated / name

    assert path.exists()
    assert not path.with_suffix(".jsonl").exists()
    assert not (migrated / (name + ".jsonl")).exists()


def test_stat(datadir):
    stat = mk_migrator(datadir).main()

    assert stat.files == 8
    assert stat.skipped_files == 0
    assert stat.lines == 27
    assert stat.error_lines == 0


def test_old_files_are_kept(migrated):
    """元の ``.cgi`` は消さない。"""
    assert (migrated / "2021/08/01.cgi").exists()


def test_empty_file(migrated):
    """空のファイルは、空のまま変換される。"""
    assert (migrated / "2021/08/03.jsonl").read_bytes() == b""


def test_broken_byte_line_is_kept(migrated):
    """どちらでも読めない 1 バイトを含む行も残る（手順 1）。"""
    data = load_jsonl(migrated / "2005/07/13.jsonl")

    assert len(data) == 3
    assert data[0]["sde_id"] == "1120729620-000164"
    assert "�" in data[0]["detail"]
    assert data[0]["detail"].startswith("資料は前日までに配布\n")


def test_euc_jp_lines(migrated):
    """euc_jp の行が読める。"""
    data = load_jsonl(migrated / "2005/07/13.jsonl")

    assert data[1]["title"] == "(キャンセル)△△社打合せ"
    assert data[2]["title"] == "動作確認の結果まとめ"


def test_nbsp_becomes_space(migrated):
    """``&nbsp;`` ``&amp;#160;`` が半角空白になる（手順 5）。"""
    data = load_jsonl(migrated / "2005/07/14.jsonl")

    assert data[0]["place"] == "第一会議室 A"
    assert "\u00a0" not in data[0]["detail"]
    assert "&#160;" not in data[0]["detail"]
    assert data[2]["detail"] == "連絡先 内線 1234"


def test_escaped_chars(migrated):
    """``&quot;`` ``&lt;`` ``&gt;`` が戻る（手順 5）。"""
    data = load_jsonl(migrated / "2005/07/14.jsonl")

    assert data[0]["title"] == '"仮"見積の確認'
    assert data[0]["detail"].startswith("条件は 3 < x > 1 の範囲")


def test_time_out_of_range(migrated):
    """``28:00`` が ``04:00`` になる（手順 4）。"""
    data = load_jsonl(migrated / "2012/01/09.jsonl")
    time_list = [(d["time_start"], d["time_end"]) for d in data]

    assert time_list == [
        ("10:00", "11:30"),
        ("09:00", None),
        (None, "18:00"),
        (None, None),
        ("04:00", None),
    ]


def test_zenkaku_paren_is_kept(migrated):
    """全角括弧はそのままにする（手順 6）。"""
    data = load_jsonl(migrated / "2021/08/01.jsonl")

    assert data[1]["title"] == "（重要）健康診断の申込"


def test_br_becomes_newline(migrated):
    data = load_jsonl(migrated / "2021/08/01.jsonl")

    assert data[0]["detail"] == "議題\n・進捗\n・来月の予定"


def test_html_tags_are_kept(migrated):
    """``<br />`` 以外の HTML タグはそのまま残す。"""
    data = load_jsonl(migrated / "2021/08/02.jsonl")

    assert data[0]["detail"] == (
        "<b>重要</b>な連絡あり\n"
        '詳細は <a href="https://example.com/">こちら</a>'
    )


def test_u2028_is_not_split(migrated):
    """U+2028 で 1 件が 2 行に割れない。"""
    path = migrated / "2021/08/02.jsonl"
    data = load_jsonl(path)

    assert len(data) == 3
    assert data[2]["detail"] == "前半のまとめ\u2028後半のまとめ\n以上"
    # ファイルの中でも生の U+2028 のまま
    assert "\u2028".encode() in path.read_bytes()


def test_duplicated_sde_id_is_kept(migrated):
    """重複した ``sde_id`` も、そのまま移す（振り直さない）。"""
    data = load_jsonl(migrated / "2021/08/02.jsonl")

    assert [d["sde_id"] for d in data[:2]] == [
        "1627783341-8621308",
        "1627783341-8621308",
    ]


def test_short_and_long_line(migrated):
    """6 列の行は空文字で埋め、8 列の行はつなぎ直す（手順 2）。"""
    data = load_jsonl(migrated / "2021/08/04.jsonl")

    assert len(data) == 3
    assert data[1]["place"] == "detail が無い"
    assert data[1]["detail"] == ""
    assert data[2]["detail"] == (
        "本文にタブが入っている\t8 個目から先は detail の続き"
    )


def test_todo(migrated):
    """``ToDo.cgi`` は ``ToDo.jsonl`` になる。"""
    data = load_jsonl(migrated / "ToDo.jsonl")

    assert len(data) == 5
    assert data[0]["type"] == "□解約"
    assert data[0]["date"] == "2026-08-31"


def test_migrated_data_is_loadable(migrated):
    """変換したデータを ``SchedDataFile`` で読める。"""
    sdf = SchedDataFile(datetime.date(2021, 8, 1), topdir=str(migrated))

    assert len(sdf.sde) == 5
    assert sdf.is_holiday is True

    sde = sdf.get_sde("1627783338-8621305")
    assert sde is not None
    assert sde.title == "（重要）健康診断の申込"
    # 全角括弧のままでも「重要」と判定される
    assert sde.is_important() is True


def test_migrated_todo_is_loadable(migrated):
    sdf = SchedDataFile(None, topdir=str(migrated))

    assert len(sdf.sde) == 5
    assert all(sde.is_todo() for sde in sdf.sde)


def test_migrated_data_has_no_warning(migrated):
    """変換したデータを読んでも、飛ばす行が出ない。"""
    for path in sorted(migrated.glob("**/*.jsonl")):
        raw = path.read_bytes()
        n_line = len(SchedDataFile.split_lines(raw))
        assert len(load_jsonl(path)) == n_line, path


#
# --dry-run と、変換できなかった行
#
def test_dry_run(datadir):
    stat = mk_migrator(datadir, dry_run=True).main()

    assert stat.files == 8
    assert stat.lines == 27
    assert not list(datadir.glob("**/*.jsonl"))


def test_existing_jsonl_is_skipped(datadir):
    (datadir / "ToDo.jsonl").write_text("", encoding="utf-8")

    stat = mk_migrator(datadir).main()

    assert stat.files == 7
    assert stat.skipped_files == 1
    assert (datadir / "ToDo.jsonl").read_text(encoding="utf-8") == ""


def test_error_line_is_saved(tmp_path):
    """変換できない行は、捨てずに書き出す。"""
    datadir = tmp_path / "data"
    (datadir / "2021" / "08").mkdir(parents=True)
    (datadir / "2021/08/01.cgi").write_text(
        "id-1\t2021/08/01\t:-:\t予定\t読める行\t\t\n"
        "id-2\txxxx\t:-:\t予定\t読めない行\t\t\n",
        encoding="utf-8",
    )
    error_file = tmp_path / "errors.txt"

    stat = mk_migrator(datadir, error_file=str(error_file)).main()

    assert stat.lines == 1
    assert stat.error_lines == 1
    assert stat.skipped_lines == 1
    assert "読めない行" in error_file.read_text(encoding="utf-8")

    data = load_jsonl(datadir / "2021/08/01.jsonl")
    assert [d["sde_id"] for d in data] == ["id-1"]


def test_crlf_line_has_no_cr(tmp_path):
    """CRLF の旧データでも、行末の ``\\r`` が残らない（TODO-029）。

    合成テストデータは LF だけなので、ここで作る。旧形式では
    テキストモードの読み込みで消えていたので、移行で新しく入れない。
    """
    datadir = tmp_path / "data"
    (datadir / "2021" / "08").mkdir(parents=True)
    (datadir / "2021/08/01.cgi").write_bytes(
        "id-1\t2021/08/01\t10:00-11:00\t予定\t打合せ\t会議室"
        "\t議題<br />・進捗\r\n"
        "id-2\t2021/08/01\t:-:\t予定\t2 行目\t\t\r\n".encode()
    )

    stat = mk_migrator(datadir).main()

    assert stat.lines == 2
    assert stat.skipped_lines == 0

    data = load_jsonl(datadir / "2021/08/01.jsonl")
    assert data[0]["detail"] == "議題\n・進捗"
    assert data[1]["detail"] == ""
    # 値そのものを見る。json.dumps() の結果を見ると CR が ``\r`` の
    # 2 文字にエスケープされるので、どんな値でも通ってしまう
    assert all(
        "\r" not in v for d in data for v in d.values() if isinstance(v, str)
    )


def test_crlf_empty_line_is_skipped(tmp_path):
    """``\\r`` だけの行は空行として飛ばす（TODO-029）。

    ``is_empty_line()`` が ``strip()`` を使うので、TODO-029 の
    ``removesuffix(b"\\r")`` が無くても空行になる。**挙動が変わって
    いないことの確認**で、TODO-029 の変更を守るテストではない。
    """
    datadir = tmp_path / "data"
    (datadir / "2021" / "08").mkdir(parents=True)
    (datadir / "2021/08/01.cgi").write_bytes(
        "id-1\t2021/08/01\t:-:\t予定\t読める行\t\t\r\n\r\n".encode()
    )

    stat = mk_migrator(datadir).main()

    assert stat.lines == 1
    assert stat.empty_lines == 1
    assert stat.error_lines == 0


def test_empty_line_is_skipped(tmp_path):
    """空行は飛ばす（変換できなかった行にはしない）。"""
    datadir = tmp_path / "data"
    (datadir / "2021" / "08").mkdir(parents=True)
    (datadir / "2021/08/01.cgi").write_text(
        "id-1\t2021/08/01\t:-:\t予定\t読める行\t\t\n\n\n",
        encoding="utf-8",
    )

    stat = mk_migrator(datadir).main()

    assert stat.lines == 1
    assert stat.empty_lines == 2
    assert stat.error_lines == 0


def test_no_target_file_warns(tmp_path):
    """対象の ``.cgi`` が 1 つも無ければ、警告を出す。"""
    datadir = tmp_path / "empty"
    datadir.mkdir()

    with mock.patch.object(Migrator, "_Migrator__log") as log:
        stat = mk_migrator(datadir).main()

    assert stat.files == 0
    assert log.warning.called


def test_summary_is_printed(datadir, capsys):
    mk_migrator(datadir).main()

    out = capsys.readouterr().out
    assert "変換したファイル: 8" in out
    assert "変換した行      : 27" in out
    assert "飛ばした行      : 0" in out

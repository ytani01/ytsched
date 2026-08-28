#
# (c) 2026 ytani01
#
"""HandlerBase（conf.json の読み書き）のテスト"""

import json
import os
import subprocess
import sys
from unittest import mock

import pytest
from helpers import (
    URL_PREFIX,
    app_sd,
    make_app,
    make_handler,
    run_in_c_locale,
)

from ytsched.conf import ConfFile
from ytsched.handler import HandlerBase

CONF_FNAME = ConfFile.FNAME


@pytest.fixture
def datadir(tmp_path):
    path = tmp_path / "data"
    path.mkdir()
    return path


def test_settings_are_read(datadir):
    """``initialize()`` から受け取る依存
    （TODO-021 のゴールデンマスターテスト）。

    ``HandlerBase.__init__`` を整理しても、この値は変わらない。
    ``_days`` は TODO-049 で ``--days`` を消したときに落ちた。
    ``_sd`` は TODO-081 で ``app.settings`` 経由から ``initialize()``
    経由に変わり、``_title``/``_author``/``_version``/``_url_prefix``/
    ``_datadir`` は TODO-090 で ``AppInfo``（``_app_info``）へまとまった。
    渡ってくる値そのものは変わらない。
    """
    app = make_app(datadir)

    handler = make_handler(app, HandlerBase)

    assert handler._app_info.title == "Ytsched"
    assert handler._app_info.author == "ytani01"
    assert handler._app_info.version == "0.0.0"
    assert handler._app_info.url_prefix == URL_PREFIX + "/"
    assert handler._app_info.datadir == str(datadir)
    assert handler._sd is app_sd(app)
    assert handler._conf.pathname == os.path.join(str(datadir), CONF_FNAME)


def test_load_conf_no_file(datadir):
    handler = make_handler(make_app(datadir), HandlerBase)

    assert handler._conf.to_dict() == {}
    assert handler.get_conf("ToDo_Days") is None


def test_load_conf(datadir):
    (datadir / CONF_FNAME).write_text(
        '{"ToDo_Days": "365", "FilterStr": "会議"}', encoding="utf-8"
    )

    handler = make_handler(make_app(datadir), HandlerBase)

    assert handler.get_conf("ToDo_Days") == "365"
    assert handler.get_conf("FilterStr") == "会議"
    assert handler.get_conf("NoSuchKey") is None


def test_save_conf_is_json(datadir):
    """JSON で書き出す（TODO-032）。人が読める形にする。

    書き込みは ``on_finish()``（リクエストの終わり）にまとまっている
    ので、``set_conf()`` の直後ではなく、それを呼んでから確かめる
    （TODO-090）。
    """
    handler = make_handler(make_app(datadir), HandlerBase)
    handler.set_conf(HandlerBase.CONF_KEY_SEARCH_STR, "会議")
    handler.on_finish()

    text = (datadir / CONF_FNAME).read_text(encoding="utf-8")
    assert text == '{\n  "SearchStr": "会議"\n}\n'
    assert json.loads(text) == {"SearchStr": "会議"}


def test_conf_round_trip(datadir):
    """``on_finish()`` で書いた値が、新しい ``app``（＝新しい
    ``ConfFile``）でファイルから読み直せる（TODO-090）。
    """
    handler = make_handler(make_app(datadir), HandlerBase)
    handler.set_conf("ToDo_Days", "30")
    handler.set_conf("SearchN", "5")
    handler.on_finish()

    handler2 = make_handler(make_app(datadir), HandlerBase)
    assert handler2.get_conf("ToDo_Days") == "30"
    assert handler2.get_conf("SearchN") == "5"


def test_set_conf_overwrite(datadir):
    handler = make_handler(make_app(datadir), HandlerBase)
    handler.set_conf("ToDo_Days", "30")
    handler.set_conf("ToDo_Days", "7")
    handler.on_finish()

    handler2 = make_handler(make_app(datadir), HandlerBase)
    assert handler2.get_conf("ToDo_Days") == "7"


def test_conf_reloads_when_file_changed_outside(datadir):
    """外から ``conf.json`` を書き換えたら、次のリクエストで読み直す
    （``SchedDataFile.is_stale()`` と同じやり方。TODO-090）。
    """
    app = make_app(datadir)
    handler1 = make_handler(app, HandlerBase)
    assert handler1.get_conf("ToDo_Days") is None

    # mtime の分解能で不安定にならないよう、明示的に時刻をずらす
    conf_path = datadir / CONF_FNAME
    conf_path.write_text('{"ToDo_Days": "30"}', encoding="utf-8")
    st = os.stat(conf_path)
    os.utime(conf_path, (st.st_atime + 10, st.st_mtime + 10))

    # 次のリクエスト (＝新しい handler) の __init__ で読み直す
    handler2 = make_handler(app, HandlerBase)
    assert handler2.get_conf("ToDo_Days") == "30"


def test_conf_keeps_unsaved_changes(datadir):
    """未保存の変更があるうちは、外の書き換えで読み直さない
    （読み直すと変更が消えるため。TODO-090）。
    """
    app = make_app(datadir)
    handler1 = make_handler(app, HandlerBase)
    handler1.set_conf("ToDo_Days", "7")

    # 保存する (on_finish()) 前に、外からファイルが書き換わる
    conf_path = datadir / CONF_FNAME
    conf_path.write_text('{"ToDo_Days": "30"}', encoding="utf-8")
    st = os.stat(conf_path)
    os.utime(conf_path, (st.st_atime + 10, st.st_mtime + 10))

    # 同じ app（＝同じ ConfFile）を使う次の handler は、まだ読み直さない
    handler2 = make_handler(app, HandlerBase)
    assert handler2.get_conf("ToDo_Days") == "7"


def test_conf_write_happens_once_per_request(datadir):
    """1 リクエストの中で ``set_conf()`` を何度呼んでも、
    書き込みは ``on_finish()`` で 1 回だけ（TODO-090）。
    """
    handler = make_handler(make_app(datadir), HandlerBase)

    with mock.patch.object(
        handler._conf, "_save", wraps=handler._conf._save
    ) as save:
        handler.set_conf("ToDo_Days", "7")
        handler.set_conf("SearchN", "5")
        handler.set_conf("FilterStr", "会議")
        handler.on_finish()

    save.assert_called_once()

    handler2 = make_handler(make_app(datadir), HandlerBase)
    assert handler2.get_conf("ToDo_Days") == "7"
    assert handler2.get_conf("SearchN") == "5"
    assert handler2.get_conf("FilterStr") == "会議"


def test_conf_save_failure_does_not_break_next_request(datadir):
    """``save_if_dirty()`` の書き込みが失敗しても、例外を外へ出さず、
    次のリクエスト以降が止まらない（``ConfFile`` はプロセスで 1 つを
    共有するので、``_dirty`` が ``True`` のまま残ると ``refresh()`` も
    ``on_finish()`` の再試行も以後ずっと止まる。TODO-090）。
    """
    handler = make_handler(make_app(datadir), HandlerBase)
    handler.set_conf("ToDo_Days", "7")

    with mock.patch.object(
        handler._conf, "_save", side_effect=PermissionError("denied")
    ):
        handler.on_finish()  # 例外が外へ出ない

    assert handler._conf._dirty is False

    # 変更が無ければ、そもそも ``_save()`` は呼ばれない
    with mock.patch.object(handler._conf, "_save") as save:
        handler.on_finish()
    save.assert_not_called()

    # ``_dirty`` が ``False`` に戻っているので、外部の書き換えを
    # 次のリクエストで読み直せる（止まっていない）
    conf_path = datadir / CONF_FNAME
    conf_path.write_text('{"ToDo_Days": "30"}', encoding="utf-8")
    st = os.stat(conf_path)
    os.utime(conf_path, (st.st_atime + 10, st.st_mtime + 10))

    handler2 = make_handler(make_app(datadir), HandlerBase)
    assert handler2.get_conf("ToDo_Days") == "30"


def test_load_conf_empty_value(datadir):
    """値が空文字列でも読める。"""
    (datadir / CONF_FNAME).write_text('{"SearchStr": ""}', encoding="utf-8")

    handler = make_handler(make_app(datadir), HandlerBase)

    assert handler.get_conf(HandlerBase.CONF_KEY_SEARCH_STR) == ""


def test_conf_round_trip_value_with_tab_and_newline(datadir):
    """タブや改行を含む値も、そのまま往復する（TODO-032）。"""
    handler = make_handler(make_app(datadir), HandlerBase)
    handler.set_conf(HandlerBase.CONF_KEY_SEARCH_STR, "a\tb\nc")
    handler.on_finish()

    handler2 = make_handler(make_app(datadir), HandlerBase)
    assert handler2.get_conf(HandlerBase.CONF_KEY_SEARCH_STR) == "a\tb\nc"


def test_load_conf_broken_json(datadir):
    """JSON として壊れていても例外にせず、空の設定として扱う。

    設定ファイルが壊れて画面が出ないほうが困るので、不正な正規表現
    （TODO-012）・不正な引数（TODO-027）と同じ扱いにする（TODO-032）。
    """
    (datadir / CONF_FNAME).write_text('{"ToDo_Days": ', encoding="utf-8")

    handler = make_handler(make_app(datadir), HandlerBase)

    assert handler._conf.to_dict() == {}


def test_load_conf_invalid_encoding(datadir):
    """utf-8 で読めなくても、空の設定として扱う。

    旧 ``Conf.cgi``（euc_jp のことがある）を手で ``conf.json`` に
    しただけ、といった場合に踏む（TODO-032）。
    """
    (datadir / CONF_FNAME).write_bytes(
        '{"FilterStr": "会議"}'.encode("euc_jp")
    )

    handler = make_handler(make_app(datadir), HandlerBase)

    assert handler._conf.to_dict() == {}


def test_load_conf_not_object(datadir):
    """トップレベルが dict でなければ、空の設定として扱う。"""
    (datadir / CONF_FNAME).write_text(
        '["ToDo_Days", "365"]', encoding="utf-8"
    )

    handler = make_handler(make_app(datadir), HandlerBase)

    assert handler._conf.to_dict() == {}


def test_load_conf_non_string_value(datadir):
    """値が文字列でないキーだけを飛ばして、他のキーは読める。"""
    (datadir / CONF_FNAME).write_text(
        '{"ToDo_Days": 365, "FilterStr": "会議"}', encoding="utf-8"
    )

    handler = make_handler(make_app(datadir), HandlerBase)

    assert handler._conf.to_dict() == {"FilterStr": "会議"}


C_LOCALE_CONF_SCRIPT = """\
import sys

from helpers import make_app, make_handler
from ytsched.handler import HandlerBase

datadir = sys.argv[1]

handler = make_handler(make_app(datadir), HandlerBase)
handler.set_conf(HandlerBase.CONF_KEY_SEARCH_STR, '会議')
handler.on_finish()

handler2 = make_handler(make_app(datadir), HandlerBase)
value = handler2.get_conf(HandlerBase.CONF_KEY_SEARCH_STR)
assert value == '会議', value
"""


def test_conf_is_not_locale_dependent(tmp_path, datadir):
    """``LC_ALL=C`` でも、日本語の設定を保存・読み込みできる。"""
    res = run_in_c_locale(tmp_path, C_LOCALE_CONF_SCRIPT, datadir)

    assert res.returncode == 0, res.stderr
    assert (datadir / CONF_FNAME).read_text(
        encoding="utf-8"
    ) == '{\n  "SearchStr": "会議"\n}\n'


#
# import 時の副作用
#
def test_import_prints_nothing():
    """``import`` しただけで標準出力に何か出てはいけない。"""
    result = subprocess.run(
        [sys.executable, "-c", "import ytsched.main_handler"],
        capture_output=True,
        text=True,
        check=True,
    )

    assert result.stdout == ""

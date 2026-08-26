#
# (c) 2026 Yoichi Tanibayashi
#
"""HandlerBase（conf.json の読み書き）と days2x_percent のテスト"""

import json
import os
import subprocess
import sys

import pytest
from helpers import URL_PREFIX, make_app, make_handler, run_in_c_locale

from ytsched.handler import HandlerBase
from ytsched.main_handler import DAYS_YEAR, days2x_percent

CONF_FNAME = HandlerBase.CONF_FNAME


@pytest.fixture
def datadir(tmp_path):
    path = tmp_path / "data"
    path.mkdir()
    return path


def test_settings_are_read(datadir):
    """``app.settings`` から読む値（TODO-021 のゴールデンマスターテスト）。

    ``HandlerBase.__init__`` を整理しても、この 7 つは変わらない。
    ``_days`` は TODO-049 で ``--days`` を消したときに落ちた。
    """
    app = make_app(datadir)

    handler = make_handler(app, HandlerBase)

    assert handler._title == "Ytsched"
    assert handler._author == "Yoichi Tanibayashi"
    assert handler._version == "0.0.0"
    assert handler._url_prefix == URL_PREFIX + "/"
    assert handler._datadir == str(datadir)
    assert handler._sd is app.settings["sd"]
    assert handler._conf_file == os.path.join(str(datadir), CONF_FNAME)


def test_load_conf_no_file(datadir):
    handler = make_handler(make_app(datadir), HandlerBase)

    assert handler._conf == {}
    assert handler.get_conf(HandlerBase.CONF_KEY_TODO_DAYS) is None


def test_load_conf(datadir):
    (datadir / CONF_FNAME).write_text(
        '{"ToDo_Days": "365", "FilterStr": "会議"}', encoding="utf-8"
    )

    handler = make_handler(make_app(datadir), HandlerBase)

    assert handler.get_conf(HandlerBase.CONF_KEY_TODO_DAYS) == "365"
    assert handler.get_conf(HandlerBase.CONF_KEY_FILTER_STR) == "会議"
    assert handler.get_conf("NoSuchKey") is None


def test_save_conf_is_json(datadir):
    """JSON で書き出す（TODO-032）。人が読める形にする。"""
    handler = make_handler(make_app(datadir), HandlerBase)
    handler.set_conf(HandlerBase.CONF_KEY_SEARCH_STR, "会議")

    text = (datadir / CONF_FNAME).read_text(encoding="utf-8")
    assert text == '{\n  "SearchStr": "会議"\n}\n'
    assert json.loads(text) == {"SearchStr": "会議"}


def test_conf_round_trip(datadir):
    app = make_app(datadir)

    handler = make_handler(app, HandlerBase)
    handler.set_conf(HandlerBase.CONF_KEY_TODO_DAYS, "30")
    handler.set_conf(HandlerBase.CONF_KEY_SEARCH_N, "5")

    handler2 = make_handler(app, HandlerBase)
    assert handler2.get_conf(HandlerBase.CONF_KEY_TODO_DAYS) == "30"
    assert handler2.get_conf(HandlerBase.CONF_KEY_SEARCH_N) == "5"


def test_set_conf_overwrite(datadir):
    app = make_app(datadir)

    handler = make_handler(app, HandlerBase)
    handler.set_conf(HandlerBase.CONF_KEY_TODO_DAYS, "30")
    handler.set_conf(HandlerBase.CONF_KEY_TODO_DAYS, "7")

    handler2 = make_handler(app, HandlerBase)
    assert handler2.get_conf(HandlerBase.CONF_KEY_TODO_DAYS) == "7"


def test_load_conf_empty_value(datadir):
    """値が空文字列でも読める。"""
    (datadir / CONF_FNAME).write_text('{"SearchStr": ""}', encoding="utf-8")

    handler = make_handler(make_app(datadir), HandlerBase)

    assert handler.get_conf(HandlerBase.CONF_KEY_SEARCH_STR) == ""


def test_conf_round_trip_value_with_tab_and_newline(datadir):
    """タブや改行を含む値も、そのまま往復する（TODO-032）。"""
    app = make_app(datadir)

    handler = make_handler(app, HandlerBase)
    handler.set_conf(HandlerBase.CONF_KEY_SEARCH_STR, "a\tb\nc")

    handler2 = make_handler(app, HandlerBase)
    assert handler2.get_conf(HandlerBase.CONF_KEY_SEARCH_STR) == "a\tb\nc"


def test_load_conf_broken_json(datadir):
    """JSON として壊れていても例外にせず、空の設定として扱う。

    設定ファイルが壊れて画面が出ないほうが困るので、不正な正規表現
    （TODO-012）・不正な引数（TODO-027）と同じ扱いにする（TODO-032）。
    """
    (datadir / CONF_FNAME).write_text('{"ToDo_Days": ', encoding="utf-8")

    handler = make_handler(make_app(datadir), HandlerBase)

    assert handler._conf == {}


def test_load_conf_invalid_encoding(datadir):
    """utf-8 で読めなくても、空の設定として扱う。

    旧 ``Conf.cgi``（euc_jp のことがある）を手で ``conf.json`` に
    しただけ、といった場合に踏む（TODO-032）。
    """
    (datadir / CONF_FNAME).write_bytes(
        '{"FilterStr": "会議"}'.encode("euc_jp")
    )

    handler = make_handler(make_app(datadir), HandlerBase)

    assert handler._conf == {}


def test_load_conf_not_object(datadir):
    """トップレベルが dict でなければ、空の設定として扱う。"""
    (datadir / CONF_FNAME).write_text(
        '["ToDo_Days", "365"]', encoding="utf-8"
    )

    handler = make_handler(make_app(datadir), HandlerBase)

    assert handler._conf == {}


def test_load_conf_non_string_value(datadir):
    """値が文字列でないキーだけを飛ばして、他のキーは読める。"""
    (datadir / CONF_FNAME).write_text(
        '{"ToDo_Days": 365, "FilterStr": "会議"}', encoding="utf-8"
    )

    handler = make_handler(make_app(datadir), HandlerBase)

    assert handler._conf == {"FilterStr": "会議"}


C_LOCALE_CONF_SCRIPT = """\
import sys

from helpers import make_app, make_handler
from ytsched.handler import HandlerBase

datadir = sys.argv[1]

handler = make_handler(make_app(datadir), HandlerBase)
handler.set_conf(HandlerBase.CONF_KEY_SEARCH_STR, '会議')

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
# days2x_percent()
#
def test_days2x_percent_zero():
    assert days2x_percent(0) == 0.0


def test_days2x_percent_sign():
    assert days2x_percent(7) == pytest.approx(-days2x_percent(-7))
    assert days2x_percent(7) > 0
    assert days2x_percent(-7) < 0


def test_days2x_percent_is_monotonic():
    values = [days2x_percent(d) for d in [1, 3, 7, 30, 365]]
    assert values == sorted(values)


def test_days2x_percent_clamps_at_30y():
    """±30y がゲージの端 (50) になる。"""
    assert days2x_percent(DAYS_YEAR * 30) == pytest.approx(50.0)
    assert days2x_percent(-DAYS_YEAR * 30) == pytest.approx(-50.0)


def test_days2x_percent_stays_clamped_beyond_30y():
    """30y より先の日付でも、端 (50) で頭打ちのまま。"""
    assert days2x_percent(DAYS_YEAR * 60) == pytest.approx(50.0)
    assert days2x_percent(-DAYS_YEAR * 60) == pytest.approx(-50.0)


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

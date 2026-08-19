#
# (c) 2026 Yoichi Tanibayashi
#
"""HandlerBase（Conf.cgi の読み書き）と days2y_offset のテスト"""
import subprocess
import sys

import pytest

from helpers import make_app, make_handler
from ytsched.handler import HandlerBase
from ytsched.main_handler import days2y_offset

CONF_FNAME = HandlerBase.CONF_FNAME


@pytest.fixture
def datadir(tmp_path):
    path = tmp_path / 'data'
    path.mkdir()
    return path


def test_load_conf_no_file(datadir):
    handler = make_handler(make_app(datadir), HandlerBase)

    assert handler._conf == {}
    assert handler.get_conf(HandlerBase.CONF_KEY_TODO_DAYS) is None


def test_load_conf(datadir):
    (datadir / CONF_FNAME).write_text(
        'ToDo_Days\t365\nFilterStr\t会議\n', encoding='utf-8')

    handler = make_handler(make_app(datadir), HandlerBase)

    assert handler.get_conf(HandlerBase.CONF_KEY_TODO_DAYS) == '365'
    assert handler.get_conf(HandlerBase.CONF_KEY_FILTER_STR) == '会議'
    assert handler.get_conf('NoSuchKey') is None


def test_save_conf_is_tab_separated(datadir):
    handler = make_handler(make_app(datadir), HandlerBase)
    handler.set_conf(HandlerBase.CONF_KEY_SEARCH_STR, '会議')

    text = (datadir / CONF_FNAME).read_text(encoding='utf-8')
    assert text == 'SearchStr\t会議\n'


def test_conf_round_trip(datadir):
    app = make_app(datadir)

    handler = make_handler(app, HandlerBase)
    handler.set_conf(HandlerBase.CONF_KEY_TODO_DAYS, '30')
    handler.set_conf(HandlerBase.CONF_KEY_SEARCH_N, '5')

    handler2 = make_handler(app, HandlerBase)
    assert handler2.get_conf(HandlerBase.CONF_KEY_TODO_DAYS) == '30'
    assert handler2.get_conf(HandlerBase.CONF_KEY_SEARCH_N) == '5'


def test_set_conf_overwrite(datadir):
    app = make_app(datadir)

    handler = make_handler(app, HandlerBase)
    handler.set_conf(HandlerBase.CONF_KEY_TODO_DAYS, '30')
    handler.set_conf(HandlerBase.CONF_KEY_TODO_DAYS, '7')

    handler2 = make_handler(app, HandlerBase)
    assert handler2.get_conf(HandlerBase.CONF_KEY_TODO_DAYS) == '7'


def test_load_conf_empty_value(datadir):
    """値が空文字列の行も読める。"""
    (datadir / CONF_FNAME).write_text('SearchStr\t\n', encoding='utf-8')

    handler = make_handler(make_app(datadir), HandlerBase)

    assert handler.get_conf(HandlerBase.CONF_KEY_SEARCH_STR) == ''


@pytest.mark.xfail(reason='TODO-005 で直す', strict=True)
def test_load_conf_empty_line(datadir):
    """空行があっても、他の行は読める。

    ``if line:`` は ``'\n'`` を真と判定するので、空行でも
    ``split('\t')`` されて ``ValueError`` になる。
    """
    (datadir / CONF_FNAME).write_text(
        'ToDo_Days\t365\n\n', encoding='utf-8')

    handler = make_handler(make_app(datadir), HandlerBase)

    assert handler.get_conf(HandlerBase.CONF_KEY_TODO_DAYS) == '365'


@pytest.mark.xfail(reason='TODO-005 で直す', strict=True)
def test_load_conf_line_without_tab(datadir):
    """タブの無い行があっても、他の行は読める。"""
    (datadir / CONF_FNAME).write_text(
        'ToDo_Days\t365\nbroken\n', encoding='utf-8')

    handler = make_handler(make_app(datadir), HandlerBase)

    assert handler.get_conf(HandlerBase.CONF_KEY_TODO_DAYS) == '365'


#
# days2y_offset()
#
def test_days2y_offset_zero():
    assert days2y_offset(0) == 0


def test_days2y_offset_sign():
    assert days2y_offset(7) == 62
    assert days2y_offset(-7) == -62


def test_days2y_offset_is_monotonic():
    values = [days2y_offset(d) for d in [1, 3, 7, 30, 365]]
    assert values == sorted(values)


#
# import 時の副作用
#
@pytest.mark.xfail(reason='TODO-005 で直す', strict=True)
def test_import_prints_nothing():
    """``import`` しただけで標準出力に何か出てはいけない。"""
    result = subprocess.run(
        [sys.executable, '-c', 'import ytsched.main_handler'],
        capture_output=True, text=True, check=True)

    assert result.stdout == ''

#
# (c) 2026 ytani01
#
import io

import pytest
from loguru import logger

from ytsched import mylog
from ytsched.mylog import getLogger, loggerInit, setLevel


@pytest.fixture(autouse=True)
def _clean_logger():
    """loguru と水準のグローバル状態をテストごとにリセットする。"""
    yield
    logger.remove()
    mylog._levels.clear()
    mylog._levels[""] = 0


def test_default_level_is_info(monkeypatch):
    out = io.StringIO()
    loggerInit(debug=False, out=out)

    _log = getLogger("Foo")
    _log.debug("debug message")
    _log.info("info message")

    text = out.getvalue()
    assert "debug message" not in text
    assert "info message" in text


def test_debug_flag_enables_debug():
    out = io.StringIO()
    loggerInit(debug=True, out=out)

    _log = getLogger("Foo")
    _log.debug("debug message")

    assert "debug message" in out.getvalue()


def test_unbound_logger_uses_default_level():
    out = io.StringIO()
    loggerInit(debug=True, out=out)

    logger.debug("plain logger message")

    assert "plain logger message" in out.getvalue()


def test_getLogger_level_overrides_default():
    out = io.StringIO()

    _log_loud = getLogger("Loud", "DEBUG")
    _log_quiet = getLogger("Quiet")
    loggerInit(debug=False, out=out)

    _log_loud.debug("loud debug")
    _log_quiet.debug("quiet debug")

    text = out.getvalue()
    assert "loud debug" in text
    assert "quiet debug" not in text


def test_getLogger_level_survives_loggerInit():
    """getLogger() の指定は、後から呼ばれた loggerInit() でも消えない。"""
    out = io.StringIO()

    _log = getLogger("Loud", "DEBUG")
    loggerInit(debug=False, out=out)

    _log.debug("loud debug")

    assert "loud debug" in out.getvalue()


def test_setLevel_overrides_default():
    out = io.StringIO()

    _log = getLogger("Quiet")
    setLevel("Quiet", "ERROR")
    loggerInit(debug=False, out=out)

    _log.info("quiet info")
    _log.error("quiet error")

    text = out.getvalue()
    assert "quiet info" not in text
    assert "quiet error" in text


def test_setLevel_none_restores_default():
    out = io.StringIO()

    _log = getLogger("Quiet")
    setLevel("Quiet", "ERROR")
    setLevel("Quiet", None)
    loggerInit(debug=False, out=out)

    _log.info("quiet info")

    assert "quiet info" in out.getvalue()


def test_setLevel_none_on_unset_name_is_noop():
    setLevel("NeverSet", None)

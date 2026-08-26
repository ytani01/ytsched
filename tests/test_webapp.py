#
# (c) 2026 ytani01
#
"""WebServer が組み立てる Application の設定のテスト"""

import json
import os

import pytest

from ytsched.webapp import WebServer


@pytest.fixture
def svr(tmp_path):
    """listen しない ``WebServer``"""
    return WebServer(datadir=str(tmp_path / "data"))


def test_datadir_is_made(tmp_path):
    WebServer(datadir=str(tmp_path / "data"))

    assert (tmp_path / "data").is_dir()


def test_app_settings(svr, tmp_path):
    settings = svr._app.settings

    assert settings["datadir"] == str(tmp_path / "data")
    assert settings["url_prefix"] == WebServer.DEF_URL_PREFIX + "/"
    assert settings["debug"] is False
    assert settings["static_url_prefix"] == (
        WebServer.DEF_URL_PREFIX + "/static/"
    )


def test_webroot_is_bundled(svr):
    """テンプレートと静的ファイルはパッケージに同梱されている。"""
    settings = svr._app.settings

    assert os.path.isfile(
        os.path.join(settings["template_path"], "main.html")
    )
    assert os.path.isfile(
        os.path.join(settings["static_path"], "favicon.ico")
    )


def test_manifest_and_icons_are_bundled(svr):
    """manifest.json とアイコンがパッケージに同梱されている（TODO-039）。"""
    static_path = svr._app.settings["static_path"]

    for name in [
        "manifest.json",
        "favicon.ico",
        "icons/icon.svg",
        "icons/icon-192.png",
        "icons/icon-512.png",
        "icons/icon-maskable-512.png",
        "icons/apple-touch-icon.png",
    ]:
        assert os.path.isfile(os.path.join(static_path, name)), name


def test_manifest_content(svr):
    """manifest.json の中身（TODO-039）。"""
    static_path = svr._app.settings["static_path"]

    with open(
        os.path.join(static_path, "manifest.json"), encoding="utf-8"
    ) as f:
        manifest = json.load(f)

    # ``--urlprefix`` を変えても付いてくるよう、相対で書いている
    assert manifest["start_url"] == "../"
    assert manifest["scope"] == "../"

    for icon in manifest["icons"]:
        assert os.path.isfile(os.path.join(static_path, icon["src"]))


def test_datadir_is_expanded(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))

    svr = WebServer(datadir="~/ytsched_test/data")

    assert svr._app.settings["datadir"] == str(tmp_path / "ytsched_test/data")


def test_autoreload_is_not_forced(svr):
    """``autoreload`` は固定でなく、``debug`` のときだけ有効になる。"""
    assert not svr._app.settings.get("autoreload")


def test_autoreload_with_debug(tmp_path):
    svr = WebServer(datadir=str(tmp_path / "data"), debug=True)

    assert svr._app.settings.get("autoreload") is True

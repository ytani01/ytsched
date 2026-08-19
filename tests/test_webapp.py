#
# (c) 2026 Yoichi Tanibayashi
#
"""WebServer が組み立てる Application の設定のテスト"""
import os

import pytest

from ytsched.main_handler import MainHandler
from ytsched.webapp import WebServer


@pytest.fixture
def svr(tmp_path):
    """listen しない ``WebServer``"""
    return WebServer(datadir=str(tmp_path / 'data'))


def test_datadir_is_made(tmp_path):
    WebServer(datadir=str(tmp_path / 'data'))

    assert (tmp_path / 'data').is_dir()


def test_app_settings(svr, tmp_path):
    settings = svr._app.settings

    assert settings['datadir'] == str(tmp_path / 'data')
    assert settings['url_prefix'] == WebServer.URL_PREFIX + '/'
    assert settings['days'] == MainHandler.DEF_DAYS
    assert settings['debug'] is False
    assert settings['static_url_prefix'] == (
        WebServer.URL_PREFIX + '/static/')


def test_webroot_is_bundled(svr):
    """テンプレートと静的ファイルはパッケージに同梱されている。"""
    settings = svr._app.settings

    assert os.path.isfile(
        os.path.join(settings['template_path'], 'main.html'))
    assert os.path.isfile(
        os.path.join(settings['static_path'], 'favicon.ico'))


def test_datadir_is_expanded(tmp_path, monkeypatch):
    monkeypatch.setenv('HOME', str(tmp_path))

    svr = WebServer(datadir='~/ytsched_test/data')

    assert svr._app.settings['datadir'] == str(
        tmp_path / 'ytsched_test/data')


@pytest.mark.xfail(reason='TODO-005 で直す', strict=True)
def test_autoreload_is_not_forced(svr):
    """``autoreload`` が ``True`` に固定されている。"""
    assert not svr._app.settings.get('autoreload')

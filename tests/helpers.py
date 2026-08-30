#
# (c) 2026 ytani01
#
"""テスト用の共通部品

``webapp.WebServer`` が組み立てているのと同じ ``Application`` を、
``datadir`` だけ差し替えて作る。
"""

import os
import subprocess
import sys
import weakref
from pathlib import Path
from unittest import mock

import tornado.httputil
import tornado.web

from ytsched.conf import ConfFile
from ytsched.edit_handler import EditHandler
from ytsched.handler import AppInfo
from ytsched.main_handler import MainHandler
from ytsched.trash_handler import TrashHandler
from ytsched.webapp import WebServer
from ytsched.ytsched import SchedData

URL_PREFIX = WebServer.DEF_URL_PREFIX

# ``make_app()`` が作った ``SchedData``/``ConfFile`` を、``app`` から
# 引けるようにする (TODO-081・TODO-090)。どちらも ``app.settings`` に無く
# （``webapp.py`` と同じく ``URLSpec`` の kwargs で ``initialize()`` へ
# 渡す）、``tornado.web.Application`` に無い属性を動的に生やす代わりに
# こちらへ持つ。
_APP_SD: weakref.WeakKeyDictionary[tornado.web.Application, SchedData] = (
    weakref.WeakKeyDictionary()
)
_APP_CONF: weakref.WeakKeyDictionary[tornado.web.Application, ConfFile] = (
    weakref.WeakKeyDictionary()
)
_APP_INFO: weakref.WeakKeyDictionary[tornado.web.Application, AppInfo] = (
    weakref.WeakKeyDictionary()
)


def make_app(datadir):
    """テスト用の ``tornado.web.Application`` を作る。

    ``autoreload`` は付けない（テストでは邪魔になるため。
    ``webapp.py`` 側は ``debug`` のときだけ有効になる）。
    """
    datadir = str(datadir)
    webroot = WebServer.DEF_WEBROOT
    sd = SchedData(datadir)
    conf = ConfFile(Path(datadir) / ConfFile.FNAME)
    app_info = AppInfo(
        title="Ytsched",
        author="ytani01",
        version="0.0.0",
        url_prefix=URL_PREFIX + "/",
        datadir=datadir,
    )

    handler_kwargs = {"sd": sd, "app_info": app_info, "conf": conf}

    app = tornado.web.Application(
        [
            (r"/", MainHandler, handler_kwargs),
            (URL_PREFIX, MainHandler, handler_kwargs),
            (rf"{URL_PREFIX}/", MainHandler, handler_kwargs),
            (rf"{URL_PREFIX}/edit", EditHandler, handler_kwargs),
            (rf"{URL_PREFIX}/edit/", EditHandler, handler_kwargs),
            (rf"{URL_PREFIX}/trash", TrashHandler, handler_kwargs),
            (rf"{URL_PREFIX}/trash/", TrashHandler, handler_kwargs),
        ],
        static_path=Path(webroot) / "static",
        static_url_prefix=URL_PREFIX + "/static/",
        template_path=Path(webroot) / "templates",
        debug=False,
    )
    _APP_SD[app] = sd
    _APP_CONF[app] = conf
    _APP_INFO[app] = app_info
    return app


def app_sd(app: tornado.web.Application) -> SchedData:
    """``make_app(app)`` が使った ``SchedData`` を返す（TODO-081）。"""
    return _APP_SD[app]


def app_conf(app: tornado.web.Application) -> ConfFile:
    """``make_app(app)`` が使った ``ConfFile`` を返す（TODO-090）。"""
    return _APP_CONF[app]


def app_info(app: tornado.web.Application) -> AppInfo:
    """``make_app(app)`` が使った ``AppInfo`` を返す（TODO-090）。"""
    return _APP_INFO[app]


def make_handler(app, handler_class, uri=URL_PREFIX + "/"):
    """リクエストを実際に送らずに handler を作る。

    ``HandlerBase`` の ``get_conf()`` などを直に試すために使う。
    ``sd``/``app_info``/``conf`` は ``make_app()`` が作ったものを
    ``initialize()`` へ渡す。
    """
    req = tornado.httputil.HTTPServerRequest(
        method="GET", uri=uri, connection=mock.Mock()
    )
    return handler_class(
        app,
        req,
        sd=app_sd(app),
        app_info=app_info(app),
        conf=app_conf(app),
    )


def run_in_c_locale(tmp_path, script, *args):
    """ASCII ロケール（``LC_ALL=C``）で Python スクリプトを実行する。

    ``open()`` に ``encoding=`` が無いとロケール依存になるので、
    日本語の読み書きがロケールに依らないことを確かめるために使う。
    UTF-8 モードと、C ロケールの自動置き換え（C.UTF-8）は無効にする。

    Returns
    -------
    subprocess.CompletedProcess
    """
    script_path = tmp_path / "_c_locale_script.py"
    script_path.write_text(script, encoding="utf-8")

    env = dict(
        os.environ,
        LC_ALL="C",
        PYTHONUTF8="0",
        PYTHONCOERCECLOCALE="0",
        PYTHONPATH=str(Path(__file__).resolve().parent),
    )

    return subprocess.run(
        [sys.executable, str(script_path)] + [str(a) for a in args],
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )

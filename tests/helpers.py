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
from unittest import mock

import tornado.httputil
import tornado.web

from ytsched.edit_handler import EditHandler
from ytsched.main_handler import MainHandler
from ytsched.webapp import WebServer
from ytsched.ytsched import SchedData

URL_PREFIX = WebServer.DEF_URL_PREFIX

# ``make_app()`` が作った ``SchedData`` を、``app`` から引けるようにする
# (TODO-081)。``sd`` はもう ``app.settings`` に無い（``webapp.py`` と同じく
# ``URLSpec`` の kwargs で ``initialize()`` へ渡す）ので、
# ``tornado.web.Application`` に無い属性を動的に生やす代わりにこちらへ持つ。
_APP_SD: weakref.WeakKeyDictionary[tornado.web.Application, SchedData] = (
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

    app = tornado.web.Application(
        [
            (r"/", MainHandler, {"sd": sd}),
            (URL_PREFIX, MainHandler, {"sd": sd}),
            (rf"{URL_PREFIX}/", MainHandler, {"sd": sd}),
            (rf"{URL_PREFIX}/edit", EditHandler, {"sd": sd}),
            (rf"{URL_PREFIX}/edit/", EditHandler, {"sd": sd}),
        ],
        static_path=os.path.join(webroot, "static"),
        static_url_prefix=URL_PREFIX + "/static/",
        template_path=os.path.join(webroot, "templates"),
        title="Ytsched",
        author="ytani01",
        version="0.0.0",
        url_prefix=URL_PREFIX + "/",
        datadir=datadir,
        debug=False,
    )
    _APP_SD[app] = sd
    return app


def app_sd(app: tornado.web.Application) -> SchedData:
    """``make_app(app)`` が使った ``SchedData`` を返す（TODO-081）。"""
    return _APP_SD[app]


def make_handler(app, handler_class, uri=URL_PREFIX + "/"):
    """リクエストを実際に送らずに handler を作る。

    ``HandlerBase`` の ``load_conf()`` などを直に試すために使う。
    ``sd`` は ``make_app()`` が作ったものを ``initialize()`` へ渡す。
    """
    req = tornado.httputil.HTTPServerRequest(
        method="GET", uri=uri, connection=mock.Mock()
    )
    return handler_class(app, req, sd=app_sd(app))


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
        PYTHONPATH=os.path.dirname(os.path.abspath(__file__)),
    )

    return subprocess.run(
        [sys.executable, str(script_path)] + [str(a) for a in args],
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )

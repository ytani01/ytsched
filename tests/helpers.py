#
# (c) 2026 Yoichi Tanibayashi
#
"""テスト用の共通部品

``webapp.WebServer`` が組み立てているのと同じ ``Application`` を、
``datadir`` だけ差し替えて作る。
"""

import os
import subprocess
import sys
from unittest import mock

import tornado.httputil
import tornado.web

from ytsched.edit_handler import EditHandler
from ytsched.main_handler import MainHandler
from ytsched.webapp import WebServer
from ytsched.ytsched import SchedData

URL_PREFIX = WebServer.URL_PREFIX


def make_app(datadir, days=MainHandler.DEF_DAYS):
    """テスト用の ``tornado.web.Application`` を作る。

    ``autoreload`` は付けない（テストでは邪魔になるため。
    ``webapp.py`` 側は ``debug`` のときだけ有効になる）。
    """
    datadir = str(datadir)
    webroot = WebServer.DEF_WEBROOT

    return tornado.web.Application(
        [
            (r"/", MainHandler),
            (r"%s" % URL_PREFIX, MainHandler),
            (r"%s/" % URL_PREFIX, MainHandler),
            (r"%s/edit" % URL_PREFIX, EditHandler),
            (r"%s/edit/" % URL_PREFIX, EditHandler),
        ],
        static_path=os.path.join(webroot, "static"),
        static_url_prefix=URL_PREFIX + "/static/",
        template_path=os.path.join(webroot, "templates"),
        title="Ytsched",
        author="Yoichi Tanibayashi",
        version="0.0.0",
        url_prefix=URL_PREFIX + "/",
        datadir=datadir,
        days=days,
        sd=SchedData(datadir),
        debug=False,
    )


def make_handler(app, handler_class, uri=URL_PREFIX + "/"):
    """リクエストを実際に送らずに handler を作る。

    ``HandlerBase`` の ``load_conf()`` などを直に試すために使う。
    """
    req = tornado.httputil.HTTPServerRequest(
        method="GET", uri=uri, connection=mock.Mock()
    )
    return handler_class(app, req)


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

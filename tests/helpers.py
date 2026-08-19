#
# (c) 2026 Yoichi Tanibayashi
#
"""テスト用の共通部品

``webapp.WebServer`` が組み立てているのと同じ ``Application`` を、
``datadir`` だけ差し替えて作る。
"""
import os
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
    ``webapp.py`` 側の ``autoreload=True`` は TODO-005 の範囲）。
    """
    datadir = str(datadir)
    webroot = WebServer.DEF_WEBROOT

    return tornado.web.Application(
        [
            (r'/', MainHandler),
            (r'%s' % URL_PREFIX, MainHandler),
            (r'%s/' % URL_PREFIX, MainHandler),

            (r'%s/edit' % URL_PREFIX, EditHandler),
            (r'%s/edit/' % URL_PREFIX, EditHandler),
        ],
        static_path=os.path.join(webroot, 'static'),
        static_url_prefix=URL_PREFIX + '/static/',
        template_path=os.path.join(webroot, 'templates'),

        title='Ytsched',
        author='Yoichi Tanibayashi',
        version='0.0.0',

        url_prefix=URL_PREFIX + '/',

        datadir=datadir,
        days=days,
        sd=SchedData(datadir),

        debug=False,
    )


def make_handler(app, handler_class, uri=URL_PREFIX + '/'):
    """リクエストを実際に送らずに handler を作る。

    ``HandlerBase`` の ``load_conf()`` などを直に試すために使う。
    """
    req = tornado.httputil.HTTPServerRequest(
        method='GET', uri=uri, connection=mock.Mock())
    return handler_class(app, req)

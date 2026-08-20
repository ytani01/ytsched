#!/usr/bin/env python3
#
# (c) 2020 Yoichi Tanibayashi
#
"""
Web Interface
"""

__author__ = "Yoichi Tanibayashi"
__date__ = "2021/01"

import os
import sys

import tornado.httpserver
import tornado.ioloop
import tornado.web

from . import __author__ as AUTHOR
from . import __prog_name__ as PROG_NAME
from . import __version__ as VERSION
from .edit_handler import EditHandler
from .main_handler import MainHandler
from .mylog import getLogger
from .ytsched import SchedData


class WebServer:
    """
    Web application server
    """

    __log = getLogger(__qualname__)

    URL_PREFIX = "/ytsched"

    DEF_PORT = 10085
    # パッケージに同梱した webroot（templates/, static/）
    DEF_WEBROOT = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "webroot"
    )
    DEF_WORKDIR = os.path.expanduser("~/ytsched")
    DEF_DATADIR = os.path.join(DEF_WORKDIR, "data")

    DEF_SIZE_LIMIT = 100 * 1024 * 1024  # 100MB

    def __init__(
        self,
        port: int = DEF_PORT,
        webroot: str = DEF_WEBROOT,
        datadir: str = DEF_DATADIR,
        days: int = MainHandler.DEF_DAYS,
        size_limit: int = DEF_SIZE_LIMIT,
        version: bool = False,
        debug: bool = False,
    ):
        """Constructor

        Parameters
        ----------
        port: int
            port number
        webroot: str

        datadir: str

        days: int

        size_limit: int
            max upload size

        version: bool
        """
        self._dbg = debug
        self.__log.debug(
            f"port={port}, webroot={webroot}, datadir={datadir}, days={days}"
        )
        self.__log.debug(f"size_limit={size_limit}")

        self._port = port
        self._webroot = os.path.expanduser(webroot)
        self._datadir = os.path.expanduser(datadir)
        self._sd = SchedData(self._datadir)
        self._days = days
        self._size_limit = size_limit

        if version:
            print("%s %s by %s" % (PROG_NAME, VERSION, AUTHOR))
            sys.exit(0)

        os.makedirs(self._datadir, exist_ok=True)

        self._app = tornado.web.Application(
            [
                (r"/", MainHandler),
                (r"%s" % self.URL_PREFIX, MainHandler),
                (r"%s/" % self.URL_PREFIX, MainHandler),
                (r"%s/edit" % self.URL_PREFIX, EditHandler),
                (r"%s/edit/" % self.URL_PREFIX, EditHandler),
            ],
            static_path=os.path.join(self._webroot, "static"),
            static_url_prefix=self.URL_PREFIX + "/static/",
            template_path=os.path.join(self._webroot, "templates"),
            autoreload=self._dbg,
            title=PROG_NAME,
            author=AUTHOR,
            version=VERSION,
            url_prefix=self.URL_PREFIX + "/",
            datadir=self._datadir,
            days=self._days,
            sd=self._sd,
            debug=self._dbg,
        )
        self.__log.debug(f"app={self._app.__dict__}")

        self._svr = tornado.httpserver.HTTPServer(
            self._app, max_buffer_size=self._size_limit
        )
        self.__log.debug(f"svr={self._svr.__dict__}")

    def main(self):
        """main"""
        self.__log.debug("")

        self._svr.listen(self._port)
        self.__log.info("start server: run forever ..")

        tornado.ioloop.IOLoop.current().start()

        self.__log.debug("done")

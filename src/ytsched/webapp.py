#
# (c) 2026 ytani01
#
"""
Web Interface
"""

__author__ = "ytani01"
__date__ = "2021/01"

import os

import tornado.httpserver
import tornado.ioloop
import tornado.web

from . import __author__ as AUTHOR
from . import __prog_name__ as PROG_NAME
from . import __version__ as VERSION
from .conf import ConfFile
from .edit_handler import EditHandler
from .handler import AppInfo
from .main_handler import MainHandler
from .mylog import getLogger
from .ytsched import SchedData


class WebServer:
    """
    Web application server
    """

    __log = getLogger(__qualname__)

    DEF_URL_PREFIX = "/ytsched"

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
        url_prefix: str = DEF_URL_PREFIX,
        size_limit: int = DEF_SIZE_LIMIT,
        debug: bool = False,
    ):
        """Constructor

        Parameters
        ----------
        port: int
            port number
        webroot: str

        datadir: str

        url_prefix: str

        size_limit: int
            max upload size
        """
        self._dbg = debug
        self.__log.debug(f"port={port}, webroot={webroot}, datadir={datadir}")
        self.__log.debug(f"size_limit={size_limit}")

        self._port = port
        self._webroot = os.path.expanduser(webroot)
        self._datadir = os.path.expanduser(datadir)
        self._url_prefix = url_prefix
        self._sd = SchedData(self._datadir)
        self._size_limit = size_limit

        os.makedirs(self._datadir, exist_ok=True)

        self._conf = ConfFile(os.path.join(self._datadir, ConfFile.FNAME))
        self._app_info = AppInfo(
            title=PROG_NAME,
            author=AUTHOR,
            version=VERSION,
            url_prefix=self._url_prefix + "/",
            datadir=self._datadir,
        )

        # 5 つの ``URLSpec`` すべてで同じ dict を使い回す (TODO-090)
        handler_kwargs = {
            "sd": self._sd,
            "app_info": self._app_info,
            "conf": self._conf,
        }

        self._app = tornado.web.Application(
            [
                (r"/", MainHandler, handler_kwargs),
                (self._url_prefix, MainHandler, handler_kwargs),
                (rf"{self._url_prefix}/", MainHandler, handler_kwargs),
                (rf"{self._url_prefix}/edit", EditHandler, handler_kwargs),
                (rf"{self._url_prefix}/edit/", EditHandler, handler_kwargs),
            ],
            static_path=os.path.join(self._webroot, "static"),
            static_url_prefix=self._url_prefix + "/static/",
            template_path=os.path.join(self._webroot, "templates"),
            autoreload=self._dbg,
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

#
# (c) 2026 ytani01
#
"""
Web Interface
"""

__author__ = "ytani01"
__date__ = "2021/01"

from pathlib import Path

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
from .trash_handler import TrashHandler
from .ytsched import SchedData


class WebServer:
    """
    Web application server
    """

    __log = getLogger(__qualname__)

    DEF_URL_PREFIX = "/ytsched"

    DEF_PORT = 10085
    # パッケージに同梱した webroot（templates/, static/）
    DEF_WEBROOT = Path(__file__).absolute().parent / "webroot"
    DEF_WORKDIR = Path("~/ytsched").expanduser()
    DEF_DATADIR = DEF_WORKDIR / "data"

    DEF_SIZE_LIMIT = 100 * 1024 * 1024  # 100MB

    def __init__(
        self,
        port: int = DEF_PORT,
        webroot: str | Path = DEF_WEBROOT,
        datadir: str | Path = DEF_DATADIR,
        url_prefix: str = DEF_URL_PREFIX,
        size_limit: int = DEF_SIZE_LIMIT,
        debug: bool = False,
    ):
        """Constructor

        Parameters
        ----------
        port: int
            port number
        webroot: str | Path

        datadir: str | Path

        url_prefix: str

        size_limit: int
            max upload size
        """
        self._dbg = debug
        self.__log.debug(f"port={port}, webroot={webroot}, datadir={datadir}")
        self.__log.debug(f"size_limit={size_limit}")

        self._port = port
        self._webroot = Path(webroot).expanduser()
        self._datadir = Path(datadir).expanduser()
        self._url_prefix = url_prefix
        self._sd = SchedData(self._datadir)
        self._size_limit = size_limit

        self._datadir.mkdir(parents=True, exist_ok=True)

        self._conf = ConfFile(self._datadir / ConfFile.FNAME)
        self._app_info = AppInfo(
            title=PROG_NAME,
            author=AUTHOR,
            version=VERSION,
            url_prefix=self._url_prefix + "/",
            datadir=str(self._datadir),
        )

        # URLSpec すべてで同じ dict を使い回す (TODO-090)
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
                (rf"{self._url_prefix}/trash", TrashHandler, handler_kwargs),
                (rf"{self._url_prefix}/trash/", TrashHandler, handler_kwargs),
            ],
            static_path=self._webroot / "static",
            static_url_prefix=self._url_prefix + "/static/",
            template_path=self._webroot / "templates",
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

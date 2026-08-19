#!/usr/bin/env python3
#
# (c) 2020 Yoichi Tanibayashi
#
"""
Web Interface
"""
__author__ = 'Yoichi Tanibayashi'
__date__ = '2021/01'

import os
import sys
import tornado.ioloop
import tornado.httpserver
import tornado.web

from . import __prog_name__ as PROG_NAME
from . import __author__ as AUTHOR
from . import __version__ as VERSION

from .main_handler import MainHandler
from .edit_handler import EditHandler
from .ytsched import SchedData
from .my_logger import get_logger


class WebServer:
    """
    Web application server
    """
    URL_PREFIX = '/ytsched'

    DEF_PORT = 10085
    DEF_WEBROOT = './webroot/'
    DEF_WORKDIR = os.path.expanduser('~/ytsched')
    DEF_DATADIR = os.path.join(DEF_WORKDIR, 'data')

    DEF_SIZE_LIMIT = 100*1024*1024  # 100MB

    def __init__(self, port: int = DEF_PORT,
                 webroot: str = DEF_WEBROOT,
                 datadir: str = DEF_DATADIR,
                 days: int = MainHandler.DEF_DAYS,
                 size_limit: int = DEF_SIZE_LIMIT,
                 version: bool = False,
                 debug: bool = False):
        """ Constructor

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
        self._log = get_logger(self.__class__.__name__, self._dbg)
        self._log.debug('port=%s, webroot=%s, datadir=%s, days=%s',
                        port, webroot, datadir, days)
        self._log.debug('size_limit=%s', size_limit)

        self._port = port
        self._webroot = os.path.expanduser(webroot)
        self._datadir = os.path.expanduser(datadir)
        self._sd = SchedData(self._datadir, debug=self._dbg)
        self._days = days
        self._size_limit = size_limit

        if version:
            print('%s %s by %s' % (PROG_NAME, VERSION, AUTHOR))
            sys.exit(0)

        try:
            os.makedirs(self._datadir, exist_ok=True)
        except Exception as ex:
            raise ex

        self._app = tornado.web.Application(
            [
                (r'/', MainHandler),
                (r'%s' % self.URL_PREFIX, MainHandler),
                (r'%s/' % self.URL_PREFIX, MainHandler),

                (r'%s/edit' % self.URL_PREFIX, EditHandler),
                (r'%s/edit/' % self.URL_PREFIX, EditHandler),
            ],
            static_path=os.path.join(self._webroot, "static"),
            static_url_prefix=self.URL_PREFIX + '/static/',
            template_path=os.path.join(self._webroot, "templates"),

            autoreload=True,

            title=PROG_NAME,
            author=AUTHOR,
            version=VERSION,

            url_prefix=self.URL_PREFIX + '/',

            datadir=self._datadir,
            days=self._days,
            sd=self._sd,

            debug=self._dbg
        )
        self._log.debug('app=%s', self._app.__dict__)

        self._svr = tornado.httpserver.HTTPServer(
            self._app, max_buffer_size=self._size_limit)
        self._log.debug('svr=%s', self._svr.__dict__)

    def main(self):
        """ main """
        self._log.debug('')

        self._svr.listen(self._port)
        self._log.info('start server: run forever ..')

        tornado.ioloop.IOLoop.current().start()

        self._log.debug('done')

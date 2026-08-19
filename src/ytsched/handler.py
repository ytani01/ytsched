#!/usr/bin/env python3
#
# (c) 2020 Yoichi Tanibayashi
#
"""
HandlerBase
"""
__author__ = 'Yoichi Tanibayashi'
__date__ = '2021/01'

import os
import tornado.web
from .my_logger import get_logger


class HandlerBase(tornado.web.RequestHandler):
    """ HandlerBase """
    CONF_FNAME = 'Conf.cgi'
    CONF_KEY_TODO_DAYS = 'ToDo_Days'
    CONF_KEY_FILTER_STR = 'FilterStr'
    CONF_KEY_SEARCH_STR = 'SearchStr'
    CONF_KEY_SEARCH_N = 'SearchN'

    HTML_MAIN = 'main.html'
    HTML_EDIT = 'edit.html'

    def __init__(self, app, req):
        """ Constructor """
        self._dbg = app.settings.get('debug')
        self._mylog = get_logger(self.__class__.__name__, self._dbg)
        self._mylog.debug('debug=%s', self._dbg)
        self._mylog.debug('app=%s', app)
        self._mylog.debug('req=%s', req)

        self._app = app
        self._req = req

        self._title = app.settings.get('title')
        self._mylog.debug('title=%s', self._title)

        self._author = app.settings.get('author')
        self._mylog.debug('author=%s', self._author)

        self._version = app.settings.get('version')
        self._mylog.debug('version=%s', self._version)

        self._url_prefix = app.settings.get('url_prefix')
        self._mylog.debug('url_prefix=%s', self._url_prefix)

        self._datadir = app.settings.get('datadir')
        self._mylog.debug('datadir=%s', self._datadir)

        self._days = app.settings.get('days')
        self._mylog.debug('days=%s', self._days)

        self._sd = app.settings.get('sd')
        self._mylog.debug('sd=%s', self._sd)

        self._conf_file = os.path.join(self._datadir, self.CONF_FNAME)
        self._mylog.debug('conf_file=%s', self._conf_file)

        self._conf = self.load_conf()

        super().__init__(app, req)

    def load_conf(self):
        """
        """
        self._mylog.debug('')

        conf = {}

        try:
            with open(self._conf_file) as f:
                lines = f.readlines()
        except FileNotFoundError:
            return conf

        for line in lines:
            if line:
                self._mylog.debug('line=%s', line)
                (param, value) = line.split('\t', maxsplit=2)
                value = value.rstrip('\n')
                self._mylog.debug('%a,%a.', param, value)
                conf[param] = value

        return conf

    def save_conf(self):
        """
        """
        self._mylog.debug('')

        with open(self._conf_file, mode='w') as f:
            for p in self._conf:
                f.write('%s\t%s\n' % (p, self._conf[p]))

    def get_conf(self, name):
        """
        """
        self._mylog.debug('name=%s', name)

        try:
            return self._conf[name]
        except KeyError:
            return None

    def set_conf(self, name, value):
        """
        """
        self._mylog.debug('name=%s, value=\'%s\'', name, value)
        self._conf[name] = value
        self.save_conf()

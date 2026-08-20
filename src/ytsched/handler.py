#
# (c) 2020 Yoichi Tanibayashi
#
"""
HandlerBase
"""

__author__ = "Yoichi Tanibayashi"
__date__ = "2021/01"

import os

import tornado.web

from .mylog import getLogger


class HandlerBase(tornado.web.RequestHandler):
    """HandlerBase"""

    __log = getLogger(__qualname__)

    CONF_FNAME = "Conf.cgi"
    CONF_ENCODE = "utf-8"
    CONF_KEY_TODO_DAYS = "ToDo_Days"
    CONF_KEY_FILTER_STR = "FilterStr"
    CONF_KEY_SEARCH_STR = "SearchStr"
    CONF_KEY_SEARCH_N = "SearchN"

    HTML_MAIN = "main.html"
    HTML_EDIT = "edit.html"

    def __init__(self, app, req):
        """Constructor"""
        super().__init__(app, req)

        self.__log.debug(f"app={app}")
        self.__log.debug(f"req={req}")

        self._app = app
        self._req = req

        self._title = app.settings.get("title")
        self.__log.debug(f"title={self._title}")

        self._author = app.settings.get("author")
        self.__log.debug(f"author={self._author}")

        self._version = app.settings.get("version")
        self.__log.debug(f"version={self._version}")

        self._url_prefix = app.settings.get("url_prefix")
        self.__log.debug(f"url_prefix={self._url_prefix}")

        self._datadir = app.settings.get("datadir")
        self.__log.debug(f"datadir={self._datadir}")

        self._days = app.settings.get("days")
        self.__log.debug(f"days={self._days}")

        self._sd = app.settings.get("sd")
        self.__log.debug(f"sd={self._sd}")

        self._conf_file = os.path.join(self._datadir, self.CONF_FNAME)
        self.__log.debug(f"conf_file={self._conf_file}")

        self._conf = self.load_conf()

    def load_conf(self):
        """``Conf.cgi`` を読み込んで dict で返す。

        ファイルが無ければ空の dict を返す。
        """
        self.__log.debug("")

        conf: dict[str, str] = {}

        try:
            with open(self._conf_file, encoding=self.CONF_ENCODE) as f:
                lines = f.readlines()
        except FileNotFoundError:
            return conf

        for line in lines:
            line = line.rstrip("\n")
            if not line:
                continue

            self.__log.debug(f"line={line}")

            if "\t" not in line:
                self.__log.warning(f"{line!a}: no tab .. ignored")
                continue

            (param, value) = line.split("\t", maxsplit=1)
            self.__log.debug(f"{param!a},{value!a}.")
            conf[param] = value

        return conf

    def save_conf(self):
        """設定を ``Conf.cgi`` へ書き出す。"""
        self.__log.debug("")

        with open(self._conf_file, mode="w", encoding=self.CONF_ENCODE) as f:
            f.writelines(f"{p}\t{self._conf[p]}\n" for p in self._conf)

    def get_conf(self, name):
        """設定値を返す。無ければ ``None`` を返す。"""
        self.__log.debug(f"name={name}")

        try:
            return self._conf[name]
        except KeyError:
            return None

    def set_conf(self, name, value):
        """設定値を変更して、``Conf.cgi`` へ保存する。"""
        self.__log.debug(f"name={name}, value='{value}'")
        self._conf[name] = value
        self.save_conf()

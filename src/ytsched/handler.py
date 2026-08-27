#
# (c) 2026 ytani01
#
"""
HandlerBase
"""

__author__ = "ytani01"
__date__ = "2021/01"

import json
import os

import tornado.web

from .mylog import getLogger
from .ytsched import SchedData


class HandlerBase(tornado.web.RequestHandler):
    """HandlerBase: ``conf.json`` の読み書き。"""

    __log = getLogger(__qualname__)

    CONF_FNAME = "conf.json"
    CONF_ENCODE = "utf-8"
    CONF_KEY_TODO_DAYS = "ToDo_Days"
    CONF_KEY_FILTER_STR = "FilterStr"
    CONF_KEY_SEARCH_STR = "SearchStr"
    CONF_KEY_SEARCH_N = "SearchN"

    HTML_MAIN = "main.html"
    HTML_EDIT = "edit.html"

    def __init__(self, app, req, **kwargs):
        """Constructor

        ``**kwargs`` は ``initialize()`` へそのまま渡る
        (``tornado.web.RequestHandler.__init__`` が ``self.initialize(
        **kwargs)`` を呼ぶ。TODO-081)。
        """
        super().__init__(app, req, **kwargs)

        self.__log.debug(f"app={app}")
        self.__log.debug(f"req={req}")

        self._app = app
        self._req = req

        # 属性への代入は明示のまま(型チェッカが属性を追えなくなるため)
        self._title = app.settings.get("title")
        self._author = app.settings.get("author")
        self._version = app.settings.get("version")
        self._url_prefix = app.settings.get("url_prefix")
        self._datadir = app.settings.get("datadir")

        self._conf_file = os.path.join(self._datadir, self.CONF_FNAME)

        self.__log.debug(
            f"title={self._title}, author={self._author},"
            f" version={self._version}, url_prefix={self._url_prefix},"
            f" datadir={self._datadir}, conf_file={self._conf_file}"
        )

        self._conf = self.load_conf()

    def initialize(self, sd: SchedData) -> None:
        """URL の登録時に渡された ``sd`` を受け取る (TODO-081)。

        tornado は ``__init__`` のあとに、``URLSpec`` の 3 番目に
        渡した dict をキーワード引数として ``initialize()`` へ渡す。

        Parameters
        ----------
        sd: SchedData

        """
        self._sd: SchedData = sd

    def load_conf(self) -> dict[str, str]:
        """``conf.json`` を読み込んで dict で返す (TODO-032)。

        ファイルが無ければ空の dict を返す。

        **JSON として読めなくても例外にしない。** 壊れている場合や
        トップレベルが object でない場合は、警告を 1 行出して空の dict
        を返す。値が文字列でないキーは、そのキーだけ飛ばす。不正な
        正規表現の扱い (TODO-012)、不正な引数の扱い (TODO-027) と同じ
        考え方 (設定ファイルが壊れて画面が出ないほうが困る)。

        ファイルそのものが読めない場合 (``PermissionError`` など) は
        捕まえない。設定の中身の問題ではなく、直すべき環境の問題なので、
        黙って既定値で動かない (TODO-032)。

        Returns
        -------
        conf: dict[str, str]

        """
        self.__log.debug("")

        conf: dict[str, str] = {}

        try:
            with open(self._conf_file, encoding=self.CONF_ENCODE) as f:
                data = json.load(f)
        except FileNotFoundError:
            return conf
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            self.__log.warning(f"{self._conf_file}: {e} .. ignored")
            return conf

        if not isinstance(data, dict):
            self.__log.warning(f"{self._conf_file}: not an object .. ignored")
            return conf

        # JSON の object のキーは必ず文字列
        loaded: dict[str, object] = data
        for param, value in loaded.items():
            if not isinstance(value, str):
                self.__log.warning(
                    f"{self._conf_file}: {param!a}={value!a}:"
                    " not a string .. ignored"
                )
                continue

            self.__log.debug(f"{param!a},{value!a}.")
            conf[param] = value

        return conf

    def save_conf(self):
        """設定を ``conf.json`` へ書き出す (TODO-032)。"""
        self.__log.debug("")

        with open(self._conf_file, mode="w", encoding=self.CONF_ENCODE) as f:
            json.dump(self._conf, f, ensure_ascii=False, indent=2)
            f.write("\n")

    def get_conf(self, name):
        """設定値を返す。無ければ ``None`` を返す。"""
        self.__log.debug(f"name={name}")

        return self._conf.get(name)

    def set_conf(self, name, value):
        """設定値を変更して、``conf.json`` へ保存する。"""
        self.__log.debug(f"name={name}, value='{value}'")
        self._conf[name] = value
        self.save_conf()

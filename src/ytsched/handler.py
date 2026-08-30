#
# (c) 2026 ytani01
#
"""
HandlerBase
"""

__author__ = "ytani01"
__date__ = "2021/01"

import dataclasses

import tornado.web

from .conf import ConfFile
from .mylog import getLogger
from .ytsched import SchedData


@dataclasses.dataclass(frozen=True)
class AppInfo:
    """アプリの固定情報 (TODO-090)。

    以前は ``tornado.web.Application`` の設定 (``app.settings``) から
    ``self._title`` のように 1 つずつ取り出していたが、型はどれも
    ``Any`` になり、渡すものが増えるたびに ``webapp.py`` の
    ``URLSpec`` が伸びていた。この 5 つをまとめて ``initialize()`` の
    引数として渡す。

    ``url_prefix`` は末尾に ``/`` が付いた形。
    """

    title: str
    author: str
    version: str
    url_prefix: str
    datadir: str


class HandlerBase(tornado.web.RequestHandler):
    """HandlerBase: ``sd``/``app_info``/``conf`` の受け取りと、
    ``conf.json`` の読み書き (``ConfFile`` へ委譲)。
    """

    __log = getLogger(__qualname__)

    CONF_KEY_SEARCH_STR = "SearchStr"

    HTML_MAIN = "main.html"
    HTML_EDIT = "edit.html"
    HTML_TRASH = "trash.html"

    def __init__(self, app, req, **kwargs):
        """Constructor

        ``**kwargs`` は ``initialize()`` へそのまま渡る
        (``tornado.web.RequestHandler.__init__`` が ``self.initialize(
        **kwargs)`` を呼ぶ。TODO-081)。

        ``self._conf`` は ``initialize()`` で受け取った ``ConfFile``
        (全ハンドラで共有。TODO-090)。ここで 1 リクエストごとに 1 回、
        外部の書き換えが無いか確かめて、あれば読み直す。
        """
        super().__init__(app, req, **kwargs)

        self.__log.debug(f"app={app}")
        self.__log.debug(f"req={req}")

        self._conf.refresh()

    def initialize(
        self, sd: SchedData, app_info: AppInfo, conf: ConfFile
    ) -> None:
        """URL の登録時に渡された依存を受け取る (TODO-081・TODO-090)。

        tornado は ``__init__`` の中で、``URLSpec`` の 3 番目に
        渡した dict をキーワード引数として ``initialize()`` へ渡す。

        Parameters
        ----------
        sd: SchedData
        app_info: AppInfo
        conf: ConfFile

        """
        self._sd: SchedData = sd
        self._app_info = app_info
        self._conf = conf

    def get_conf(self, name):
        """設定値を返す。無ければ ``None`` を返す。"""
        self.__log.debug(f"name={name}")

        return self._conf.get(name)

    def set_conf(self, name, value):
        """設定値を変更する。``conf.json`` への書き込みは
        ``on_finish()`` にまとめてある (TODO-090)。
        """
        self.__log.debug(f"name={name}, value='{value}'")

        self._conf.set(name, value)

    def on_finish(self) -> None:
        """レスポンスを返し終えたあとに tornado が 1 回だけ呼ぶ。

        1 リクエストの中で ``set_conf()`` を何度呼んでいても、
        ``conf.json`` への書き込みはここで 1 回だけ、変更があった
        ときだけ行う (TODO-090)。
        """
        self._conf.save_if_dirty()

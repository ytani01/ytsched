#
# (c) 2026 ytani01
#
"""
EditHandler
"""

__author__ = "ytani01"
__date__ = "2021/01"

import datetime

import tornado.web

from . import handler_util
from .handler import HandlerBase
from .mylog import getLogger
from .ytsched import SchedDataEnt


class EditHandler(HandlerBase):
    """
    Web request handler
    """

    __log = getLogger(__qualname__)

    def get(self, date=None, sde_id=None, todo_flag=False):
        """
        ``date``の優先順位
          1. Parameter
          2. getargument('date')
          3. today()

        ``sde_id``の優先順位
          1. Parameter
          2. getargument('sde_id')
          3. SchedDataEnt.new_id()

        Parameters
        ----------
        date: datetime.date

        sde_id: str

        todo_flag: bool

        """
        self.__log.debug(
            f"date={date}, sde_id={sde_id}, todo_flag={todo_flag}"
        )
        self.__log.debug(f"request={self.request}")
        self.__log.debug(f"request.path={self.request.path}")

        #
        # date
        #
        if not date:
            date_str = self.get_argument("date", None)

            if date_str:
                # 日付として読めなければ「指定が無かった」のと同じ
                # ＝ 今日 (TODO-027)
                date = handler_util.convert_value(
                    "date", date_str, handler_util.str2date
                )

        if not date:
            date = datetime.date.today()

        #
        # search_str
        #
        # 検索中かどうかで、保存したあとの表示位置が変わる
        # (``edit.html`` の ``sde_align``)。**検索語は URL に載せず、
        # ``conf.json`` から読む** (TODO-050)。一覧の URL に持たせるのは
        # 日付だけと決めたので、編集画面へも引数では渡さない
        search_str = self.get_conf(self.CONF_KEY_SEARCH_STR)
        self.__log.debug(f"search_str={search_str}")

        #
        # sde_id
        #
        if not sde_id:
            sde_id = self.get_argument("sde_id", None)

        #
        # todo_flag
        #
        todo_flag_str = self.get_argument("todo_flag", "")
        todo_flag = todo_flag_str == "true"

        self.__log.debug(
            f"date={date}, sde_id={sde_id}, todo_flag={todo_flag}"
        )

        #
        # sde
        #
        new_flag = False

        # ``orig_date`` は「その ``sde`` を読み込んだファイルの日付」
        # (ToDo は None)。行の ``date`` がファイル名から決まる日付と
        # 食い違っていても、``cmd_del()`` が実際にその行が入っている
        # ファイルを見に行けるようにする (TODO-029)。
        # 新規のときは、まだどのファイルにも入っていないので、
        # 今までどおり表示している日付にする
        orig_date = date

        if sde_id:
            if todo_flag:
                sdf = self._sd.get_sdf(None)
            else:
                sdf = self._sd.get_sdf(date)

            sde = sdf.get_sde(sde_id)
            if sde is None:
                # 存在しない ``sde_id`` は 404 (TODO-016)
                raise tornado.web.HTTPError(
                    404, "sde not found: sde_id=%s", sde_id
                )

            orig_date = sdf.date

        else:
            sde = SchedDataEnt("", date)
            self.__log.debug(f"sde_id={sde.sde_id}")
            new_flag = True

        self.render(
            self.HTML_EDIT,
            title=self._app_info.title,
            author=self._app_info.author,
            version=self._app_info.version,
            url_prefix=self._app_info.url_prefix,
            post_url=self._app_info.url_prefix,
            date=date,
            orig_date=orig_date,
            sde=sde,
            new_flag=new_flag,
            todo_flag=todo_flag,
            search_str=search_str,
        )

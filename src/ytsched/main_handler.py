#
# (c) 2026 ytani01
#
"""一覧画面の HTTP ハンドラ (TODO-106)。"""

import datetime
import urllib.parse
from typing import Any, cast

import tornado.web

from .conf import ConfFile
from .handler import AppInfo, HandlerBase
from .main_binder import MainBinder
from .main_view import MainViewBuilder
from .mylog import getLogger
from .sched_load import SchedLoader
from .sched_update import SchedUpdater
from .trash import TrashFile
from .ytsched import SchedData


class MainHandler(HandlerBase):
    """HTTP の受付、コマンド実行、リダイレクトを担当する。"""

    __log = getLogger(__qualname__)

    # 既存の参照先を保つ。実装本体は binder / view builder にある。
    DEF_SEARCH_N = MainBinder.DEF_SEARCH_N
    TODO_DAYS = MainBinder.TODO_DAYS
    DEF_TODO_DAYS = MainBinder.DEF_TODO_DAYS
    DEF_MONTH_CAL = MainBinder.DEF_MONTH_CAL
    DEF_LOAD_WEEK_PAGES = MainBinder.DEF_LOAD_WEEK_PAGES
    LOAD_WEEK_PAGES_MIN = MainBinder.LOAD_WEEK_PAGES_MIN
    LOAD_WEEK_PAGES_MAX = MainBinder.LOAD_WEEK_PAGES_MAX
    DEF_AUTO_TURN_MSEC = MainBinder.DEF_AUTO_TURN_MSEC
    AUTO_TURN_MSEC_MIN = MainBinder.AUTO_TURN_MSEC_MIN
    AUTO_TURN_MSEC_MAX = MainBinder.AUTO_TURN_MSEC_MAX
    DEF_GAUGE_FOLLOW_MSEC = MainBinder.DEF_GAUGE_FOLLOW_MSEC
    GAUGE_FOLLOW_MSEC_MIN = MainBinder.GAUGE_FOLLOW_MSEC_MIN
    GAUGE_FOLLOW_MSEC_MAX = MainBinder.GAUGE_FOLLOW_MSEC_MAX

    def initialize(
        self, sd: SchedData, app_info: AppInfo, conf: ConfFile
    ) -> None:
        super().initialize(sd, app_info, conf)
        self._updater = SchedUpdater(sd)
        loader = SchedLoader(sd)
        self._binder = MainBinder(cast(Any, self))
        self._view_builder = MainViewBuilder(loader)

    def post(self) -> None:
        """設定とコマンドを受け取り、表示用 GET へリダイレクトする。"""
        self.__log.debug(
            f"request.body_arguments={self.request.body_arguments}"
        )
        self._binder.update_conf_args()
        modified_date, edit_url = self.exec_cmd()
        if edit_url:
            self.redirect(edit_url)
            return
        date = self._binder.get_date(modified_date)
        self.redirect(
            self.mkurl(
                self._app_info.url_prefix,
                {
                    "date": date,
                    "sde_align": self.get_argument("sde_align", None),
                },
            )
        )

    def get(self) -> None:
        """GET の表示を binder と view builder へ委譲する。"""
        values = self._view_builder.build(self._binder.get_display_args())
        self.render(
            self.HTML_MAIN,
            title=self._app_info.title,
            author=self._app_info.author,
            version=self._app_info.version,
            url_prefix=self._app_info.url_prefix,
            cache_size=self._sd.get_cache_size(),
            trash_count=TrashFile(self._app_info.datadir).count(),
            **values,
        )

    @staticmethod
    def mkurl(path: str, args: dict[str, object | None]) -> str:
        """空でないクエリだけを含む URL を組み立てる。"""
        params = {key: str(value) for key, value in args.items() if value}
        return (
            path if not params else f"{path}?{urllib.parse.urlencode(params)}"
        )

    def exec_cmd(self) -> tuple[datetime.date | None, str | None]:
        """更新コマンドを実行し、必要なら編集画面の URL を返す。"""
        cmd = self.get_argument("cmd", None)
        if cmd not in ["add", "fix", "update", "del"]:
            return None, None
        modified_date, modified_sde_id = self._updater.exec_update(
            self._binder.get_update_form(cmd)
        )
        if cmd == "del":
            return modified_date, None
        sde = self._updater.get_modified_sde(modified_date, modified_sde_id)
        if sde is None:
            raise tornado.web.HTTPError(
                404,
                "sde not found: date=%s, sde_id=%s (cmd=%s)",
                modified_date,
                modified_sde_id,
                cmd,
            )
        todo_flag = sde.is_todo()
        if todo_flag:
            modified_date = sde.date
        if cmd == "update":
            return modified_date, self.mkurl(
                self._app_info.url_prefix + "edit/",
                {
                    "date": modified_date,
                    "sde_id": modified_sde_id,
                    "todo_flag": str(todo_flag).lower(),
                },
            )
        return modified_date, None

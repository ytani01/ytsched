#
# (c) 2026 ytani01
#
"""
SchedUpdater
"""

__author__ = "ytani01"
__date__ = "2026/08"

import dataclasses
import datetime

from .mylog import getLogger
from .ytsched import SchedData, SchedDataEnt


@dataclasses.dataclass
class SchedUpdateForm:
    """更新フォームから受け取る値一式 (TODO-087)。"""

    cmd: str
    sde_id: str | None
    orig_date: datetime.date | None
    date: datetime.date | None
    time_start: datetime.time | None
    time_end: datetime.time | None
    sde_type: str
    title: str
    place: str
    detail: str
    deadline_date_str: str
    deadline_time_start_str: str
    deadline_time_end_str: str


class SchedUpdater:
    """``cmd`` (add/fix/update/del) を実行する (TODO-087)。"""

    __log = getLogger(__qualname__)

    def __init__(self, sd: SchedData) -> None:
        """Constructor

        Parameters
        ----------
        sd: SchedData

        """
        self._sd = sd

    def exec_update(
        self, form: SchedUpdateForm
    ) -> tuple[datetime.date | None, str | None]:
        """
        Parameters
        ----------
        form: SchedUpdateForm

        Returns
        -------
        date: datetime.date | None
            更新された日付。ToDo の場合は None
        modified_sde_id: str | None
            更新されたスケジュールID。``del`` の場合は None
        """
        self.__log.debug("")

        cmd = form.cmd
        orig_date = form.orig_date
        date = form.date
        time_start = form.time_start
        time_end = form.time_end
        sde_type = form.sde_type
        title = form.title
        place = form.place
        detail = form.detail

        if form.deadline_date_str and not SchedDataEnt.type_is_todo(sde_type):
            #
            # ToDoが完了した場合
            #
            date, time_start, time_end, detail = self.fix_todo_done(
                form.deadline_date_str,
                form.deadline_time_start_str,
                form.deadline_time_end_str,
                detail,
            )

        # sde_id
        sde_id = form.sde_id
        self.__log.debug(f"sde_id={sde_id}")

        # exec cmd
        self.__log.debug(f"EXEC: {cmd}")

        new_sde = None
        modified_sde_id = None

        if cmd in ["add"]:
            sde_id = None

        # ``cmd_del()``/``cmd_add()`` は変更を覚えるだけで保存しない。
        # 同じファイルへの保存が 1 回で済むよう、ここでまとめて
        # 保存する (TODO-077)。
        #
        # ``finally`` にしてあるのは、``SchedData`` がアプリ全体で 1 つ
        # だからで、途中で例外が出たときに変更の印を残したまま抜けると、
        # **次の関係の無いリクエストの保存に紛れ込む**。
        # 途中まで保存されるのは、保存を分ける前と同じ挙動
        try:
            if cmd in ["del", "fix", "update"]:
                self.cmd_del(orig_date, sde_id)

            if cmd in ["add", "fix", "update"]:
                new_sde = self.cmd_add(
                    sde_id,
                    date,
                    time_start,
                    time_end,
                    sde_type,
                    title,
                    place,
                    detail,
                )
        finally:
            self._sd.save()

        if new_sde:
            modified_sde_id = new_sde.sde_id
            date = new_sde.date
            if new_sde.is_todo():
                date = None

        self.__log.debug(f"date={date}, modified_sde_id={modified_sde_id}")
        return date, modified_sde_id

    def get_modified_sde(
        self, date: datetime.date | None, sde_id: str | None
    ) -> SchedDataEnt | None:
        """更新したデータを読み直す。

        Parameters
        ----------
        date: datetime.date | None
        sde_id: str | None

        Returns
        -------
        SchedDataEnt | None
            見つからなければ ``None`` (404 にするのは呼び出し側)

        """
        sdf = self._sd.get_sdf(date)
        sde = sdf.get_sde(sde_id)
        self.__log.debug(f"sde={sde}")

        return sde

    def fix_todo_done(
        self,
        deadline_date_str: str,
        deadline_time_start_str: str,
        deadline_time_end_str: str,
        detail: str,
    ) -> tuple[datetime.date, datetime.time, datetime.time | None, str]:
        """ToDoが完了した場合の補正。

        ``date``, ``time_start``を現在日時にして、``detail``の先頭に
        元の締切を書き足す。

        Parameters
        ----------
        deadline_date_str: str
        deadline_time_start_str: str
        deadline_time_end_str: str
        detail: str

        Returns
        -------
        date: datetime.date
        time_start: datetime.time
        time_end: datetime.time | None
        detail: str

        """
        date = datetime.date.today()
        self.__log.debug(f"[fix] date={date}")

        time_start = datetime.datetime.now().time()
        # msec を切り捨てる
        time_start = datetime.time.fromisoformat(
            time_start.strftime(SchedDataEnt.TIME_FORMAT)
        )
        self.__log.debug(f"[fix] time_start={time_start}")
        time_end = None

        deadline_date = deadline_date_str.replace("-", "/")
        deadline_time = f"{deadline_time_start_str}{deadline_time_end_str}"
        # 時刻が無ければ、区切りの空白も付けない (TODO-028)
        deadline_line = f"〆{deadline_date}"
        if deadline_time:
            deadline_line += f" {deadline_time}"

        detail = f"{deadline_line}\n{detail}"
        self.__log.debug(f"[fix] detail={detail}")

        return date, time_start, time_end, detail

    def cmd_add(
        self,
        sde_id,
        date,
        time_start,
        time_end,
        sde_type,
        title,
        place,
        detail,
    ):
        """
        Parameters
        ----------
        sde_id: str
        date: datetime.date
        time_start, time_end:
        sde_type: str
        title: str
        place: str
        detail: str

        Returns
        -------
        new_sde: SchedDataEnt

        """
        self.__log.debug(f"sde_id={sde_id}, date={date}")

        new_sde = SchedDataEnt(
            sde_id,
            date,
            time_start,
            time_end,
            sde_type,
            title,
            place,
            detail,
        )
        if new_sde.is_todo():
            self._sd.add_sde(None, new_sde)
        else:
            # ``date`` が空でも ``SchedDataEnt`` 側で今日に補正される。
            # 書き込み先も ``new_sde.date`` に合わせる (TODO-016)
            self._sd.add_sde(new_sde.date, new_sde)

        return new_sde

    def cmd_del(self, date, sde_id):
        """
        Parameters
        ----------
        date: datetime.date

        sde_id: str

        """
        self.__log.debug(f"date={date}, sde_id={sde_id}")

        self._sd.del_sde(date, sde_id)

#
# (c) 2026 ytani01
#
"""ゴミ箱画面の HTTP ハンドラ（TODO-086・TODO-141）。"""

import datetime

import tornado.web

from .handler import HandlerBase
from .trash import TrashEntry, TrashFile
from .ytsched import SchedDataEnt


class TrashHandler(HandlerBase):
    """``trash.jsonl`` の表示、復活、一括削除を扱う。"""

    CONF_KEY_TRASH_MAX = "TrashMax"
    DEF_TRASH_MAX = 100

    def _max_entries(self) -> int:
        value = self.get_conf(self.CONF_KEY_TRASH_MAX)
        try:
            max_entries = (
                int(value) if value is not None else self.DEF_TRASH_MAX
            )
        except ValueError:
            return self.DEF_TRASH_MAX
        return max_entries if max_entries > 0 else self.DEF_TRASH_MAX

    def _trash(self) -> TrashFile:
        return TrashFile(self._app_info.datadir)

    def get(self) -> None:
        sde_id = self.get_argument("sde_id", None)
        entries = self._trash().entries(sde_id, self._max_entries())
        groups: list[list[TrashEntry]] = []
        by_id: dict[str, list[TrashEntry]] = {}
        for entry in entries:
            by_id.setdefault(
                SchedDataEnt.id_uuid(entry.sde.sde_id), []
            ).append(entry)
        groups = list(by_id.values())
        self.render(
            self.HTML_TRASH,
            title=self._app_info.title,
            author=self._app_info.author,
            version=self._app_info.version,
            url_prefix=self._app_info.url_prefix,
            groups=groups,
            entry_count=len(entries),
            sde_id=sde_id,
            today=datetime.date.today(),
        )

    def post(self) -> None:
        cmd = self.get_argument("cmd", None)
        if cmd == "restore":
            self._restore()
        elif cmd == "delete_many":
            self._delete_many()
        else:
            raise tornado.web.HTTPError(400, "unknown command")

    def _restore_id(self, sde: SchedDataEnt) -> str | None:
        """復活させる予定の ``sde_id`` を決める（TODO-171）。

        元の ID が新しい形式（``{UUID}-{版}``）なら、元の UUID を
        引き継いで版を増やす。

        版は、データディレクトリ全体（ゴミ箱と、日々のファイル・
        ``ToDo.jsonl``）を走査して、同じ UUID を持つ行の最大の版 + 1
        にする。**「復活先の日付のファイル」だけを見ると、日付を変える
        編集で生きている予定が別の日付へ移ったときに見落とす**
        （reviewer 指摘。TODO-171）。復活は滅多に使わない操作なので、
        全走査の費用を払ってよい。

        元の ID が新しい形式でなければ ``None``（呼び出し元で新しい
        UUID が発行される）。
        """
        split = SchedDataEnt.split_id(sde.sde_id)
        if split is None:
            return None
        uuid_part, version = split

        max_version = max(
            self._trash().max_version(uuid_part),
            self._sd.max_version(uuid_part),
            version,
        )

        return SchedDataEnt.format_id(uuid_part, max_version + 1)

    def _restore(self) -> None:
        sde_id = self.get_argument("sde_id")
        trashed_at = self.get_argument("trashed_at")
        entry = self._trash().get(sde_id, trashed_at)
        if entry is None:
            raise tornado.web.HTTPError(404, "trash entry not found")

        sde = entry.sde
        restored_id = self._restore_id(sde)
        restored = SchedDataEnt(
            restored_id,
            sde.date,
            sde.time_start,
            sde.time_end,
            sde.type,
            f"(復活){sde.title}",
            sde.place,
            sde.detail,
        )
        self._sd.add_sde(restored.date, restored)
        self._sd.save()
        self.redirect(f"{self._app_info.url_prefix}?date={restored.date}")

    def _delete_many(self) -> None:
        sde_ids = self.get_arguments("sde_id")
        trashed_ats = self.get_arguments("trashed_at")
        if (
            not sde_ids
            or len(sde_ids) != len(trashed_ats)
            or not all(sde_ids)
            or not all(trashed_ats)
        ):
            raise tornado.web.HTTPError(400, "invalid trash entries")
        try:
            for trashed_at in trashed_ats:
                if "T" not in trashed_at:
                    raise ValueError("not an ISO 8601 timestamp")
                datetime.datetime.fromisoformat(trashed_at)
        except ValueError as e:
            raise tornado.web.HTTPError(400, "invalid trashed_at") from e

        trash = self._trash()
        if not trash.delete_many(set(zip(sde_ids, trashed_ats, strict=True))):
            raise tornado.web.HTTPError(404, "trash entry not found")
        if trash.entries(max_entries=1):
            self.redirect(f"{self._app_info.url_prefix}trash")
        else:
            self.redirect(self._app_info.url_prefix)

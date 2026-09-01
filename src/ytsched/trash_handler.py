#
# (c) 2026 ytani01
#
"""ゴミ箱画面の HTTP ハンドラ（TODO-086）。"""

import tornado.web

from .handler import HandlerBase
from .trash import TrashEntry, TrashFile
from .ytsched import SchedDataEnt


class TrashHandler(HandlerBase):
    """``trash.jsonl`` の表示、復活、削除、空にするを扱う。"""

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
            by_id.setdefault(entry.sde.sde_id, []).append(entry)
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
        )

    def post(self) -> None:
        cmd = self.get_argument("cmd", None)
        if cmd == "restore":
            self._restore()
        elif cmd == "delete":
            self._delete()
        elif cmd == "clear":
            self._clear()
        else:
            raise tornado.web.HTTPError(400, "unknown command")

    def _restore(self) -> None:
        sde_id = self.get_argument("sde_id")
        trashed_at = self.get_argument("trashed_at")
        entry = self._trash().get(sde_id, trashed_at)
        if entry is None:
            raise tornado.web.HTTPError(404, "trash entry not found")

        sde = entry.sde
        restored = SchedDataEnt(
            None,
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

    def _delete(self) -> None:
        sde_id = self.get_argument("sde_id")
        trashed_at = self.get_argument("trashed_at")
        if not self._trash().delete(sde_id, trashed_at):
            raise tornado.web.HTTPError(404, "trash entry not found")
        self.redirect(f"{self._app_info.url_prefix}trash")

    def _clear(self) -> None:
        self._trash().clear()
        self.redirect(self._app_info.url_prefix)

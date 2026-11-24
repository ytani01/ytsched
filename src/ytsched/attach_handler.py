#
# (c) 2026 ytani01
#
"""添付ファイルを返す HTTP ハンドラ（TODO-237）。"""

import mimetypes
import urllib.parse
from pathlib import Path

import tornado.web

from .attach import AttachStore
from .fix_id import is_uuid


class AttachHandler(tornado.web.StaticFileHandler):
    """``attach/{UUID}/{ファイル名}`` を返す。

    ``path`` には ``attachments/`` のフォルダを渡す。UUID とファイル名を
    検証してから読むので、``..`` などでフォルダの外は読めない。
    画像（``IMAGE_TYPES``）だけをその場に表示させ、それ以外は
    ``application/octet-stream`` のダウンロードにする。HTML や SVG を
    同じオリジンで描画させないため。
    """

    def parse_url_path(self, url_path: str) -> str:
        uuid_part, sep, name = url_path.partition("/")
        if (
            not sep
            or not is_uuid(uuid_part)
            or not AttachStore.is_valid_name(name)
        ):
            raise tornado.web.HTTPError(404)
        return str(Path(uuid_part) / name)

    def compute_etag(self) -> str | None:
        # 消したあと同じ名前で置き直せるので、パスごとに覚える
        # StaticFileHandler のハッシュは使わない（Last-Modified で足りる）
        return None

    def get_content_type(self) -> str:
        assert self.absolute_path is not None
        if AttachStore.is_image(self.absolute_path):
            return mimetypes.guess_type(self.absolute_path)[0] or ""
        return "application/octet-stream"

    def set_extra_headers(self, path: str) -> None:
        name = Path(path).name
        disposition = "inline" if AttachStore.is_image(name) else "attachment"
        self.set_header(
            "Content-Disposition",
            f"{disposition}; filename*=UTF-8''{urllib.parse.quote(name)}",
        )
        self.set_header("X-Content-Type-Options", "nosniff")
        self.set_header("Content-Security-Policy", "sandbox")

#
# (c) 2026 ytani01
#
"""添付ファイルのテスト（TODO-237）。"""

import json
import re
import uuid
from urllib.parse import quote, urlencode

from helpers import URL_PREFIX
from test_web import DATE1, DATE1_STR, FORM_HEADERS, WebTestBase, mk_dataline

from ytsched.attach import AttachStore

UUID_A = "3f2a1b0c-4d5e-6f70-8192-a3b4c5d6e7f8"
PNG = b"\x89PNG\r\n\x1a\nfake"


# ---------------------------------------------------------------------------
# AttachStore
# ---------------------------------------------------------------------------


def test_add_does_not_overwrite_same_name(tmp_path):
    store = AttachStore(tmp_path)
    sde_id = f"{UUID_A}-1"

    assert store.add(sde_id, "a.png", b"1") == "a.png"
    assert store.add(f"{UUID_A}-2", "a.png", b"2") == "a-1.png"
    assert store.add(sde_id, "a.png", b"3") == "a-2.png"

    d = tmp_path / "attachments" / UUID_A
    assert (d / "a.png").read_bytes() == b"1"
    assert (d / "a-1.png").read_bytes() == b"2"
    assert store.list_files(sde_id) == ["a-1.png", "a-2.png", "a.png"]


def test_safe_name():
    assert AttachStore.safe_name("../../etc/passwd") == "passwd"
    assert AttachStore.safe_name("C:\\tmp\\x.pdf") == "x.pdf"
    assert AttachStore.safe_name(".bashrc") == "bashrc"
    assert AttachStore.safe_name("..") is None
    assert AttachStore.safe_name("a\nb") is None
    assert AttachStore.safe_name("") is None
    # 先頭の ``.`` と空白が交互でも、2 回通して変わらない形にする
    assert AttachStore.safe_name(". a.png") == "a.png"
    assert AttachStore.safe_name(" . .b ") == "b"


def test_legacy_id_has_no_attachments(tmp_path):
    store = AttachStore(tmp_path)
    assert store.add("id-1", "a.png", b"1") is None
    assert store.list_files("id-1") == []
    assert not (tmp_path / "attachments").exists()


def test_remove_drops_empty_dir(tmp_path):
    store = AttachStore(tmp_path)
    store.add(f"{UUID_A}-1", "a.png", b"1")
    store.remove(f"{UUID_A}-2", "a.png")
    assert not (tmp_path / "attachments" / UUID_A).exists()


# ---------------------------------------------------------------------------
# Web
# ---------------------------------------------------------------------------


class TestAttachWeb(WebTestBase):
    def post_multipart(self, fields, files=()):
        """``multipart/form-data`` で ``/`` へ POST する。

        ``WebTestBase.fetch()`` は ``_xsrf`` を urlencode の形で足すので、
        ここで自分で足す。
        """
        res = super(WebTestBase, self).fetch(URL_PREFIX + "/")
        m = re.search(r"_xsrf=([^;]+)", res.headers["Set-Cookie"])
        assert m is not None
        token = m.group(1)
        boundary = "----ytschedtest"
        parts = []
        for name, value in [*fields, ("_xsrf", token)]:
            parts.append(
                f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"'
                f"\r\n\r\n{value}\r\n".encode()
            )
        for filename, body in files:
            parts.append(
                f"--{boundary}\r\nContent-Disposition: form-data; "
                f'name="attach"; filename="{filename}"\r\n'
                "Content-Type: application/octet-stream\r\n\r\n".encode()
                + body
                + b"\r\n"
            )
        parts.append(f"--{boundary}--\r\n".encode())
        return self.fetch(
            URL_PREFIX + "/",
            method="POST",
            headers={
                "Content-Type": f"multipart/form-data; boundary={boundary}",
                "Cookie": f"_xsrf={token}",
            },
            body=b"".join(parts),
            follow_redirects=False,
            raise_error=False,
            xsrf=False,
        )

    def fix_fields(self, sde_id, cmd="fix"):
        return [
            ("cmd", cmd),
            ("sde_id", sde_id),
            ("orig_date", DATE1_STR),
            ("date", DATE1_STR),
            ("title", "定例ミーティング"),
        ]

    def live_ids(self):
        return [
            json.loads(line)["sde_id"]
            for line in self.data_path(DATE1)
            .read_text(encoding="utf-8")
            .splitlines()
        ]

    def attach_dir(self, uuid_part=UUID_A):
        return self.datadir / "attachments" / uuid_part

    def test_fix_saves_files_and_list_shows_them(self):
        self.write_data(DATE1, [mk_dataline(sde_id=f"{UUID_A}-1")])

        res = self.post_multipart(
            self.fix_fields(f"{UUID_A}-1"),
            [("photo.png", PNG), ("memo.pdf", b"%PDF"), ("photo.png", PNG)],
        )

        assert res.code == 302
        assert sorted(p.name for p in self.attach_dir().iterdir()) == [
            "memo.pdf",
            "photo-1.png",
            "photo.png",
        ]
        body = self.get_body(URL_PREFIX + "/", date=DATE1_STR)
        url = f"{URL_PREFIX}/attach/{UUID_A}"
        assert re.search(rf'<img\s+src="{url}/photo\.png"', body)
        assert f'<a href="{url}/memo.pdf">memo.pdf</a>' in body

        edit = self.get_body(
            URL_PREFIX + "/edit/", date=DATE1_STR, sde_id=f"{UUID_A}-2"
        )
        assert 'name="attach_del" value="memo.pdf"' in edit
        # 編集画面でも画像だけサムネイルを出す (TODO-241)
        assert re.search(rf'<img\s+src="{url}/photo\.png"', edit)
        assert f'src="{url}/memo.pdf"' not in edit

    def test_update_removes_checked_file(self):
        self.write_data(DATE1, [mk_dataline(sde_id=f"{UUID_A}-1")])
        store = AttachStore(self.datadir)
        store.add(f"{UUID_A}-1", "a.png", PNG)
        store.add(f"{UUID_A}-1", "b.pdf", b"%PDF")

        res = self.post_multipart(
            [
                *self.fix_fields(f"{UUID_A}-1", "update"),
                ("attach_del", "a.png"),
            ]
        )

        assert res.code == 302
        assert [p.name for p in self.attach_dir().iterdir()] == ["b.pdf"]

    def test_legacy_id_attaches_to_new_uuid(self):
        """旧形式の ID は ``next_id()`` が振る新しい UUID の側に置く。"""
        self.write_data(DATE1, [mk_dataline(sde_id="id-1")])

        res = self.post_multipart(self.fix_fields("id-1"), [("a.png", PNG)])

        assert res.code == 302
        (new_id,) = self.live_ids()
        new_uuid = AttachStore.uuid_of(new_id)
        assert new_uuid is not None
        assert (self.attach_dir(new_uuid) / "a.png").read_bytes() == PNG

    def test_name_starting_with_dot_and_space_can_be_opened_and_removed(self):
        self.write_data(DATE1, [mk_dataline(sde_id=f"{UUID_A}-1")])

        res = self.post_multipart(
            self.fix_fields(f"{UUID_A}-1"), [(". a.png", PNG)]
        )
        assert res.code == 302
        (name,) = AttachStore(self.datadir).list_files(f"{UUID_A}-1")
        res = self.fetch(f"{URL_PREFIX}/attach/{UUID_A}/{quote(name)}")
        assert res.code == 200

        res = self.post_multipart(
            [*self.fix_fields(f"{UUID_A}-2"), ("attach_del", name)]
        )
        assert res.code == 302
        assert not self.attach_dir().exists()

    def test_too_long_name_is_shortened_keeping_suffix(self):
        """FS の上限（255 バイト）を超える名前でも 500 にしない。"""
        self.write_data(DATE1, [mk_dataline(sde_id=f"{UUID_A}-1")])
        long_name = "あ" * 90 + ".pdf"

        res = self.post_multipart(
            self.fix_fields(f"{UUID_A}-1"),
            [(long_name, b"1"), (long_name, b"2")],
        )

        assert res.code == 302
        names = AttachStore(self.datadir).list_files(f"{UUID_A}-2")
        assert len(names) == 2
        for name in names:
            assert len(name.encode()) <= AttachStore.MAX_NAME_BYTES
            assert name.endswith(".pdf")
            assert AttachStore.is_valid_name(name)

    def test_add_copy_keeps_original_attachments(self):
        """複製（``add``）は別の UUID になる。``attach_del`` で元の予定の
        添付を消さず、元の添付も引き継がない。
        """
        self.write_data(DATE1, [mk_dataline(sde_id=f"{UUID_A}-1")])
        AttachStore(self.datadir).add(f"{UUID_A}-1", "a.png", PNG)

        res = self.post_multipart(
            [
                *self.fix_fields(f"{UUID_A}-1", "add"),
                ("attach_del", "a.png"),
            ],
            [("b.pdf", b"%PDF")],
        )

        assert res.code == 302
        assert [p.name for p in self.attach_dir().iterdir()] == ["a.png"]
        (new_id,) = [i for i in self.live_ids() if not i.startswith(UUID_A)]
        new_uuid = AttachStore.uuid_of(new_id)
        assert new_uuid is not None
        assert [p.name for p in self.attach_dir(new_uuid).iterdir()] == [
            "b.pdf"
        ]

    def test_handler_serves_image_inline_and_others_as_download(self):
        store = AttachStore(self.datadir)
        store.add(f"{UUID_A}-1", "a.png", PNG)
        store.add(f"{UUID_A}-1", "x.html", b"<script>alert(1)</script>")
        store.add(f"{UUID_A}-1", "y.svg", b"<svg/>")

        res = self.fetch(f"{URL_PREFIX}/attach/{UUID_A}/a.png")
        assert res.code == 200
        assert res.body == PNG
        assert res.headers["Content-Type"] == "image/png"
        assert res.headers["Content-Disposition"].startswith("inline")

        for name in ["x.html", "y.svg"]:
            res = self.fetch(f"{URL_PREFIX}/attach/{UUID_A}/{name}")
            assert res.code == 200
            assert res.headers["Content-Type"] == "application/octet-stream"
            assert res.headers["Content-Disposition"].startswith("attachment")
            assert res.headers["X-Content-Type-Options"] == "nosniff"

    def test_handler_rejects_path_traversal(self):
        (self.datadir / "trash.jsonl").write_text("secret", encoding="utf-8")
        AttachStore(self.datadir).add(f"{UUID_A}-1", "a.png", PNG)

        for path in [
            f"{UUID_A}/{quote('../../trash.jsonl', safe='')}",
            f"{UUID_A}/{quote('..', safe='')}",
            f"{quote('..', safe='')}/trash.jsonl",
            f"{UUID_A}/.hidden",
            "not-a-uuid/a.png",
            UUID_A,
            f"{UUID_A}/",
        ]:
            res = self.fetch(f"{URL_PREFIX}/attach/{path}")
            assert res.code == 404, path
            assert b"secret" not in res.body

    def write_trash(self, *sde_ids):
        (self.datadir / "trash.jsonl").write_text(
            "".join(
                json.dumps(
                    {
                        "trashed_at": f"2026-08-29T09:10:0{i}",
                        **json.loads(mk_dataline(sde_id=sde_id)),
                    }
                )
                + "\n"
                for i, sde_id in enumerate(sde_ids)
            ),
            encoding="utf-8",
        )

    def delete_from_trash(self, *pairs):
        return self.fetch(
            URL_PREFIX + "/trash",
            method="POST",
            headers=FORM_HEADERS,
            body=urlencode(
                [("cmd", "delete_many")]
                + [
                    kv
                    for sde_id, at in pairs
                    for kv in [("sde_id", sde_id), ("trashed_at", at)]
                ]
            ),
            follow_redirects=False,
            raise_error=False,
        )

    def test_delete_from_trash_removes_orphan_dir(self):
        self.write_trash(f"{UUID_A}-1", f"{UUID_A}-2")
        AttachStore(self.datadir).add(f"{UUID_A}-1", "a.png", PNG)

        res = self.delete_from_trash(
            (f"{UUID_A}-1", "2026-08-29T09:10:00"),
            (f"{UUID_A}-2", "2026-08-29T09:10:01"),
        )

        assert res.code == 302
        assert not self.attach_dir().exists()

    def test_delete_from_trash_keeps_dir_if_version_left_in_trash(self):
        self.write_trash(f"{UUID_A}-1", f"{UUID_A}-2")
        AttachStore(self.datadir).add(f"{UUID_A}-1", "a.png", PNG)

        res = self.delete_from_trash((f"{UUID_A}-1", "2026-08-29T09:10:00"))

        assert res.code == 302
        assert (self.attach_dir() / "a.png").exists()

    def test_delete_from_trash_keeps_dir_if_live_version_exists(self):
        self.write_data(DATE1, [mk_dataline(sde_id=f"{UUID_A}-2")])
        self.write_trash(f"{UUID_A}-1")
        AttachStore(self.datadir).add(f"{UUID_A}-1", "a.png", PNG)

        res = self.delete_from_trash((f"{UUID_A}-1", "2026-08-29T09:10:00"))

        assert res.code == 302
        assert (self.attach_dir() / "a.png").exists()

    def test_delete_from_trash_keeps_other_uuid_dirs(self):
        other = str(uuid.uuid4())
        self.write_trash(f"{UUID_A}-1")
        AttachStore(self.datadir).add(f"{other}-1", "a.png", PNG)

        self.delete_from_trash((f"{UUID_A}-1", "2026-08-29T09:10:00"))

        assert (self.attach_dir(other) / "a.png").exists()

# TODO-169 verifier 報告

対象: `docs/image-attach-proposal.md` の事実記述 12 項目。

1. 合っている。`src/ytsched/sched_update.py` `exec_update()` は
   `cmd in ["del", "fix", "update"]` で `cmd_del()`、
   `cmd in ["add", "fix", "update"]` で `cmd_add()` を呼ぶ（127-140行）。
   `add` のときだけ `sde_id = None`（106-107行）にしてから `cmd_add()` へ
   渡し、`fix`/`update` は元の `sde_id` を渡す。`SchedDataEnt.__init__()`
   （`ytsched.py` 99行）は `sde_id` が空なら `new_id()` を発行するので、
   `add` は振り直し、`fix`/`update` は保つ。

2. 合っている。`SchedData.del_sde()`（`ytsched.py` 971-1000行）は
   `SchedDataFile.del_sde()` で日ファイルの行を消し、直後に
   `self._trash.add(sde)` で `trash.jsonl` へ追記する
   （`trash.py` は `TrashFile` クラス）。

3. 合っている。`trash_handler.py` `_restore()`（63-82行）は
   `SchedDataEnt(None, sde.date, sde.time_start, ..., sde.detail)` と
   フィールドを 1 つずつ列挙して組み直しており、`sde_id` は `None`
   （＝振り直し）。新しいキーを足すなら、この列挙にも足さないと
   引き継がれない、という記述はコードの実態と一致する。

4. 合っている。`docs/data-format.md` 241行「`sde_id` は 13352 種類で、
   8 種類が重複していた（最大 3 回）」。提案書の「8 種類が重複していた」
   と一致。ただし提案書は「UUID でなく」とだけ書き、data-format.md の
   54行にある「独自の形で 13〜18 文字」という具体を省いているが、
   誤りではない。

5. 合っている。`docs/data-format.md` 66行「書くときは全部のキーを出す。
   読むときは欠けていてもよい。」。`SchedDataEnt.to_dict()`
   （`ytsched.py` 131-145行）は全キーを常に出す。`from_dict()`
   （147-183行）は `dict_str()`/`dict_time()` 経由で欠けたキーを既定値
   として読む。

6. 合っている。`sched_update.py`・`sched_load.py`（`SchedLoader` の
   定義ファイル）・`trash.py` のいずれも `import tornado` は無い
   （grep で確認）。

7. 合っている。`webapp.py` 109-110行で
   `static_path=self._webroot / "static"`、
   `static_url_prefix=self._url_prefix + "/static/"` を
   `tornado.web.Application` に渡している。`datadir` は
   `StaticFileHandler` や `static_path` に登場せず、配信対象になって
   いない。

8. 合っている。`webapp.py` 44行 `DEF_SIZE_LIMIT = 100 * 1024 * 1024`、
   118行付近で `HTTPServer(self._app, max_buffer_size=self._size_limit)`
   に渡している。

9. 合っている。`grep -rn "fetch(\|XMLHttpRequest\|FormData"
   src/ytsched/webroot/static/js/` はヒット無し（exit 1）。

10. 合っている。`edit.html` 77-78行 `<form id="input_form" ...
    action="{{ post_url }}" method="POST">` に `enctype` は無い。
    `edit_handler.py` 136行で `post_url=self._app_info.url_prefix` を
    テンプレートへ渡している。`url_prefix`（既定 `/ytsched`）は
    `webapp.py` 102-103行で `MainHandler` に登録されている
    （`MainHandler.post()` が受ける想定と一致。`post()` 自体の中身は
    今回の依頼の確認範囲外なので中身までは見ていない）。

11. 合っている。`sde.html` 145-161行、チェックボックス
    `class="my-longtext-sw"` と隣接する `.my-longtext` を CSS の
    `~` セレクタ（`my.css` 475行 `.my-longtext-sw:checked ~
    .my-longtext`）で開閉している。`grep -rln longtext
    src/ytsched/webroot/static/js/` はヒット無し。

12. 合っている。`pyproject.toml` 11-15行の `dependencies` は
    `click` `loguru` `tornado` の 3 つのみ。画像を扱うライブラリ
    （Pillow 等）は無い。

## まとめ

12 項目すべて、コード・既存文書の実態と一致していた。事実誤認は
見つからなかった。

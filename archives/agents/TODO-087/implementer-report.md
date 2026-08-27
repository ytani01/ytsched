# TODO-087 implementer 報告

## 変更したファイル

- `src/ytsched/sched_update.py`（新規）— `SchedUpdateForm`（dataclass）と
  `SchedUpdater`（`exec_update()` / `get_modified_sde()` /
  `fix_todo_done()` / `cmd_add()` / `cmd_del()`）。tornado は import しない。
  `get_modified_sde()` は 404 を投げず `SchedDataEnt | None` を返す形に変更
  （依頼書のとおり）
- `src/ytsched/main_handler.py` — `exec_update()` / `cmd_add()` /
  `cmd_del()` / `fix_todo_done()` / 旧 `get_modified_sde()` を削除。
  `initialize()` を追加して `self._updater = SchedUpdater(sd)` を作成。
  `get_update_form(cmd)` を新設（引数の取り出しをそのまま移設、順序も
  そのまま）。`exec_cmd()` は `search_str` 引数を削除し、
  `self._updater.exec_update(form)` / `self._updater.get_modified_sde(...)`
  を呼ぶ形に変更、404 の送出は `exec_cmd()` に残した（メッセージ・
  ステータス・引数は変更なし）。`post()` の `search_str = self.get_conf_arg(...)`
  を `_ = self.get_conf_arg(...)` に変更し、`exec_cmd(search_str)` を
  `exec_cmd()` に変更
- `tests/test_main_handler.py` — `spy_cmd_add()` のパッチ先を
  `MainHandler.cmd_add` から `SchedUpdater.cmd_add` に変更（import 追加）
- `tests/test_web.py` — `mock.patch.object(MainHandler, "cmd_add", ...)`
  を `SchedUpdater.cmd_add` に変更（import 追加）

## 確かめたこと

- `mise run lint`（`ruff format` / `ruff check` / `basedpyright` /
  `mypy`）すべて問題なし
- `uv run pytest -q` → 475 件全て pass
- `uv run ytsched webapp --datadir <一時ディレクトリ>` で起動し、
  `GET /ytsched/` が 200、`POST cmd=add` が 302 で
  `/ytsched/?date=2026-08-28` へリダイレクトされることを確認
  （POST-Redirect-GET の挙動は変わっていない）

## 判断が要る点

特になし。依頼書の設計どおりに移動しただけで、追加の判断はしていない。

## 気づいたが直さなかったこと

- `tests/test_main_handler.py` / `tests/test_web.py` のコメント・docstring
  中に `exec_update()` / `cmd_del()` などの古いクラスへの言及が残っている
  （例: 「``fix`` は ``cmd_del()`` → ``cmd_add()`` で実装されている」）。
  関数名自体は `SchedUpdater` 側にそのまま残っているので実質的な誤りは
  ないが、`MainHandler` のメソッドという含みが消えていない。TODO-087 の
  範囲（移動のみ、テストの期待値は変えない）を超えるので触っていない

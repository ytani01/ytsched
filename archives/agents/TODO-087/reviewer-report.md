# TODO-087 reviewer 報告

## 見た範囲

- `git diff`（`src/ytsched/main_handler.py` / `src/ytsched/sched_update.py`
  / `tests/test_main_handler.py` / `tests/test_web.py`）
- 移す前のコード（`git show HEAD:src/ytsched/main_handler.py`）と
  1 行単位で突き合わせ

依頼書の 1〜7 の観点を確認した結果、指摘は無し。

## 確認した内容（依頼の 1〜7 に対応）

1. `get_update_form()` の中で `orig_date` → `date` → 時刻 → その他 の順は
   旧 `exec_update()` の前半とまったく同じ。`exec_cmd()` は
   `form = self.get_update_form(cmd)` を `self._updater.exec_update(form)`
   より先に呼んでおり、`cmd_del()`/`cmd_add()`（`SchedUpdater` 側）より
   前に 400 を投げる経路が保たれている
2. `try`/`finally` の `self._sd.save()` は `SchedUpdater.exec_update()` に
   そのまま残っている。コメント（TODO-077 の理由）も移してある
3. `fix_todo_done()` に入る条件
   `form.deadline_date_str and not SchedDataEnt.type_is_todo(sde_type)`
   は旧コードと同一
4. `cmd in ["add"]` のときの `sde_id = None`、`new_sde.is_todo()` の
   ときの `date = None` は、どちらも `SchedUpdater.exec_update()` に
   そのまま残っている
5. `SchedUpdater.get_modified_sde()` は `None` を返すだけになり、
   `MainHandler.exec_cmd()` 側で `sde is None` のとき 404 を投げている。
   ステータス・メッセージ・引数（`date=%s, sde_id=%s (cmd=%s)`）は
   旧 `get_modified_sde()` の例外と同じ
6. `SchedUpdateForm` の全フィールド（`cmd` / `sde_id` / `orig_date` /
   `date` / `time_start` / `time_end` / `sde_type` / `title` / `place` /
   `detail` / `deadline_date_str` / `deadline_time_start_str` /
   `deadline_time_end_str`）は `get_update_form()` で漏れなく埋められ、
   `SchedUpdater.exec_update()` 側でも全フィールドを読んでいる。
   詰め忘れ・詰め違いは無い
7. `exec_cmd(search_str)` の `search_str` は、旧コードでも
   docstring に書かれているだけで本体では未使用だった（`grep` で確認）。
   削除は挙動に影響しない

その他、`grep` で `MainHandler.cmd_add` / `exec_update` などへの
参照がリポジトリ内に残っていないことも確認した（テスト側の
パッチ先の付け替えのみで一貫している）。

## 確信度の低い所感

無し。

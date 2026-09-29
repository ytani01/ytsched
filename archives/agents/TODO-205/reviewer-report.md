# TODO-205 reviewer 報告

対象: `git diff`（`src/ytsched/trash_handler.py` の `_restore()`、
`tests/test_web.py` の `test_restore_todo_goes_to_todo_file_and_edit_opens`）

## 確信度の高い指摘

無し。

## 依頼の観点ごとの結果

1. `SchedUpdater.cmd_add()` と同じ分け方か: 同じ。`is_todo()` なら
   `add_sde(None, …)`、そうでなければ `add_sde(sde.date, …)`
   （`sched_update.py:304-309`）。
2. `restored.is_todo()` と元の `sde.type`: 一致する。`SchedDataEnt.__init__`
   は `type` を加工せずに持ち（`ytsched.py:111`）、`is_todo()` は `type` の
   先頭だけで決まる（`ytsched.py:332`）。
3. redirect の `?date=restored.date`（報告のみ）: 通常の ToDo の追加でも
   `MainHandler.exec_cmd()` が `modified_date = sde.date`（締切日）に
   戻している（`main_handler.py:121-123`）ので、揃っている。
4. `add_sde(None, …)` / `save()` の経路: `get_sdf(None)` が `ToDo.jsonl` の
   `SchedDataFile` を返し、`_dirty_sdf[None]` に載って `save()` で書かれる
   （`ytsched.py:967`・`1051-1071`・`1107-1121`）。問題なし。
5. 新テストの強さ（読み）: 修正を戻すと `assert not self.data_path(DATE1).exists()`
   で落ち、仮にそこを外しても `ToDo.jsonl` の `read_text()` が
   `FileNotFoundError`、編集画面は `get_sdf(None)` で見つからず 404 になる。
   妥当。
6. `_restore_id()` が ToDo を含めて走査しているか: 含めている。
   `SchedData.max_version()` → `SchedDataFile.list_all_files(include_trash=False)`
   が `ToDo.jsonl` を足している（`ytsched.py:555-557`）。ゴミ箱は
   `TrashFile.max_version()` が見る。

他に `add_sde()` を呼ぶのは `holiday.py:183`（祝日の追加で ToDo ではない）
だけで、同じ不具合を持つ呼び出し元は残っていない。

## 確信度の低いもの

- 「ToDo なら `None`、そうでなければ `date`」の分け方が
  `SchedUpdater.cmd_add()` と `TrashHandler._restore()` の 2 か所に
  なった。どちらも 1 行なので今は害が無い。3 か所目ができるなら
  `SchedData` 側で決める形にまとめる余地がある、という程度（実害は未確認）。

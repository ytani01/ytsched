# TODO-087 reviewer への依頼

TODO-087 の変更を見てほしい。**挙動を変えないための移動**なので、
「移す前と後で挙動が変わっていないか」を最優先で見ること。

- 設計: `archives/agents/TODO-087/implementer-request.md`
- 実装の報告: `archives/agents/TODO-087/implementer-report.md`
- 変更範囲: `git diff`（新規の `src/ytsched/sched_update.py` も
  `git add -N` 済みなので diff に出る）。移す前のコードは
  `git show HEAD:src/ytsched/main_handler.py` で読める

## 特に見てほしいところ

1. **`exec_update()` の書き込み順**。`orig_date` / `date` / 時刻の
   取り出し（400 を投げうる）が、`cmd_del()` / `cmd_add()` より
   **先**に済んでいるか。TODO-027 で決めた「書き込みが 1 つも
   起きる前に弾く」が保たれているか
2. `try` / `finally` の `self._sd.save()`（TODO-077）が残っているか。
   例外が出たときの挙動が変わっていないか
3. ToDo 完了時の補正（`fix_todo_done()`）に入る条件が同じか
4. `cmd=add` のときに `sde_id` を捨てるところ、`new_sde.is_todo()` の
   ときに `date` を `None` にするところ
5. `get_modified_sde()` が 404 を投げなくなった代わりに、
   `exec_cmd()` が同じステータス・同じメッセージで投げているか
6. `SchedUpdateForm` に詰め忘れ・詰め違いが無いか
   （フォームの引数名と、`SchedUpdater` が読む属性の対応）
7. 消した `exec_cmd(search_str)` の引数が、本当にどこからも
   使われていなかったか

## 見なくてよいもの（既知）

- `load_sched()` / `get()` の長さ（TODO-088 の範囲）
- `SchedLoadCond` の中身（TODO-088・TODO-091 の範囲）
- テストの docstring に残る旧い言い回し

報告は `archives/agents/TODO-087/reviewer-report.md`。返事は 5 行以内。

# TODO-080 reviewer への依頼

TODO-080（キャッシュがファイルの更新に追随しないのを直す）の実装が
終わった。**良いかどうか**を見てほしい。動作確認は verifier が別に行う。

- 実装の報告: `archives/agents/TODO-080/implementer-report.md`
- 依頼書: `archives/agents/TODO-080/implementer-task.md`
- 変更点は `git diff` で見られる（まだコミットしていない）

## 特に見てほしいところ

1. **TODO-077 で入れた `_dirty_sdf` との噛み合わせ。**
   `add_sde()` / `del_sde()` で変更した `SchedDataFile` が
   `_dirty_sdf` に入っている状態で、`get_sdf()` が「古い」と判断して
   **別のインスタンスに差し替える**と何が起きるか。
   保存されていない変更が捨てられる道が開いていないか。
   `exec_update()` の中で `get_sdf()` が再び呼ばれる経路があるか
2. `is_stale()` の判定。`(st_mtime, st_size)` で足りるか。
   ファイルが無い場合（`None`）の扱いが、あとからできた場合・
   消えた場合の両方で正しいか
3. `save()` のあとに `_stat_key` を持ち直す処理が、
   `SchedDataFile.save()` の**すべての経路**を通るか
   （空のファイルを書くとき、`skipped_lines` があるとき）
4. `DEF_CACHE_SIZE = 2000` の根拠のコメントが、実装と合っているか
   （`main_handler.py` の `months2weeks()` と `SEARCH_MODE_MAX_DAYS`
   を実際に見て確かめること）
5. 足したテストが、実装を戻すと落ちるものになっているか
6. `~/.claude/CLAUDE.md`・`CLAUDE.md` の決まりからの逸脱

## 決まりごと

- **コードを直さない。** 指摘するだけ
- **確信度の高い指摘に絞る。数を稼がない**
- 報告は `archives/agents/TODO-080/reviewer-report.md` に書く。返事は 5 行以内

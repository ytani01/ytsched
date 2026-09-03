# TODO-171 reviewer 報告

## 1. 復活の版の決め方に穴がある — 日付をまたいだ編集のあと、復活した ID が生きている予定と衝突する（確信度: 高）

`src/ytsched/trash_handler.py` の `_restore_id()` は、次の版を

- ゴミ箱の同じ UUID の最大版（`TrashFile.max_version()`）
- **「復活先の日付ファイル」＝ `self._sd.get_sdf(sde.date).sde`**
  （`sde.date` はゴミ箱に入っている行＝復活させる行自身の `date`）

の 2 か所の最大 + 1 で決めている。しかし、その UUID の「現在生きている」
予定が**別の日付に移っていた場合**、その最新版はこの 2 か所のどちらにも
現れない。

再現手順:

1. 予定 A を作る（`sde_id = U-1`、日付 2026-01-01）
2. A を編集し、**日付だけ 2026-01-02 に変更**して保存する
   （`update`/`fix` は `orig_date` と `date` を別々に持ち、日付を
   変えられる — `src/ytsched/edit_handler.py` 102〜124 行、
   `src/ytsched/main_binder.py` の `get_update_form()`）。
   `cmd_del(2026-01-01, U-1)` で `U-1`（日付 2026-01-01 のまま）が
   ゴミ箱へ、`cmd_add(U-2, 2026-01-02, ...)` で `U-2` が
   2026-01-02 のファイルに生きた状態でできる
3. ゴミ箱で `U-1`（trashed_at はそのとき）を復活させる
   （POST `/trash` `cmd=restore`）
4. `_restore_id()` は `sde.date = 2026-01-01` を見に行くが、そこには
   もう `U-2` は無い（2026-01-02 に移っている）。ゴミ箱側も `U-1` しか
   無いので `max_version = 1`。結果、復活する予定の ID は `U-2` になる
5. これは 2026-01-02 のファイルに**既にある生きた予定 `U-2` と完全に
   同じ `sde_id`**。2 つの日付ファイルに同じ ID の生きた予定が
   同時に存在してしまう

依頼書（`archives/agents/TODO-171/reviewer-task.md`）が名指ししている
「復活の版の決め方に穴がないか」に該当する。`docs/data-format.md` の
記述も「ゴミ箱と復活先の日付のファイルの両方」とだけ書いてあり、UUID の
現在の生きた場所を追いかける仕組みが無い点は実装・文書とも同じ穴を
持っている。

テストもこの経路を確認していない。`tests/test_web.py` の
`test_restore_keeps_uuid_and_increments_version` はゴミ箱の行だけを
直接書き込んで検証しており、生きている予定が絡むケースは無い
（`test_update_increments_version_and_original_goes_to_trash` は
編集で日付を変えないケース）。「復活先の日付ファイル」を見る部分は
実質どのテストからも踏まれていない。

## 確信度が低いもの

特に無し（上記以外は仕様どおりで、実装・テスト・文書とも一致していると
判断した）。

---

## 2 回目のレビュー（指摘 1 の直し）

`archives/agents/TODO-171/implementer-task-2.md` の指示どおりに直った。
確信度の高い問題は見つからなかった。

### 確認した内容

1. **指摘 1 の穴が塞がったか。**
   `SchedDataEnt.max_version()`（`ytsched.py`）が、
   `SchedDataFile.list_all_files(topdir, include_trash=False)` で
   日々のファイルと `ToDo.jsonl` を全走査して同じ UUID の最大版を探す
   形に変わった。`trash_handler._restore_id()` は
   `max(self._trash().max_version(uuid_part), self._sd.max_version(uuid_part), version) + 1`
   という素直な式になり、「復活先の日付のファイルだけを見る」という
   穴のあった経路は消えている。

   - 日付を変える編集のあとの復活: 私が最初に出した再現手順を
     そのままテストにした `tests/test_web.py` の
     `test_restore_after_date_change_does_not_collide_with_live_entry`
     が通ることを確認した。復活後の ID が生きている予定・ゴミ箱の行の
     どちらとも重ならないことを見ている
   - 復活を 2 回続けた場合: 専用のテストは無いが、`max_version()` は
     ディスク上のファイルを毎回読み直す作りで、`_restore()` は
     `self._sd.save()` を都度呼んで即座に永続化するため、1 回目の
     復活で増えた版は 2 回目の `_restore_id()` の走査で拾われる。
     単一プロセス・同期処理（Tornado のハンドラが 1 リクエストずつ
     順に処理される）という前提のもとでは、連続復活でも衝突する経路は
     見当たらなかった
   - ToDo が絡む場合: `SchedData.max_version()` は `ToDo.jsonl` も
     対象に含めており、`test_sd_max_version_scans_daily_and_todo_files`
     で日々のファイルと `ToDo.jsonl` に散らばった同じ UUID を拾うことを
     確認している。ToDo の復活（`sde.date is None`）は UUID だけで
     版を決めるので、日付に依存する前回の穴の影響を受けない

2. **`SchedDataFile.list_all_files()` への一本化が `IdFixer.find_files()`
   の対象を変えていないか。**
   `DAILY_GLOB`（`"[0-9][0-9][0-9][0-9]/[0-9][0-9]/[0-9][0-9].jsonl"`）
   は `IdFixer` にあったものと文字列まで同一のまま `SchedDataFile` へ
   移されている（`git show HEAD:src/ytsched/fix_id.py` と比較して確認）。
   `TODO_FNAME`（`"ToDo.jsonl"`）も同じ。`include_trash` の既定は
   `True` で、`IdFixer.find_files()` は `list_all_files(self.topdir)`
   をそのまま呼ぶだけなので、1 回目の直しで加わった
   `trash.jsonl` を含む対象範囲は変わっていない。`.bak`・`.cgi` に
   一致するパターンは無い

3. **`SchedData.max_version()` の走査が取りこぼさないか、別の UUID を
   誤って拾わないか。**
   `uuid_bytes not in raw_line` は「解析するかどうか」の前段の
   絞り込みに過ぎず、実際の一致判定は `SchedDataEnt.split_id()` の
   結果と `uuid_part` の完全一致で行っている。`detail` などに UUID の
   文字列がたまたま含まれていても、`sde_id` フィールドの比較で
   弾かれるので誤検出はしない。`tests/test_ytsched.py` の
   `test_sd_max_version_does_not_pick_up_other_uuid` で別 UUID を
   拾わないことを、`test_sd_max_version_scans_daily_and_todo_files` で
   複数ファイルにまたがる同じ UUID を取りこぼさないことを確認している

4. **テストがこの穴を実際に踏んでいるか。**
   上記のとおり `test_restore_after_date_change_does_not_collide_with_live_entry`
   が私の再現手順をそのまま踏んでおり、`restored_sde_id != live_sde_id`・
   `restored_sde_id != sde_id`・`restored_sde_id == SchedDataEnt.next_id(live_sde_id)`
   を確かめている。実際に穴を踏むテストになっている

### 確信度が低いもの

特に無し。

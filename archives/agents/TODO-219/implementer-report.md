# implementer 報告（TODO-219）

## 変更
- `src/ytsched/trash.py`: 読み取りを `_parse_line()`、例外の組を `_BAD_LINE` にまとめた。`entries()`/`count()`/`delete_many()` が使う。警告・飛ばす/残す扱いは同じ。`delete()` を削除
- `src/ytsched/ytsched.py`: `SchedDataEnt.get_date/set_date`、`SchedData.get_keys` と `# self.__log` のコメント行（複数行の 1 件を含む）を削除
- `tests/test_trash.py`: `delete()` を `delete_many({...}) == 0` に書き換え
- `tests/test_ytsched.py`: `test_get_date`/`test_set_date`/`test_set_date_none_is_today` を削除。`set_date` を使う 1 件は `sde.date = ...` に
- 項目 5（click_utils）は取りやめの指示で、一度直したが `git checkout` で戻した（差分なし）
- `TODO.md`: 項目 1〜4 のチェックを入れた（項目 5 は入れていない）

## 検証
fmt / lint / typecheck 通過、pytest 719 件通過（click_utils を直した状態での実行。その後の差分は元に戻しただけ）。`docs/`・`src/README.md` に消したメソッドの記述は無かった。

## 判断
- `get_keys()` を使う LRU・破棄のテスト 2 件は、キャッシュ順の確認で他に見るものが無いため、削除せず `sd._sdf_cache`（キーは date）を直接見る形に変えた。private 参照を避けるなら削除に変えられる
- 消した `get_date/set_date` のテストが見ていた挙動（日付のタプル化、`None` で今日）は、他のテストでは見ていない。メソッドごと無くなったので問題なし
- `_discarded`/`_i` はコメント削除で未使用になったが、ruff は通るので残した

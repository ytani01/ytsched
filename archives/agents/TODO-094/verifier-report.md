# TODO-094 verifier report

「細かいもの」3 件の実装を確認した。**すべて OK。不具合なし。**

## 確認したコマンドと結果

- `mise run fmt` … ○ ruff format 31 files unchanged / ruff check All checks passed
- `mise run typecheck` … ○ basedpyright 0 errors / mypy Success (28 source files)
- `mise run lint` … ○ ruff・eslint・prettier いずれも pass
- `mise run test` … ○ `481 passed in 63.93s`
- `uv run ytsched webapp --help | grep -i size` … ○
  `-l, --size-limit INTEGER  upload size limit, default=104857600`
- `git grep -n 'SEARCH_MODE_DAYS\|SEARCH_MODE_MAX_DAYS' -- src/ tests/` … ○ 空（exit 1）
- `git grep -n 'size_limit\|size-limit' -- src/ tests/ docs/ README.md` … ○
  option は `--size-limit`、Python 識別子 `size_limit` は据え置きで一貫

## 個別の確認

1. 定数の改名
   - `SchedLoader.SEARCH_ENOUGH_DAYS`(365) / `handler_util.SEARCH_HARD_LIMIT_DAYS`(1825)
     に改名済み。値は変わっていない。
   - コメント・docstring の参照（`handler_util.py` `date_range()`、
     `sched_load.py` `load_sched()` の Returns/Notes、`ytsched.py:753` の
     コメント、`main_handler.py:52` のコメント）もすべて追随。
   - `sched_load.py:132` のコメント書き直しは、`load_sched()`
     （旧 358 行あたり）のロジックと整合。`date_from1`（`SEARCH_ENOUGH_DAYS`）は
     `if search_count > 0` の中で打ち切り判定に使われており、
     「1 件でも当たったら、ここまで戻って打ち切る」という新コメントどおり。

2. `mk_todo_by_date()` の二重照合除去
   - `load_todo()`（`sched_load.py:178`）が `search_match(search_re, sde)` で
     すでに `todo_sde` を絞っている。`mk_todo_by_date()` の中の同じ照合は
     冗長で、除去しても挙動は変わらない。
   - `search_re` 引数の削除に呼び出し側（`main_handler.py:268`、
     `tests/test_main_handler.py` の `call_load_sched`）が追随。
   - `todo_days_value` が負のとき空 dict を返す分岐（`sched_load.py:225` 付近）は
     変更なし。
   - `test_main_handler.py` の検索モード関連テストを含む 481 件が pass。

3. CLI オプション名
   - `__main__.py:136` が `--size-limit`（`-l` は据え置き、識別子
     `size_limit` は変更なし）。`--help` で確認済み。

## main の判断が要る点

なし。

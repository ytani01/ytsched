# TODO-094 verifier への依頼

「細かいもの」3 件を実装した。動くかを確かめてほしい。**コードは直さない**。
見つけたことは報告ファイルに書き、直すかは管理者が決める。

## 変更の内容

1. **定数の改名**
   - `SchedLoader.SEARCH_MODE_DAYS` → `SchedLoader.SEARCH_ENOUGH_DAYS`（365）
   - `handler_util.SEARCH_MODE_MAX_DAYS` → `handler_util.SEARCH_HARD_LIMIT_DAYS`（1825）
   - コメント・docstring・テストの参照も追随。`sched_load.py:132` の
     コメントは、挙動と食い違っていたので書き直した
     （旧「1 件も当たらないときに諦める日数」→ 新「1 件でも当たったら、
     ここまで戻って検索を打ち切る日数」）。
   - `SEARCH_ENOUGH_DAYS`（365）は `if search_count > 0` の中で使われ、
     1 件でも当たったあとの打ち切り。`SEARCH_HARD_LIMIT_DAYS`（1825）は
     さかのぼりの絶対の上限。テスト
     `test_search_mode_stops_365_days_after_first_hit` /
     `test_search_mode_max_days_when_nothing_is_found` で挙動を確認できる。

2. **`mk_todo_by_date()` の二重 `search_match()` 除去**
   - `mk_todo_by_date()` に渡る `todo_sde` は `load_todo()` が同じ
     `search_re` で絞ったあとのもの。中の `search_match()` 照合を削除し、
     不要になった `search_re` 引数も外した。
   - 呼び出し側（`main_handler.py`、`tests/test_main_handler.py` の
     `call_load_sched`）も追随。

3. **CLI オプション名**
   - `webapp` の `--size_limit` → `--size-limit`（`-l` は据え置き、
     Python 側の識別子 `size_limit` は変更なし）。

## 確かめてほしいこと

- `mise run fmt` / `mise run typecheck` / `mise run lint` / `mise run test`
  が通ること（main では全部通っている。再実行して確認）。
- `uv run ytsched webapp --help` に `-l, --size-limit INTEGER` と出ること。
- `git grep -n 'SEARCH_MODE_DAYS\|SEARCH_MODE_MAX_DAYS'` が空であること
  （archives 配下は歴史なので対象外。src/ tests/ を見る）。
- 二重の `search_match()` を外して挙動が変わっていないこと（検索モードで ToDo が
  混ざる／混ざらないの境界。`todo_days_value` が負のとき空 dict）。

## 前提

- アプリ起動の確認では `--datadir` に一時ディレクトリを指定する。
- `mise run upgradeproject` は走らせない。

## 報告

`archives/agents/TODO-094/verifier-report.md` に書く。返事は 5 行以内で
「終わったか・報告ファイルのパス・判断が要る点」。

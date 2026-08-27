# TODO-088 implementer 報告

## 変更・作成したファイル

- `src/ytsched/sched_load.py`（新規）: `filter_match()` / `search_match()`
  （`MainHandler` からそのまま移動）、`SchedLoadCond` / `SchedSearchCond`
  （依頼どおりのフィールド）、`SchedLoader`（`load_todo()` /
  `mk_todo_by_date()` / `_load_day()`（新規private） / `load_week()` /
  `search()`）。`sched_update.py` と同じヘッダ・docstring の書き方に揃えた
- `src/ytsched/main_handler.py`: `SchedLoadCond` の定義・`load_todo()` /
  `mk_todo_by_date()` / `load_sched()` / `filter_match()` / `search_match()`
  を削除し、`sched_load` から import。`initialize()` に
  `self._loader = SchedLoader(sd)` を追加。`get()` は `search_mode` の分岐
  で `self._loader.search()` / `self._loader.load_week()` を呼ぶだけにし、
  週の組み立ては新設の `mk_weeks()`（private）へ出した。`SEARCH_MODE_DAYS`
  と、未使用になった `import dataclasses` / `SchedDataEnt` の import を削除
- `src/ytsched/webroot/templates/main.html`: `data-monday` の条件を
  `{% if w['monday'] %}` → `{% if not search_mode %}` に変更（1 行のみ）。
  検索モードでも `monday` に実際の月曜を入れるようにしたため
- `tests/test_main_handler.py`: import を `sched_load` からに変更。
  `call_load_sched()` を `SchedLoader` 経由（`search_re` の有無で
  `search()`/`load_week()` を呼び分け）に書き換え。
  `test_mk_todo_by_date_is_called_once_per_request` は
  `SchedLoader.mk_todo_by_date` へパッチ。`MainHandler.SEARCH_MODE_DAYS`
  の参照 2 か所を `SchedLoader.SEARCH_MODE_DAYS` に変更

## 挙動を変えないための設計判断

- `_load_day(date1, cond, search_re=None, extra_sde=None)` を共通部分にし、
  `search_re` は検索のときだけ、`extra_sde`（`todo_today_sde`）は
  `load_week()` が「今日」の日だけに渡す形にした。ソートは
  `_load_day()` の中で 1 回だけ行い、`extra_sde` を **ソートの前に**
  追加することで、元の `load_sched()` の「file → todo_by_date →
  todo_today_sde → sort」という順序（同着時の並びに影響）を保った
- `search()` の打ち切り判定（`search_count`/`date_from1` の比較順序、
  「1 件以上当たったときだけ判定」）は元の `while` の構造をそのまま
  `_load_day()` 呼び出しに置き換えただけで、条件式は変えていない
- `get()` 側で `search_mode` 判定後 `search_re` を `SchedSearchCond` に
  渡す箇所は型の上で `re.Pattern[str] | None` → `re.Pattern[str]` の絞り
  込みが要るため `assert search_re is not None` を 1 行追加した
  （`search_mode = search_re is not None` の直後の分岐内なので実害無し）

## 確認したこと

- `uv run ruff format` / `ruff check` / `basedpyright` / `mypy` /
  `pytest`（`mise run fmt` / `lint` / `test` 経由）を実行し、全て成功
  （pytest 475 件パス）
- 一時ディレクトリ（`--datadir`）でアプリを起動し、`curl` で
  `date=2021-03-15` の通常表示に `data-monday` が 3 週分出ること、
  `search_str=test` の検索表示には `data-monday` が出ず
  `data-offset="0"` の 1 要素だけになることを目視確認

## 気づいたが直していないもの

- `mk_todo_by_date()` が `search_match()` をもう一度かけている無駄
  （TODO-094 の範囲、依頼書の「変えないこと」どおり）
- `SEARCH_MODE_DAYS`/`SEARCH_MODE_MAX_DAYS` という名前（TODO-094 の範囲）

## うまくいかなかったところ

特になし。テストの期待値も変更不要だった。

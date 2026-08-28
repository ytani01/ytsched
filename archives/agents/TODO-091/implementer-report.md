# TODO-091 実装報告（implementer）

## やったこと

依頼書（scratchpad/impl-brief.md）の 2 点を、挙動を変えずに機械的置き換え。

### 1. テンプレートへ `sd` を渡すのをやめる

- `src/ytsched/main_handler.py` `get()` の `render(...)`:
  `sd=self._sd` を削除し `cache_size=self._sd.get_cache_size()` を渡す。
- `src/ytsched/webroot/templates/main.html` L330:
  `({{ sd.get_cache_size() }})` → `({{ cache_size }})`。

### 2. `sched` / `weeks` の dataclass 化

- `src/ytsched/sched_load.py`:
  - `SchedSearchCond` の直後に `SchedDay`（`date` / `is_holiday` / `sde`）と
    `SchedWeek`（`offset` / `monday` / `sched`）を追加。`@dataclasses.dataclass`、
    frozen にしない。
  - `_load_day()`: 戻り値型 `tuple[dict, int]` → `tuple[SchedDay, int]`、
    末尾の `day = {...}` → `SchedDay(...)`、docstring の `day: dict` 説明を修正。
  - `load_week()` / `search()`: 戻り値型注釈 `list[dict]` → `list[SchedDay]`、
    docstring の `sched: list[dict]` を `list[SchedDay]` に。
  - `search()`: `if not day["sde"]:` → `if not day.sde:`。
- `src/ytsched/main_handler.py`:
  - import を `SchedDay` / `SchedWeek` 追加の複数行に。
  - `mk_weeks()`: 引数 `sched: list[dict]` → `list[SchedDay]`、戻り値
    `list[dict[str, object]]` → `list[SchedWeek]`、docstring も同様。
    検索モードの `return [{...}]` → `[SchedWeek(offset=0, monday=monday, sched=sched)]`、
    `weeks: list[dict[str, object]]` → `list[SchedWeek]`、
    ループ内 `weeks.append({...})` → `weeks.append(SchedWeek(...))`。
- `src/ytsched/webroot/templates/main.html`: 週ループの
  `w['offset']` / `w['monday']` / `w['sched']` を `w.offset` / `w.monday` /
  `w.sched` に、`sched_ent['date']` / `sched_ent['sde']` を属性参照に。
  （`{% set obj = {'date': ...} %}` 等の別の dict リテラルには触れていない）
- `tests/test_main_handler.py`: `call_load_sched()` を使うテスト（L915・935・953・
  970・971）の `s["date"]` / `s["is_holiday"]` / `day["sde"]` を属性参照に。
  `skipped == opened` の比較は dataclass の `__eq__` で通るのでそのまま。
  L516・530 の `data["date"]` は JSON パース結果なので触っていない。

## 確認したこと

- `mise run fmt` / `typecheck`（basedpyright・mypy とも 0）/ `lint` / `test`
  （482 passed）をまとめて 1 回ずつ。すべて通過。
- `test_browser.py`（実ブラウザで main.html を描画。data-offset / data-monday /
  週パネルを見るもの 22 件）も通過。
- 一時 datadir でアプリを起動し `curl` で確認。フッターに `(1)` と
  キャッシュ件数が出た。

## 単独で決めた判断

- import 文は依頼書どおり `SchedDay` と `SchedWeek` を足すだけだが、ruff の
  整形で複数行の丸括弧形式になった（`fmt` に従った）。

## 残したもの

- なし（範囲外への波及は確認した限り無し）。

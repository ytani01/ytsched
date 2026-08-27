# TODO-079. 表示の条件をまとめて `load_sched()` の引数を減らす

|      | main | 担当 |
|------|------|------|
| 見込み | Sonnet 5 / effort medium | implementer + verifier |
| 実施 | Opus 5 / effort high | implementer + verifier |
| 消費 | output 8,750 / cache_creation 130,544 / 概算 $2.4 |
|      | main 61% + implementer 24% + verifier 13% + wording 2%（料金の割合） |

## きっかけ

基本設計のレビュー（`docs/design-review.md` の F）で挙がった。
元は TODO-021 で reviewer が挙げ、「挙動を変えない項目の範囲を超える」
として残されていた 1 件。

TODO-069 で週の数だけ `load_sched()` を繰り返し呼ぶようになり、
9 個の引数のうち 8 個は毎回同じ値を渡していた。さらに
`mk_todo_by_date()` が呼び出しごとに `todo_sde` を全件走査するので、
前後 1 ヶ月（9 週）なら同じ集計を 9 回やっていた。

## やったこと

**挙動は変えていない。**

- `main_handler.py` のモジュール直下に dataclass の `SchedLoadCond` を
  作り、`filter_re` / `filter_neg` / `search_re` / `search_n` /
  `todo_days_value` / `todo_sde` / `todo_today_sde` / `todo_by_date` を
  持たせた。`search_mode` は `search_re is not None` そのものなので、
  フィールドにせずプロパティにした
- `load_sched(self, date, cond)` の形にした。本体は変えず、冒頭で
  `cond` の中身を同名のローカル変数へ展開している
- **`todo_by_date` を `SchedLoadCond` を作るときに 1 回だけ作る。**
  週ごとに作り直さなくなった

`mk_todo_by_date()` は `search_match()` を使うので、インスタンスの
メソッドのまま残した。

## テスト

- `tests/test_main_handler.py` の `call_load_sched()` を新しい形に直した。
  観点は変えていない
- `test_mk_todo_by_date_is_called_once_per_request` を足した。
  複数週にまたがる 1 リクエストで 1 回しか呼ばれないことを見る
- `mise run lint` 通過。`uv run pytest tests` 460 passed

verifier が、変更前のコードを `git worktree` で用意し、**条件を変えた
8 パターン**（何も付けない／離れた週／検索／絞り込み／`todo_days` を
変えた場合と負の値／`LoadMonths` を 0 と 2）で HTML を突き合わせた。
差はバージョン表示だけで、本文に違いは無い。

分担と報告は [`archives/agents/TODO-079/`](../agents/TODO-079/README.md)。

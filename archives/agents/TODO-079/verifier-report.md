# TODO-079 verifier 報告

## 1. lint / pytest

- `mise run lint`: ○（`ruff format` 26 files left unchanged / `ruff check` All checks
  passed / `basedpyright` 0 errors, 0 warnings, 0 notes / `mypy` Success: no issues
  found in 23 source files）
- `uv run pytest tests`: ○（460 件全部通過）

## 2. HTML の突き合わせ（挙動が変わっていないこと）

`git worktree add <一時dir> HEAD` で変更前のコードを用意し、同じデータ
（`/tmp/.../scratchpad/dataA`＝旧コード用、`dataB`＝新コード用。予定 3 件・
ToDo 3 件を同じ内容で作成）を使い、`--datadir` を指定した 2 つのサーバ
（旧:18801 / 新:18802）を立てて、次のパターンで `diff` した
（`<title>` と `Version` の行はコミットハッシュ由来で毎回変わるので除外）。

- `/`（何も付けない）: ○ IDENTICAL
- `/?date=2021-03-01`（今日から離れた週）: ○ IDENTICAL
- `/?search_str=検索対象`: ○ IDENTICAL
- `/?filter_str=予定`: ○ IDENTICAL
- `/?todo_days=5`: ○ IDENTICAL
- `/?todo_days=-3`（負の値）: ○ IDENTICAL
- `conf.json` の `LoadMonths` を `0` にしたとき（`/?date=2021-03-01`）: ○ IDENTICAL
- `conf.json` の `LoadMonths` を `2` にしたとき（`/?date=2021-03-01`）: ○ IDENTICAL

依頼書にあった「`search_str` は POST」は実際には不要だった。`main_handler.py`
の `get()` が `get_conf_arg()` で GET のクエリ引数からも `search_str` /
`filter_str` / `todo_days` を読むため、GET だけで全パターンを再現できた。

差分はすべてバージョン表示（`git describe` の値、worktree と本体で違う）
だけで、本文（予定・ToDo・週の表示など）に差は無かった。

## 3. `mk_todo_by_date()` が 1 回しか呼ばれないこと

- 追加されたテスト `test_mk_todo_by_date_is_called_once_per_request` を
  単独実行: ○ PASSED
- `main_handler.py` を見ると、`mk_todo_by_date()` の呼び出しは `get()` 内の
  1 か所（290 行目）だけで、週ごとのループ（`load_sched()` 呼び出し）の
  外にある。実際に立てたサーバで `LoadMonths=2`（9 週ぶん表示）の状態で
  複数週を含むページを取得しても例外・重複計算の兆候は無かった。

## 4. アプリの起動・画面表示

- 新コード（`--datadir <一時dir>`）を起動し、`/` と `/?date=2021-03-01` の
  HTTP ステータスはいずれも 200
- 取得した HTML に `{{`・`{%` の生の残りは無し。ログ（`new.log`）に
  Traceback・Exception は無し

## 判断が要る点

特になし。挙動に差は見つからなかった。

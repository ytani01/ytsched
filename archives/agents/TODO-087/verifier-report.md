# TODO-087 verifier 報告

## 1. `uv run pytest -q`

○ 475 passed in 52.40s

## 2. `mise run lint`

○ ruff format: 29 files left unchanged
○ ruff check: All checks passed!
○ basedpyright: 0 errors, 0 warnings, 0 notes
○ mypy: Success: no issues found in 26 source files

## 3. アプリを起動して更新の 4 経路を叩く

`--datadir` は一時ディレクトリ（`/tmp/claude-.../scratchpad/ytsched-data`）を指定。

- `cmd=add`（date=2026-09-01, 10:00-11:00, title=TestEvent）
  → 302, `Location: /ytsched/?date=2026-09-01`
  → `2026/09/01.jsonl` に 1 行増えた（○）
- `cmd=fix`（同じ sde_id で time_start=12:00, title=FixedEvent）
  → 302, `Location: /ytsched/?date=2026-09-01`
  → 内容が入れ替わり、行数は 1 のまま（○ 行が増えていない）
- `cmd=update`（time_start=14:00, title=UpdateEvent）
  → 302, `Location: /ytsched/edit/?date=2026-09-01&sde_id=<uuid>&todo_flag=false`
  （○ `edit/` の URL に `date`・`sde_id`・`todo_flag` が付いている）
- `cmd=del`
  → 302, `Location: /ytsched/?date=2026-09-01`
  → `2026/09/01.jsonl` の行が消えた（空ファイル、○）

## 4. エラーの経路

- `cmd=add` に `date=2026-13-45`
  → **400 Bad Request**（○ 書き込み前に断る）。新しいデータファイルは作られなかった
    （既存の `2026/09/01.jsonl` / `.jsonl.bak` 以外にファイルは増えていない）
- `cmd=add` に `time_start=99:99`（date=2026-09-05）
  → **400 Bad Request**（○）。`2026/09/05.jsonl` は作られなかった

## 5. サーバのログ

例外・トレースバックは出ていない（○）。400 の 2 件は下記の WARNING のみ:

```
WARNING handler_util.py:57 convert_value()> date='2026-13-45': month must be in 1..12, not 13 .. ignored
400 POST /ytsched/ (127.0.0.1): invalid date: date='2026-13-45'
WARNING handler_util.py:57 convert_value()> time_start='99:99': hour must be in 0..23, not 99 .. ignored
400 POST /ytsched/ (127.0.0.1): invalid time: time_start='99:99'
```

## 結論

依頼された確認はすべて○。不具合は見つからなかった。挙動は移行前と変わっていないと判断できる。

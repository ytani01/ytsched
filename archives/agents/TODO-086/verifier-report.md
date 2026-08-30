# TODO-086 verifier 報告

## 結果

- ○ `uv run pytest tests/test_trash.py tests/test_web.py -q` — 137 passed in 3.20s
- ○ `uv run ytsched webapp --datadir /tmp/ytsched-todo086-biK3uK --port 19886` —
  `/ytsched/trash` は HTTP 200。取得した HTML に「ゴミ箱」があり、`{{` と
  `{%` は残っていない。確認した PID 3453444 / 3453452 は停止済み。
- ○ `uv run ruff check src/ytsched/trash.py src/ytsched/trash_handler.py tests/test_trash.py tests/test_web.py` — All checks passed!

## 実行コマンド

```console
uv run pytest tests/test_trash.py tests/test_web.py -q
uv run ytsched webapp --datadir /tmp/ytsched-todo086-biK3uK --port 19886
curl -sS -o /tmp/ytsched-todo086-trash.html -w '%{http_code}\n' http://127.0.0.1:19886/ytsched/trash
rg -n '<title>|ゴミ箱|\{\{|\{%' /tmp/ytsched-todo086-trash.html
pgrep -af '[y]tsched webapp|[p]ython.*ytsched'
kill 3453444 3453452
pgrep -af '[y]tsched webapp --datadir /tmp/ytsched-todo086-biK3uK --port 19886|[p]ython.*ytsched.*todo086-biK3uK'
uv run ruff check src/ytsched/trash.py src/ytsched/trash_handler.py tests/test_trash.py tests/test_web.py
```

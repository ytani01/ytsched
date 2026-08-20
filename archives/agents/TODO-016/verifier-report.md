# TODO-016 verifier 報告

working tree（未コミット）の変更に対して確認した。

## 1. lint / pytest

- `mise run lint` → ○。ruff（14 files left unchanged, All checks
  passed）/ basedpyright（0 errors, 0 warnings, 0 notes）/
  mypy（Success: no issues found in 14 source files）
- `uv run pytest tests` → ○。178 passed（1.24s）

## 2. アプリの起動確認

一時ディレクトリ
`/tmp/claude-649/.../scratchpad/ytsched-datadir` を `--datadir` に
指定し、ポート 10099 で起動して curl で確認した。

- `date` を空にした非 ToDo の `cmd=add` POST
  （`sde_type=普通`, `sde_id=`（空文字を明示的に付ける必要あり。
  `get_argument("sde_id")` はデフォルト無しのため未指定だと 400 に
  なる。既知の仕様で不具合ではない）
  → HTTP 200。`ToDo.cgi` は作られず、
  `<datadir>/2026/08/20.cgi` に 1 行入った（○）
  ```
  7dbf8def-...	2026/08/20	10:00-11:00	普通	タイトル1
  ```
- ToDo（`sde_type=□普通`）の `cmd=add` → HTTP 200。
  `<datadir>/ToDo.cgi` に 1 行入った（従来どおり、退行なし）
  ```
  89f6230a-...	2026/08/20	:-:	□普通	ToDoタイトル
  ```
- `/ytsched/edit?date=2021-03-01&sde_id=no-such-id`
  → **HTTP 404**（○）
- `/ytsched/edit?date=&sde_id=no-such-id&todo_flag=true`
  → **HTTP 404**（○）

サーバログ（`ytsched-server.log`）:
```
404 GET /ytsched/edit?date=2021-03-01&sde_id=no-such-id (::1):
  sde not found: sde_id=no-such-id
404 GET /ytsched/edit?date=&sde_id=no-such-id&todo_flag=true (::1):
  sde not found: sde_id=no-such-id
```
（`Missing argument sde_id` の 400 が 2 件あるが、これは自分が
最初の curl コマンドで `sde_id` パラメータを付け忘れたことによる
ものであり、実装の不具合ではない。付け直した 2 回目で 200 を確認）

## 3. 一覧・追加・修正・削除の一連の流れ

- 一覧表示 `GET /ytsched` → 200。`main.html` に `{{` `{%` の
  生残りなし（`grep -c` で 0 件）
- 新規追加画面 `GET /ytsched/edit?date=2021-03-01` → 200。同じく
  `{{` `{%` の生残りなし
- 追加した非 ToDo（`sde_id=7dbf8def-...`）を `cmd=fix` で修正
  → 200、ファイルの内容が
  `10:00-11:30 タイトル1修正` に更新された
- 同じ `sde_id` を `cmd=del` で削除 → 200、ファイルから
  該当行が消えた（空ファイルになった）

サーバログに traceback / Exception の出力は一切無かった
（`grep -i "traceback\|error\|exception"` で該当行なし。
既知の 404 ログメッセージ以外に "error" 文字列も出ていない）。

起動していたプロセス（PID 433705 とその子プロセス）は確認後に
kill 済み。実データディレクトリ `~/ytsched/data` には触れていない。

## 結論

依頼された 3 点はすべて確認でき、いずれも報告どおりに動作した。
main の判断が要る点は無い。

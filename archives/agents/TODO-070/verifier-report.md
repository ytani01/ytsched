# TODO-070 verifier 報告

## 1. mise run fmt / typecheck / lint / test

- `mise run fmt` → ○（ruff format: 26 files left unchanged / ruff check: All checks passed）
- `mise run typecheck` → ○（basedpyright 0 errors, mypy 23 source files 成功）
- `mise run lint` → ○（fmt + typecheck と同じ、エラー無し）
- `mise run test` → ○（`uv run pytest tests`、453 passed in 27.63s）

## 2. 消し残しの grep

```
grep -rniE 'blink|plus-square|my-add-btn' src/ tests/ docs/
```
→ `my.css:25` の `BlinkMacSystemFont`（フォントスタックの一部、無関係）のみ。
`blink` クラス・`.my-add-btn`・`#plus-square` の消し残しは無し。

`modified_sde_id` は `main_handler.py` の `exec_cmd()` 内部
（638〜703 行、1134〜1218 行）にのみ残っており、依頼どおり
「編集画面へのリダイレクト先を決める」用途に限定されている。
`post()`（137〜210 行）の戻り値の受け取りは `modified_date, edit_url` で、
URL へは載っていない。

## 3. アプリの起動確認

`uv run ytsched webapp --datadir <mktemp -d> --port 18077` を
`run_in_background` で起動し、以下を curl で確認。

- `GET /ytsched/` → 200。`{{`/`{%` の生残りなし（`grep -c` で 0）
- `POST /ytsched/` に `cmd=add, date=2026-08-27, sde_type=会議,
  title=検証用予定` → 302、`Location: /ytsched/?date=2026-08-27`
  （`modified_sde_id` はクエリに無い＝依頼どおり）
- リダイレクト先 `GET /ytsched/?date=2026-08-27` → 200、
  追加した「検証用予定」が表示される。日付欄には
  `onmousedown="doGet('/ytsched/edit/', {...})"` が残っており、
  クリックで編集画面へ行く仕組みは生きている
- `GET /ytsched/edit/?date=2026-08-27&sde_id=` → 200、
  `{{`/`{%` の生残りなし
- サーバのログ（`/tmp/ytsched_verify.log`）に例外・トレースバックなし
  （自分が URL プレフィックス無しで叩いた 404 が 1 件記録されているのみ）
- 確認後 `pgrep` で PID (1656076) を確認し `kill`、再度 `pgrep` で
  プロセスが消えたことを確認

## 4. 壊れの有無

見つからず。削除しすぎ・消し残しとも無し。

## 判断が要る点

無し。

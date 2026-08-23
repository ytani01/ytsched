# TODO-034 verifier報告

## lint / format / typecheck / pytest

すべて実行し、いずれも問題なし。

```
$ uv run ruff check src tests
All checks passed!

$ uv run ruff format --line-length 78 --check src tests
21 files already formatted

$ mise run typecheck
# basedpyright
0 errors, 0 warnings, 0 notes
# mypy
Success: no issues found in 18 source files

$ uv run pytest
============================= test session starts ==============================
collected 404 items
...
============================= 404 passed in 2.88s ==============================
```

（TODO-034 で足した `test_date2path_expands_topdir` /
`test_date2path_todo_expands_topdir` の 2 件を含む。）

## アプリの起動確認

一時ディレクトリを `--datadir` に指定して起動。

```
$ uv run ytsched webapp --datadir /tmp/.../scratchpad/ytsched-verify --port 18765
```

- `curl http://localhost:18765/` → `200`。HTML に `{{ }}` / `{% %}` の
  生残りなし
- ログ（`/tmp/.../scratchpad/webapp.log`）に例外・トレースバックなし
  （`INFO webapp.py:129 main()> start server: run forever ..` のみ）

### 一覧 → 編集 → 更新 → 削除

1. `POST /ytsched/` で `title=verify-test-entry` の予定を追加
   → `2026/08/23.jsonl` に 1 行書かれることを確認
2. `GET /ytsched/edit?date=2026-08-23&sde_id=<id>&todo_flag=false`
   → 編集画面が返る。隠しフィールド
   `<input id="orig_date" name="orig_date" type="hidden" value="2026-08-23" />`
   が、その行が入っているファイルの日付（`2026-08-23`）になっている
   ことを確認
3. 一覧画面（`GET /ytsched/`）を取得し、追加した予定のクリック部分
   （`sde.html` の `onmousedown="doPost(...)"`）を確認。
   `orig_date:` が渡されていない（`date`・`sde_id`・`todo_flag`・
   `cur_date`・`date_from`・`date_to`・`search_str` のみ）ことを確認。
   直前に `<!-- 編集画面の orig_date は EditHandler が決めるので、
   ここからは送らない (TODO-034) -->` のコメントも展開されて出力
   されている
4. `POST /ytsched/` に `cmd=update` で `title=verify-test-entry-updated`
   を送信 → `200`、ファイルの中身がタイトル変更後の内容に書き換わる
   ことを確認
5. `POST /ytsched/` に `cmd=del` を送信 → `200`、ファイルが空になる
   ことを確認

ToDo をブラウザからクリックする経路は試していない。ただし `sde.html`
の差分は `{% if sde.is_todo() %}` の判定そのものには触れておらず、
ToDo かどうかで分かれる部分は前と同じ。編集画面で ToDo の
`orig_date` が出ないこと自体は `EditHandler.get()` が決めており
（TODO-029）、そこも触っていない。`tests/test_web.py` に
「ToDo は `orig_date` が付かない」を見るテストがあり、通っている。

### `~` 付き `--datadir`

```
$ uv run ytsched webapp --datadir "~/tmp-ytsched-verify-034" --port 18766
```

- `curl http://localhost:18766/` → `200`
- `POST /ytsched/` で `title=tilde-test` の予定を追加 →
  `$HOME/tmp-ytsched-verify-034/2026/08/23.jsonl` に正しく書かれる
  ことを確認（`~` が実ホームへ展開されている）
- 確認後、`~/tmp-ytsched-verify-034` は削除済み

サーバは確認後すべて `kill` 済み（`pgrep -f "port 18765"` /
`"port 18766"` で残存プロセス無しを確認）。

## 結論

依頼書の確認項目はすべて○。不具合は見つからなかった。判断が要る点は無し。

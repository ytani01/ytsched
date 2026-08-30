# TODO-106 verifier 報告

## 結果

- × `mise run lint`: `basedpyright` が `tests/test_main_handler.py:90:28` で
  1 error。`MainHandler` を `MainBinder` の `_ArgumentSource` として渡す箇所で、
  `get_argument()` の型が Protocol と一致しない。
- ○ `uv run pytest tests --ignore=tests/test_browser.py -q`: 483 passed in 5.66s。
- ○ `uv run pytest tests/test_browser.py -q`: 26 passed in 79.51s。
- ○ 指定の一時データディレクトリ・port 10106 で起動したサーバへ curl:
  一覧、検索、編集画面はいずれも HTTP 200。取得した HTML に `{{` / `{%` はなく、
  テンプレートが展開されていた。
- ○ `cmd=add&date=abc` の POST は HTTP 400。検証用サーバの PID
  3305657, 3305659, 3305662 は確認後に停止し、停止後の `pgrep` は該当なし。

## 実行コマンド

```sh
mise run lint
uv run pytest tests --ignore=tests/test_browser.py -q
uv run pytest tests/test_browser.py -q
mise run webapp -- --datadir /tmp/ytsched-todo106-verifier --port 10106
curl 'http://127.0.0.1:10106/ytsched/?date=2021-03-01'
curl 'http://127.0.0.1:10106/ytsched/?date=2021-03-01&search_str=%E4%BC%9A%E8%AD%B0'
curl 'http://127.0.0.1:10106/ytsched/edit/?date=2021-03-01'
curl -X POST -d 'cmd=add&sde_id=&date=abc&sde_type=%E4%BC%9A%E8%AD%B0&title=%E4%B8%8D%E6%AD%A3&place=&detail=' 'http://127.0.0.1:10106/ytsched/'
```

## 判断が要る点

`mise run lint` を通すには、`tests/test_main_handler.py:90` の
`MainBinder(handler)` における型の不一致を実装側で解消する必要がある。

## 型チェック修正後の再確認

- ○ `mise run lint`: basedpyright は 0 errors、mypy は 30 source files で
  Success。ruff、Prettier、ESLint も成功。
- ○ `uv run pytest tests/test_main_handler.py tests/test_web.py -q`:
  184 passed in 4.49s。

上記の型不一致は解消されており、判断が要る点はない。

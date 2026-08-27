# TODO-082 verifier 報告

## 1. lint / test

- `mise run lint` — fmt (28 files unchanged) / ruff check all passed /
  basedpyright 0 errors / mypy no issues。○
- `mise run test` — 475 passed。○

## 2. --help / x_data1

- `ytsched --help`: `YT scheduler`、コマンドは `migrate` / `webapp` のみ。○
- `webapp --help` / `migrate --help` とも文言に問題なし。○
- `x_data1` / `musicbox` / `sample package` の grep — 実コード・テスト・
  tools・docs には残っていない。design-review.md と TODO.md にのみ、
  修正前の問題点として記述が残っているが、これは経緯を記録した文書なので
  問題なし。○

## 3. migrate の tornado 非依存

`uv run python -c "...'tornado' in sys.modules"` → `False`。○

## 4. ruff 設定の移動

- `pyproject.toml` に `line-length = 78` と `extend-select = ["I"]` が
  移っている。`mise.toml` / `docs/Developer.md` からは該当オプションが
  消えている。○
- 81 文字の行を含む一時ファイルで `ruff format --check --diff` を実行し、
  折り返しが実際に効くことを確認（78 では折り返し、直前に 77 文字では
  素通り）。○
- import 順の乱れを含む一時ファイルで `ruff check` を実行し、`I001` が
  検出されることを確認。○
- 一時ファイルはすべて確認後に削除済み。

## 5. --size_limit の既定値

`webapp --help` の `default=104857600`。`100*1024*1024` と一致。○

## 6. アプリ起動

一時ディレクトリを `--datadir` に指定して起動、`curl` で
`/ytsched/` → `HTTP=200`。応答 HTML に `{{` `{%` の生残りなし。
ログに例外・トレースバックなし。プロセスは確認後に kill 済み。○

## 7. 消した属性・参照の残存確認

- `HandlerBase._app` / `_req`、`SchedDataFile.filename` / `dirname`、
  `DataFileApp` — grep で該当なし。`webapp.py` の `self._app`（tornado
  Application）や `test_webapp.py` の `svr._app`、`test_handler.py` /
  `test_main_handler.py` の `make_app()` / `self._app` はいずれも別物
  （WebServer 側や test helper 側の概念）で問題なし。
- design-review.md / TODO.md に残る `HandlerBase._app` の記述は、
  修正前の問題点としての記録であり、コード側の残存参照ではない。○

## 8. CONF_KEY の配置

`main_handler.py` に `CONF_KEY_TODO_DAYS` / `CONF_KEY_FILTER_STR` /
`CONF_KEY_SEARCH_N` が定義され、`handler.py` には `CONF_KEY_SEARCH_STR`
のみ残っている。`edit_handler.py` は `self.CONF_KEY_SEARCH_STR`
（`HandlerBase` 由来）を引き続き参照しており壊れていない。○

## 9. src/README.md

CLI の説明が `webapp` / `migrate` の 2 つのみに書き直されており、
`x_data1` への言及なし。実装と一致。○

## 結論

不具合は見つからなかった。判断が要る点は無し。

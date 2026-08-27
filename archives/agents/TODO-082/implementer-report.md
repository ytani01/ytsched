# TODO-082 implementer 報告

依頼書・`TODO.md`・`docs/design-review.md` の H・J・K を読んで着手した。
利用者決着済みの 3 点（`__init__.py` の import はやめる／`_app` `_req`
と `filename` `dirname` は消して `get_keys()` は残す／`x_data1` は消す）
はそのとおりに実施。挙動は変えていない（`x_data1` の削除のみ例外、
依頼書どおり）。

## 変更したファイル

- `src/ytsched/__init__.py` — `MainHandler` / `WebServer` /
  `SchedData*` の re-export を削除。`__all__` はメタデータ 3 つのみ
- `src/ytsched/__main__.py` — `from . import (...)` をメタデータだけに
  し、`SchedDataFile` は `.ytsched` から、`WebServer` は `.webapp` から
  直接 import。docstring を `main for ytsched package` に、`cli` の
  help を `YT scheduler` に修正。`x_data1` サブコマンドと
  `DataFileApp` クラス、余った `datetime` の import を削除。
  `--size_limit` の既定値を `WebServer.DEF_SIZE_LIMIT` に変更
  （値は `100 * 1024 * 1024` のまま、`webapp.py` で確認済み）
- `src/ytsched/handler.py` — `self._app = app` / `self._req = req` を
  削除（直前の `__log.debug` は残した）。`CONF_KEY_TODO_DAYS` /
  `CONF_KEY_FILTER_STR` / `CONF_KEY_SEARCH_N` を `main_handler.py` へ
  移し、`HandlerBase` には `CONF_KEY_SEARCH_STR` のみ残した
- `src/ytsched/main_handler.py` — 上記 3 定数を `CONF_KEY_LOAD_MONTHS`
  の隣に追加
- `src/ytsched/ytsched.py` — `SchedDataFile.__init__` のパス分解 3 行
  （`pl = ...` / `self.filename = ...` / `self.dirname = ...`）を削除
- `tests/test_handler.py` — `HandlerBase.CONF_KEY_TODO_DAYS` /
  `CONF_KEY_FILTER_STR` / `CONF_KEY_SEARCH_N` を使っていた箇所を、
  素の文字列（`"ToDo_Days"` など）に置き換え。`CONF_KEY_SEARCH_STR` を
  使う箇所（180 行あたりの別プロセスへ渡すコードを含む）は
  `HandlerBase` に残っているのでそのまま
- `tests/test_ytsched.py` — `test_date2path` から `sdf.dirname` /
  `sdf.filename` のアサート 2 行を削除
- `src/README.md` — `x_data1` の記述を削除し、CLI は `webapp` /
  `migrate` の 2 つと書き直した
- `pyproject.toml` — `[tool.ruff]` に `line-length = 78`、
  `[tool.ruff.lint]` に `extend-select = ["I"]` を追加
- `mise.toml` — `fmt` タスクから `--line-length 78` /
  `--extend-select I` を除去
- `docs/Developer.md` — 個別コマンドの例からも同オプションを除去

`migrate.py` の `CONF_OLD_FNAME` 付近のコメントは依頼どおり変更なし。

## 確かめたこと

- `mise run lint`（fmt・basedpyright・mypy）が通る
- `mise run test` で 475 件全部 pass
- ruff の設定移動の前後で `uv run ruff format --check` /
  `uv run ruff check` の結果が変わらないこと（both green）
- `uv run ytsched --help` / `webapp --help` / `migrate --help` を
  それぞれ実行し、`x_data1` が消えていること、help 文言が直っていること
  を確認
- `uv run python -c "...from ytsched.migrate import Migrator..."` で
  `'tornado' in sys.modules` が `False` になることを確認
- `uv run ytsched webapp --datadir <一時ディレクトリ>` で起動し、
  `curl` で `/ytsched/` が 200 を返すことを確認
- grep で、パッケージ経由の import が `__main__.py` 以外に無いこと、
  `HandlerBase._app`/`_req` や `SchedDataFile.filename`/`dirname` の
  残存参照が無いことを確認済み

## 判断が要る点

無し。利用者決着済みの 3 点以外、依頼書の範囲内で完結した。

## 気づいたが直さなかったもの

- `docs/design-review.md` の「手を付ける順」の表など、TODO-083 の
  範囲（`my.js` の分割）には触れていない

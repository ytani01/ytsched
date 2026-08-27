# TODO-082 implementer への依頼

`TODO.md` の TODO-082 と `docs/design-review.md` の H・J・K を読んでから
着手すること。**挙動は変えない**（`x_data1` の削除だけは例外で、利用者が
消すと決めた）。

判断が要る 3 点は、利用者が下のとおり決めた。**蒸し返さないこと。**

1. `__init__.py` の import はやめる（`migrate.py` のコメントはそのまま）
2. `_app` / `_req` と `filename` / `dirname` は消す。`get_keys()` は残す
3. `x_data1` は消す

## やること

### 1. `__init__.py` の re-export をやめる

- `src/ytsched/__init__.py` から `MainHandler` / `WebServer` /
  `SchedData` / `SchedDataEnt` / `SchedDataFile` の import を削除し、
  `__all__` をメタデータ 3 つ（`__author__` / `__prog_name__` /
  `__version__`）だけにする
- `src/ytsched/__main__.py` の `from . import (...)` を、
  メタデータだけ `from . import` にし、`SchedDataFile` は
  `from .ytsched import`、`WebServer` は `from .webapp import` にする
- パッケージ経由で import しているのは `__main__.py` だけ
  （tests・tools はすべてモジュール直指定）。念のため grep で確かめること
- `src/ytsched/migrate.py` の `CONF_OLD_FNAME` のコメント（227 行あたり、
  「`handler.py` を import すると、移行ツールが tornado に依存して
  しまうので」）は**そのまま**。これで実情と一致する

### 2. 使われていない属性を消す

- `src/ytsched/handler.py` の `self._app = app` / `self._req = req` を削除
  （直前の `__log.debug` は残してよい）
- `src/ytsched/ytsched.py` の `SchedDataFile.__init__` から
  `pl = self.pathname.split("/")` / `self.filename = pl.pop()` /
  `self.dirname = "/".join(pl)` の 3 行を削除
- `tests/test_ytsched.py` の `test_date2path` から `sdf.dirname` と
  `sdf.filename` のアサート 2 行を削除
- `SchedData.get_keys()` は**残す**。キャッシュの LRU 順を見る唯一の
  公開手段で、`test_get_sdf_lru_order` / `test_get_sdf_discard` が使う
- これで TODO.md の「`SchedDataFile.__init__` のパスの分解を `os.path` に
  する」も同時に解消する（分解ごと無くなる）。`os.path` を新たに使う
  必要は無い

### 3. `CONF_KEY_*` 3 つを `MainHandler` へ移す

- `CONF_KEY_TODO_DAYS` / `CONF_KEY_FILTER_STR` / `CONF_KEY_SEARCH_N` を
  `handler.py` の `HandlerBase` から `main_handler.py` の `MainHandler` へ
  移す（`CONF_KEY_LOAD_MONTHS` の隣。TODO-081 と同じ形）
- `CONF_KEY_SEARCH_STR` は `EditHandler.get()` でも読むので
  `HandlerBase` に**残す**
- `tests/test_handler.py` が `HandlerBase.CONF_KEY_TODO_DAYS` などを
  使っている。あれは `get_conf` / `set_conf` の読み書きそのものを見る
  テストで、キーが何かは本質ではない。**`MainHandler` を import させず**、
  `HandlerBase` に残る `CONF_KEY_SEARCH_STR` か、素の文字列
  （`"ToDo_Days"` など）に置き換えること。180 行あたりの、別プロセスへ
  渡すコード文字列も同じ

### 4. `__main__.py` の文字列と `x_data1`

- モジュールの docstring `"""main for musicbox package"""` を
  ytsched のものに直す（他のプロジェクトからの写し）
- `cli` グループの help `sample package` を、このコマンドの説明に直す
- `x_data1` サブコマンドと、そこからしか使っていない `DataFileApp`
  クラスを削除する。`datetime` の import が余るなら一緒に消す
- `src/README.md` の「CLI には …… `x_data1` というデバッグ用の
  サブコマンドが残っている（……）」の記述を、実情に合わせて直す

### 5. `webapp` の `--size_limit`

- `default=100 * 1024 * 1024` の直書きを `WebServer.DEF_SIZE_LIMIT` に
  する（help の文字列は既にそうなっている）。値が変わらないことを
  `WebServer` 側で確かめること

### 6. ruff の設定を `pyproject.toml` へ

- `--line-length 78` と `--extend-select I` を `mise.toml` の
  コマンド行から `pyproject.toml` へ移す
  （`[tool.ruff]` の `line-length`、`[tool.ruff.lint]` の `extend-select`）
- **規則は増やさない。** `select` を足したり `ignore` を変えたりしない。
  移すのは置き場所だけ
- `mise.toml` の `fmt` タスクから該当オプションを外す
- `docs/Developer.md` の 70〜71 行にある個別コマンドの例からも外す
- 移す前と後で `uv run ruff format --check` / `uv run ruff check` の
  結果が変わらないことを確かめること

## 確かめること

- `mise run lint`（fmt・typecheck）と `mise run test` が通る
- `uv run ytsched --help` / `uv run ytsched webapp --help` /
  `uv run ytsched migrate --help` が出る
- `ytsched migrate` が tornado を読み込まなくなったこと。たとえば
  `uv run python -c "import sys; from ytsched.migrate import Migrator; print('tornado' in sys.modules)"`
  が `False` になる
- アプリの起動を確かめるときは `--datadir` に一時ディレクトリを指定する

## 報告

`archives/agents/TODO-082/implementer-report.md` に、変更したファイルと
やったこと、判断が要る点を書くこと。返事は 5 行以内で。

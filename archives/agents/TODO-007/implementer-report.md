# TODO-007 implementer 報告

標準 logging のラッパー `my_logger.py` を廃止し、`~/work/tmr` と同じ
loguru ベースの `mylog.py` へ移行した。規約は
「クラス本体に `__log = getLogger(__qualname__)` を 1 つ置く」
「CLI の各サブコマンドの先頭で `loggerInit(debug=...)` を 1 回だけ呼ぶ」。

## 変更したファイル

### 新規作成

- `src/ytsched/mylog.py` — `~/work/tmr/src/tmr/mylog.py` を持ち込み。
  実装（`getLogger` / `setLevel` / `loggerInit` / `logLevel` / `_filter` /
  `exmsg`、`LOG_FMT`）は 1 文字も変えていない。先頭 docstring の
  サンプルコードだけ ytsched のクラス名に書き換えた
- `tests/test_mylog.py` — `~/work/tmr/tests/test_mylog.py` を持ち込み。
  import 先を `ytsched.mylog` に直し、ytsched のテストに合わせて
  著作権表示の 3 行を足しただけ。テストの中身は変えていない（8 件）

### 削除

- `src/ytsched/my_logger.py` — `git rm` した

### 変更

- `pyproject.toml` — `dependencies` に `loguru>=0.7.3`、
  `[[tool.mypy.overrides]]` の `module` に `loguru,loguru.*` を追加。
  `uv sync` 済み（loguru==0.7.3 が入った）
- `src/ytsched/ytsched.py` — 3 クラス（`SchedDataEnt` / `SchedDataFile` /
  `SchedData`）。詳細は下記
- `src/ytsched/handler.py` — `HandlerBase`
- `src/ytsched/main_handler.py` — `MainHandler`
- `src/ytsched/edit_handler.py` — `EditHandler`
- `src/ytsched/webapp.py` — `WebServer`
- `src/ytsched/__main__.py` — `DataFileApp` と 2 つのサブコマンド
- `tests/test_ytsched.py` — 1 か所（下記 3-2）

## 1. ファイルごとの内容

### `src/ytsched/ytsched.py`

- import を `from .mylog import getLogger` に
- `SchedDataEnt`
  - クラス変数 `_mylog = get_logger(__name__, False)` を
    `__log = getLogger(__qualname__)` に置き換え
  - `__init__` の `debug: bool = False` 引数と `self._dbg` を削除
  - `self.__class__._mylog = get_logger(...)` の**上書きを削除**
    （TODO-007 の 3 つめのチェック項目。インスタンス 1 個の
    `debug=True` がクラス全体のロガーを差し替えていた）
  - `cls._mylog` → `cls.__log`（`new_id()` / `type_is_todo()`）
- `SchedDataFile`
  - クラス本体に `__log = getLogger(__qualname__)` を新設
    （元は `__init__` 内で `self._mylog = get_logger(...)` していた）
  - `__init__` の `debug` 引数と `self._dbg` を削除
  - `load()` 内の `SchedDataEnt(..., debug=self._dbg)` から `debug=` を落とした
- `SchedData`
  - クラス変数 `_mylog` → `__log = getLogger(__qualname__)`。
    `__init__` 内での再代入も削除
  - `__init__` の `debug` 引数と `self._dbg` を削除
  - `get_sdf()` 内の `SchedDataFile(date, self._topdir, debug=self._dbg)`
    から `debug=` を落とした
- ログ呼び出しを全て f-string に。コメントアウトされている行も同じ書式に
  直した（`# self._mylog.debug('d=%s', d)` →
  `# self.__log.debug(f"d={d}")` など、計 15 行）

### `src/ytsched/handler.py`

- `HandlerBase` のクラス本体に `__log` を新設
- `self._dbg = app.settings.get("debug")` と
  `self._mylog.debug("debug=%s", self._dbg)` の 2 行を削除
- `%a` 書式は f-string の `!a` 変換に置き換えた
  （`self._mylog.warning("%a: no tab .. ignored", line)` →
  `self.__log.warning(f"{line!a}: no tab .. ignored")`）

### `src/ytsched/main_handler.py`

- `from .mylog import getLogger` を追加、`MainHandler` のクラス本体に
  `__log` を置いた（名前マングリングされるので、サブクラスにも必要）
- `cmd_add()` の `SchedDataEnt(..., debug=self._dbg)` から `debug=` を削除
- `re.error` の warning 4 か所（`"%s:%s:%s:%s"` 形式）を f-string 1 本に

### `src/ytsched/edit_handler.py`

- 同上。`SchedDataEnt("", date, debug=self._dbg)` から `debug=` を削除

### `src/ytsched/webapp.py`

- `WebServer` のクラス本体に `__log`。`self._log` は廃止
- `self._dbg = debug` は**残した**（tornado の `autoreload` と
  `Application(debug=...)` に使うため。指示どおり）
- `SchedData(self._datadir, debug=self._dbg)` の `debug=` だけ落とした

### `src/ytsched/__main__.py`

- import を `from .mylog import getLogger, loggerInit` に
- モジュール先頭に `_log = getLogger("main")`
- `DataFileApp` はクラス本体に `__log`。`debug` 引数と `self._dbg` を廃止し、
  `SchedDataFile(..., debug=self._dbg)` からも `debug=` を落とした
- `x_data1` / `webapp` の各サブコマンドの先頭で `loggerInit(debug=debug)` を
  1 回呼ぶ。関数内の `log` は `_log` に。`--debug` オプションは残した

## 2. 単独で決めた判断

1. **`__log` はクラス docstring の直後、定数より前に置いた。**
   tmr の `BaseTimer` / `ProgressBar` がどちらもそうしていたので合わせた。
   ytsched の元の `_mylog` は定数の後ろにあったが、tmr に揃える方を優先した。
   8 クラス全てで位置を統一してある

2. **`mylog.py` の著作権表示は `(c) 2026`。** ytsched の src 側は
   2020/2021 だが、それらは 2021 年に書かれたファイル。2026 年に作った
   ファイル（`tests/helpers.py`、`tests/test_*.py`）は全て 2026 なので、
   新規作成の `mylog.py` もそれに合わせた

3. **docstring のサンプルは 3 クラスにした。**
   `SchedDataEnt`（単独のクラス）と `HandlerBase` → `MainHandler`
   （継承。サブクラスが自分の `__log` を持つ例）。tmr は `Base` / `Child`
   の 2 つだったが、ytsched では継承の例が要点なので実物の名前を使った

4. **`tests/helpers.py:53` の `debug=False` は残した。**
   依頼では「消した `debug=` 引数を渡している箇所」として挙がっていたが、
   実物を見ると `tornado.web.Application(...)` に渡す tornado 自身の設定で、
   ytsched が消した `debug=` 引数ではなかった。`webapp.py` は今も
   `Application(..., debug=self._dbg)` を渡しており、`helpers.py` は
   それを写したもの。`test_webapp.py` の `settings["debug"]` の検査とも
   対応するので、消すと `webapp.py` と食い違う。
   `grep -rn "debug" tests/` で洗った他の箇所も、全て tornado 側の設定か
   `WebServer(..., debug=True)` で、残すよう指示されたものだった

5. **`tests/test_ytsched.py` の `sd._mylog = mock.Mock()` は
   `mock.patch.object(SchedData, "_SchedData__log")` に直した。**
   `self.__log` は `_SchedData__log` にマングリングされる。
   最初は `sd._SchedData__log = mock.Mock()` と書いたが、mypy が
   `"SchedData" has no attribute "_SchedData__log"` を 2 件出したので
   `mock.patch.object` に変えた（文字列で名前を渡すので mypy が通る）。
   マングリングの件はコメント 1 行で補ってある

6. **`ruff format --line-length 78` をかけた。** `mise run lint` が
   実行しているのと同じコマンド。差分は自分が書いた行だけに出ており
   （4 ファイル、いずれも f-string の折り返しが不要になった箇所）、
   他の箇所には影響していないことを `--diff` で確認してから実行した

## 3. 自分で確かめたこと

### 3-1. テスト・型チェック・lint

| 項目 | 着手前 | 着手後 |
| --- | --- | --- |
| `uv run pytest` | 161 passed | **169 passed**（`test_mylog.py` の 8 件が増えた） |
| `uv run mypy src tests` | **2 errors**（`__class__` is not defined。ytsched.py:357、__main__.py:22） | **Success: no issues found** |
| `uv run basedpyright src tests` | 0 errors | 0 errors |
| `uv run ruff check src tests` | **87 errors** | **86 errors** |
| `uv run ruff format --check` | 全て整形済み（下記） | 14 files already formatted |

ruff の内訳（着手前 → 着手後）:

| 規則 | 前 | 後 |
| --- | --- | --- |
| UP031 printf-string-formatting | 35 | **34** |
| DTZ011 call-date-today | 13 | 13 |
| FLY002 static-join-to-f-string | 13 | 13 |
| D419 empty-docstring | 10 | 10 |
| RUF012 mutable-class-default | 5 | 5 |
| EXE001 shebang-not-executable | 4 | 4 |
| SIM102 collapsible-if | 2 | 2 |
| C408 unnecessary-collection-call | 1 | 1 |
| DTZ005 call-datetime-now-without-tzinfo | 1 | 1 |
| PERF402 manual-list-copy | 1 | 1 |
| PLC0206 dict-index-missing-items | 1 | 1 |
| SIM118 in-dict-keys | 1 | 1 |
| 合計 | 87 | 86 |

`ruff format --check` は着手前も通っていた（自分の変更を `git stash` して
確かめた）。着手後も 14 files already formatted。

**増えた規則は無い。** UP031 が 1 件減ったのは、削除した `my_logger.py` の
`raise ValueError("invalid `dbg` value: %s" % (dbg))` が消えたため。
TODO-015 の範囲であるログ以外の `"%s" % (...)` 書式には手を付けていない。

### 3-2. mypy の 2 件について

TODO-006 時点で残っていた `Name "__class__" is not defined` 2 件は、
どちらも `get_logger(__class__.__name__, ...)` の行だったので、
今回の書き換えで消えた。指示どおりの結果になっている。

### 3-3. 実際に動かした

`--datadir` には全て一時ディレクトリを指定した
（`~/ytsched/data` の実データには触れていない）。

- `uv run ytsched --help` / `uv run ytsched webapp --help` — 表示は従来どおり。
  `-d, --debug  debug flag` も残っている
- `webapp` を `--debug` **無し**で起動 → ログは
  `08/20 09:48:49 ℹ️ INFO webapp.py:126 main()> start server: run forever ..`
  の 1 行だけ。`GET /ytsched/` は 200
- `webapp` を `--debug` **付き**で起動 → 329 行の DEBUG が出た。
  内訳は ytsched.py 276 / handler.py 26 / main_handler.py 15 /
  edit_handler.py 6 / webapp.py 5。
  `🐞 DEBUG ファイル名:行 関数()> メッセージ` の形式で、
  `LOG_FMT` どおりに出ている
- `POST cmd=add` で予定を 1 件追加 → 200、
  データファイルがタブ区切りで正しく書かれた
  （`<uuid>\t2021/03/01\t09:00-:\t予定\tテスト\t\t`）。
  WARNING / ERROR は 0 件
- `uv run ytsched x-data1 2021 3 1 --datadir <tmp>` を `-d` 有無の両方で実行。
  無しでは INFO 1 行、付きでは `__main__.py` / `ytsched.py` の DEBUG が出た
- 起動したサーバは全て kill した。`pgrep` で残っていないことを確認済み

## 4. 気づいたが直さずに残したもの

- **`"%s" % (...)` 書式（UP031、34 件）** — TODO-015 の範囲。
  ログ以外は指示どおり触っていない。`webapp.py:87` の
  `print("%s %s by %s" % (...))`、`handler.py:104` の
  `f.writelines("%s\t%s\n" % ...)`、`__main__.py` の click の help 文字列などが残る
- **`D419` 空 docstring（10 件）** — `""" """` のまま。TODO-015 の範囲。
  ログ行を消したことで中身が `pass` 同然になった関数は無い
- **`__main__.py` の docstring が `main for musicbox package`** —
  別プロジェクトからの写し間違いが残っている。TODO-009（README）や
  TODO-010（CLAUDE.md）の周辺だが、どの項目の範囲とも書かれていないので
  触っていない
- **`tests/test_mylog.py` の `test_default_level_is_info(monkeypatch)` が
  `monkeypatch` を使っていない** — tmr の実物がそうなっている。
  「実装は変えない」の指示に従いそのままにした。ruff の現行設定では
  指摘されない（ARG 系は有効になっていない）
- **`loggerInit()` を呼ばずに使ったときの挙動** — loguru の既定 handler
  （stderr、水準 DEBUG）がそのまま効く。テスト（pytest）では
  `loggerInit()` を呼んでいないので、`test_mylog.py` 以外のテストでは
  DEBUG が pytest のキャプチャに入る。169 件は全て通っているが、
  仕様として意図どおりかは main の判断が要るかもしれない
  （tmr も同じ作りなので、揃えるという意味では合っている）

## 5. うまくいかなかったところ

特に無し。1 度だけ、`tests/test_ytsched.py` を
`sd._SchedData__log = mock.Mock()` と直したときに mypy が 2 件出たので、
`mock.patch.object` に変えた（上記 2-5）。

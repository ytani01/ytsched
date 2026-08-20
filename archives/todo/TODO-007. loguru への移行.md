# TODO-007. loguru への移行

見込み: main = Opus 5 / effort high、担当 = implementer + verifier
実施: main = Opus 5 / effort high、担当 = implementer + verifier

（立てたときの見込みは `main = Sonnet 5 / effort medium` だったが、
下調べで書き換えが 6 ファイル・約 123 箇所＋公開引数の変更に及ぶと
分かったので、着手時に書き直した。）

分担の理由と各担当の報告は
[archives/agents/TODO-007/](../agents/TODO-007/README.md) にある。

## きっかけ

2021 年に書いた `my_logger.py`（標準 `logging` のラッパー）を使い続けて
いた。`tmr` は既に loguru ベースの `mylog.py` に移っており、
「クラス本体に `__log = getLogger(__qualname__)` を 1 つ置く」規約で
揃っている。

`SchedDataEnt.__init__` には、インスタンスを 1 つ `debug=True` で作ると
`self.__class__._mylog` の代入でクラス全体のロガーが差し替わる問題が
あった（TODO-005 から回した）。TODO-006 で残った mypy の 2 件
（`Name "__class__" is not defined`）も `get_logger(__class__.__name__, ...)`
の行だった。

## 決めたこと

着手前に利用者と確認した。

- **各クラスの `debug` 引数は廃止する**（`SchedDataEnt` / `SchedDataFile` /
  `SchedData` / `HandlerBase` / `DataFileApp`）。ログの水準は CLI 先頭の
  `loggerInit()` と `getLogger()` だけで決める。`_dbg` はログ以外に
  使われていなかった。`WebServer` の `debug` は tornado の `autoreload` と
  `Application(debug=...)` に要るので**残す**
- **ログ呼び出しの書式は f-string**（`tmr` に揃える）。
  `debug("date=%s", date)` → `debug(f"date={date}")`

## やったこと

- `src/ytsched/mylog.py` を新規作成。`~/work/tmr/src/tmr/mylog.py` の実装
  （`getLogger` / `setLevel` / `loggerInit` / `logLevel` / `_filter` /
  `exmsg`、`LOG_FMT`）をそのまま持ち込み、先頭 docstring のサンプルだけ
  ytsched の実物のクラス名に書き直した
- `src/ytsched/my_logger.py` を削除
- `pyproject.toml` に `loguru>=0.7.3` と、mypy の
  `ignore_missing_imports` 対象への `loguru,loguru.*` を追加
- 8 クラス（`SchedDataEnt` / `SchedDataFile` / `SchedData` /
  `HandlerBase` / `MainHandler` / `EditHandler` / `WebServer` /
  `DataFileApp`）のクラス本体に `__log = getLogger(__qualname__)` を置いた。
  `__log` は名前マングリングされるので、`HandlerBase` を継承する
  `MainHandler` / `EditHandler` にもそれぞれ要る
- `__main__.py` はモジュール先頭に `_log = getLogger("main")` を置き、
  `x_data1` / `webapp` の各サブコマンドの先頭で `loggerInit(debug=debug)` を
  1 回呼ぶようにした。`--debug` オプションはそのまま
- ログ呼び出し約 123 箇所を f-string に直した。コメントアウトされている
  ログ行（15 行）も同じ書式に揃えた。`%a` は f-string の `!a` 変換にした
- `tests/test_mylog.py` を `~/work/tmr/tests/test_mylog.py` から持ち込んだ
  （8 件）。`tests/test_ytsched.py` の `sd._mylog = mock.Mock()` は
  `mock.patch.object(SchedData, "_SchedData__log")` にした
  （マングリング後の名前を直に書くと mypy が通らない）

### `loggerInit()` を呼ばないときの挙動（そのままにした）

`loggerInit()` を呼ばずに使うと loguru 既定の handler（stderr、水準
DEBUG）が効く。pytest では `loggerInit()` を呼んでいないので、
以前（`my_logger.py` の既定は INFO）とテスト時の挙動が変わっている。
`tmr` も同じ作りで、揃えるのがこの項目の趣旨なので**そのままにした**
（テストが失敗したときに DEBUG が見えるのは手がかりにもなる）。

## テスト

verifier が依頼の 9 項目をすべて自分で実行し直した
（`archives/agents/TODO-007/verifier-report.md`）。実装者の報告の数値・
挙動はすべて再現でき、不具合は見つかっていない。

| 確認 | 結果 |
| --- | --- |
| `uv run pytest` | 161 passed → **169 passed**（`test_mylog.py` の 8 件が増えた） |
| `uv run mypy src tests` | 2 件 → **0**（`__class__` の 2 件が消えた。TODO-006 の見込みどおり） |
| `uv run basedpyright src tests` | 0 errors のまま |
| `uv run ruff check src tests` | 87 件 → **86 件**。増えた規則は無い（減った 1 件は消した `my_logger.py` の `UP031`）。残りは TODO-015 / TODO-008 の範囲 |
| `uv run ruff format --line-length 78 --check src tests` | 14 files already formatted |
| `my_logger` / `get_logger` / `_mylog` の参照 | `src` `tests` とも 0 件 |
| webapp の起動（`--debug` 無し） | INFO 1 行だけ。`GET /ytsched/` は 200 |
| webapp の起動（`--debug` 付き） | 5 モジュールすべてから DEBUG が出る。**行番号・関数名を実物と抜き取り照合し、`mylog.py` ではなく呼び出し元を指している**ことを確認（loguru の `depth` の要点） |
| `POST cmd=add` | 200。データファイルはタブ区切りで従来どおり。WARNING / ERROR なし |
| `x-data1`（`-d` 有無） | 無しは INFO 1 行、付きは DEBUG が出る |

`--datadir` には一時ディレクトリを使い、`~/ytsched/data` の実データには
触れていない。

## 気づいたが直さなかったもの

- **`ruff format --check` を素で実行すると 9 files would be reformatted**
  になる。`pyproject.toml` に `[tool.ruff]` を持たず、行長 78 は
  `mise.toml` の lint タスクが `--line-length 78` で渡す流儀のため
  （TODO-004 で決めたこと）。`--line-length 78` を付ければ通る
- **`__main__.py` の docstring が `main for musicbox package`** —
  別プロジェクトからの写し間違いが残っている。どの項目の範囲とも
  書かれていないので触っていない
- `UP031`（34 件）と `D419`（10 件）は TODO-015 の範囲なので触っていない

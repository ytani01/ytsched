# TODO-100. `os.path` を `pathlib` へ移す

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort medium | implementer + verifier |
| 実施 | Opus 5 / effort medium | implementer + verifier + wording |
| 消費 | output 18,431 / cache_creation 294,770 / 概算 $5.2 |
|      | implementer 49% + main 45% + verifier 4% + wording 2%（料金の割合） |

## きっかけ

TODO-095 で ruff の規則を見直したときに出てきたもの。`PTH` を有効にすると
`src` と `tests` で 56 件の指摘が出るため、TODO-095 では足さずに別の項目に
した。書き換えが済んでいない状態で有効にすると `lint` が通らなくなるので、
**書き換えと `extend-select` への追加を同じ項目でやる**ことにしていた。

## 決めたこと

着手時に利用者と決めた。**パスを持つ属性の型そのものを `Path` にする。**

`Path(self.pathname).open(...)` のように呼び出し側で包むだけでも `PTH` は
通るが、`str` と `Path` が混ざったまま残る。属性の型を変えるほうを選んだ。

- `SchedDataFile.topdir` / `pathname`
- `ConfFile.pathname`
- `WebServer._webroot` / `_datadir`（`DEF_WEBROOT` / `DEF_WORKDIR` /
  `DEF_DATADIR` も）

CLI（`__main__.py`）から来る値は `str` なので、引数は `str | Path` で受けて
内部で `Path` に正規化する。

## やったこと

- `pyproject.toml` の `extend-select` に `"PTH"` を足した
  （`["I", "B", "SIM", "UP", "PTH"]`）
- 上の属性を `Path` にし、`os.path.*` / `open()` / `os.stat()` /
  `os.makedirs()` を `Path` のメソッドに置き換えた（`src`・`tests` の 9 ファイル）
- `SchedDataFile.PATH_FORMAT` / `TODO_PATH_FORMAT`（`%` 書式の 2 定数）は
  削除し、`date2path()` の中で `/` 演算子で組み立てるようにした。
  **できあがるパスは今までと同じ**
- `.bak` の作り方を `pathname + BACKUP_EXT` から
  `pathname.with_name(pathname.name + BACKUP_EXT)` に変えた
  （`Path` に `+` が無いため）。名前は今までと同じ
- 型が変わった属性と比べているテストの比較を `Path` 同士に直した
- docstring とコメントの ``os.stat()`` という表記を ``Path.stat()`` に
  揃えた（main）

`os.path.abspath` の置き換え先は、ruff が勧める `.resolve()` ではなく
`.absolute()` にした。`os.path.abspath` はシンボリックリンクを解決しないが
`.resolve()` は解決するので、挙動が変わってしまう。

`AppInfo.datadir`（`handler.py`）は `str` のまま残した。`PTH` の対象では
なく、パス操作にも使っていない。`WebServer` から渡すときだけ
`str(self._datadir)` にしている。

## `expanduser()` の差（対応しない）

verifier が、`os.path.expanduser()` と `Path.expanduser()` で結果が違う
入力を 2 つ見つけた。**どちらも今のコードでは到達しないので、対応しない。**

| 入力 | `os.path.expanduser()` | `Path.expanduser()` |
|------|------------------------|---------------------|
| `""` | `""` | `"."` |
| `~存在しないユーザ/x` | そのまま返す | `RuntimeError` |

`DEF_TOP_DIR` / `DEF_DATADIR` にも CLI の既定値にも空文字は無く、存在しない
ログイン名を渡す経路も無い。`~`・`~/foo`・絶対パスは一致することを
確認済み。

## テスト

- `uv run ruff check .` — `All checks passed!`（`PTH` 込み）
- `uv run mypy src` — 0 件、`uv run basedpyright` — 0 件
- `uv run pytest tests` — 481 件すべて通過（`test_browser.py` を含む）
- `date2path()` の新旧実装を実際に呼び比べ、同じ日付から同じパスが
  出ることを確認（年・月のディレクトリ、桁揃え、拡張子、ToDo ファイル）
- `.bak` の名前が新旧で一致することを確認（TODO-077 の箇所）
- `ytsched webapp --datadir <一時ディレクトリ>` を起動して `curl` が 200、
  `ytsched migrate --datadir <一時ディレクトリ> --dry-run` が正常終了
  （CLI から `str` を渡す経路の確認）

分担は [archives/agents/TODO-100/](../agents/TODO-100/README.md) にある。

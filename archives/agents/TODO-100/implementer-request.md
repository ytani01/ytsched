# TODO-100 implementer への依頼

`os.path` を `pathlib.Path` へ移し、ruff の `PTH` を有効にする。

## 方針（利用者が決めたこと）

**パスを持つ属性の型そのものを `pathlib.Path` に変える。**
`Path(self.pathname)` のように呼び出し側で包んで済ませない。対象:

- `SchedDataFile.pathname` / `SchedDataFile.topdir`
- `ConfFile.pathname`
- `WebApp._datadir` / `WebApp._webroot`
- `Migrator` は既に `Path`（`os.path.expanduser` だけ残っている）

引数の型ヒントは `str | pathlib.Path` を受けて内部で `Path` に正規化するか、
`Path` に統一するか、実装側で素直なほうを選んでよい。ただし CLI
（`__main__.py`）から来る値は `str` なので、そこで壊れないこと。

## やること

- [ ] `os.path.*` / `open()` / `os.stat()` / `os.makedirs()` を
      `pathlib.Path` のメソッドに置き換える（src・tests・tools すべて）
- [ ] `pyproject.toml` の `[tool.ruff.lint] extend-select` に `"PTH"` を足す
- [ ] `uv run ruff check .` が通ること

## 注意

- `SchedDataFile.PATH_FORMAT` / `TODO_PATH_FORMAT` は `%` で組み立てている。
  `Path` の `/` 演算子に書き換えるか、`%` の結果を `Path` に包むか判断する。
  **ファイル名の作られ方（`YYYY/MM/YYYY-MM-DD.jsonl` 等）は変えないこと。**
- `self.pathname + self.BACKUP_EXT`（`.bak`）は `Path` では
  `p.with_suffix(p.suffix + BACKUP_EXT)` ではなく
  `p.with_name(p.name + BACKUP_EXT)` 相当になる。**現在と同じ名前になること**
  （`2026-08-28.jsonl.bak`）。TODO-077 で `.bak` の扱いを直しているので壊さない
- `os.path.expanduser` → `Path(...).expanduser()`。**`~` の展開の挙動を
  変えないこと**（TODO-034 で整理した箇所）
- ログや例外メッセージに埋まるパスの見え方は、`Path` の `__str__` で
  今までと同じになる。`f"{path}"` のままでよい
- 外から見える属性の型が変わるので、**テストの比較も合わせて直す**
- 挙動は変えない。データディレクトリの構成・ファイル名は一切変えない
- `mise run upgradeproject` は走らせない。
  `uv run ruff format` / `ruff check` / `basedpyright` / `mypy` / `pytest` は可
- 起動確認をするなら `--datadir` に一時ディレクトリを指定する

## 報告

`archives/agents/TODO-100/implementer-report.md` に書く。
返事は 5 行以内（終わったか・報告ファイルのパス・判断が要る点）。

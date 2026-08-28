# TODO-100 verifier への依頼

implementer が `os.path` を `pathlib.Path` へ移した。挙動が変わっていないかを
確かめる。**コードは直さない。** 見つけたことは報告するだけ。

- 依頼書: `archives/agents/TODO-100/implementer-request.md`
- 実装の報告: `archives/agents/TODO-100/implementer-report.md`
- 変更範囲: `git diff`（`pyproject.toml`, `src/ytsched/*.py`, `tests/*.py`）

## 特に見てほしいところ

1. **データファイルのパスが今までと同じか。**
   `SchedDataFile.PATH_FORMAT` / `TODO_PATH_FORMAT`（`%` 書式）が削除され、
   `/` 演算子での組み立てに変わっている。`git show HEAD:src/ytsched/ytsched.py`
   の旧実装と突き合わせて、**同じ日付から同じパスが出ることを実際に確かめる**
   （日付の桁揃え、年・月のディレクトリ、拡張子、TODO ファイル）
2. **`.bak` の名前が今までと同じか。** 旧: `pathname + BACKUP_EXT`、
   新: `with_name(name + BACKUP_EXT)`。実際に save を 2 回走らせて
   `.bak` ができるファイル名を見る（TODO-077 の箇所）
3. **`~` の展開。** `os.path.expanduser` → `Path(...).expanduser()` で
   挙動が変わっていないか（`~` 単体、`~/…`、`~` を含まないパス、空文字）
4. **`os.path.abspath` → `.absolute()` の選択が妥当か。**
   implementer は「`.resolve()` はシンボリックリンクを解決してしまうので
   `.absolute()` にした」と書いている。webroot の解決がこれで正しく動くか
5. **`str` を渡す経路が壊れていないか。** CLI（`__main__.py`）から来る値は
   `str`。`ytsched webapp` / `ytsched migrate` などを
   **`--datadir` に一時ディレクトリを指定して実際に起動**し、動くか見る
6. `uv run ruff check .` / `basedpyright` / `mypy` / `pytest` を走らせて
   通ることを確認する（`mise run upgradeproject` は走らせない）
7. 型が `Path` に変わった属性を、まだ `str` として扱っている箇所が
   残っていないか（文字列連結、`+`、`.startswith`、`%` 書式、`os.path` の
   残骸）を grep で見る

## 報告

`archives/agents/TODO-100/verifier-report.md` に書く。
返事は 5 行以内（終わったか・報告ファイルのパス・判断が要る点）。

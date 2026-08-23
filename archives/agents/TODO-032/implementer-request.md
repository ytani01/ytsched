# TODO-032 implementer への依頼

`Conf.cgi`（タブ区切り）を `conf.json`（JSON）にする。`TODO.md` の
TODO-032 の節に、決まっていることが書いてある（**先に読むこと**）。

範囲は形式の変更だけ。値は文字列のまま持ち、`main_handler.py` の
`get_conf_arg()` / `convert_value()` には手を入れない。

## 1. `src/ytsched/handler.py`

- `CONF_FNAME` を `"conf.json"` へ。
- `load_conf()` を `json` の読み込みにする。自前の行分解は消す。
  - ファイルが無ければ今までどおり空の dict。
  - **JSON として壊れていても例外にしない。** 警告を 1 行出して空の
    dict を返す（不正な正規表現の扱い（TODO-012）、不正な引数の扱い
    （TODO-027）と揃える。設定ファイルが壊れて画面が出ないのは困る）。
  - トップレベルが dict でない、値が文字列でないキーがある場合も同じ
    考え方で、警告を出して読み飛ばす（`dict[str, str]` を保つ）。
- `save_conf()` を `json.dump()` にする。`ensure_ascii=False`、
  `indent=2`、末尾に改行。人が読める形にはするが、手で編集する
  ファイルではない（`src/README.md` の記述のとおり）。
- docstring の `Conf.cgi` を `conf.json` に直す。

## 2. `src/ytsched/migrate.py`

旧 `Conf.cgi` → `conf.json` の変換を `Migrator` に足す。

- **`handler.py` を import しない**（tornado への依存が移行ツールに
  入る）。ファイル名は `Migrator` 側にクラス変数で持つ。
- 読み方は、この移行ツールの他の変換と揃える。バイト列で読み、
  `SchedDataFile.split_lines()` で行に分け、行末の `\r` を落とし、
  `decode_line()` で 1 行ずつデコードする（旧データが euc_jp の
  こともある）。空行は飛ばす。タブの無い行は警告して飛ばす。値は
  `split("\t", maxsplit=1)` の右側（旧 `load_conf()` と同じ）。
- `Conf.cgi` が無ければ何もしない。`conf.json` が既にあれば、警告を
  出して飛ばす（`migrate_file()` と同じ扱い）。`--dry-run` では書かない。
- **元の `Conf.cgi` は消さない**（他のファイルと揃える）。
- `MigrateStat` に `conf_files` と `skipped_conf_files`（どちらも int）を
  足し、`main()` の出力へ 1 行足す。書式は既存の行に合わせること:

  ```
  設定ファイル    : 変換 1, 飛ばした 0
  ```

## 3. テスト

- `tests/test_handler.py` — タブ区切り前提のテストを JSON 用に書き直す。
  タブ特有のもの（タブの無い行、値にタブ）は JSON では意味が変わるので、
  **壊れた JSON**、**トップレベルが dict でない**、**値が文字列でない**
  に置き換える。値に改行やタブを含む往復（round trip）のテストは残す。
- `tests/test_main_handler.py` / `tests/test_web.py` — 設定ファイルを
  直に読み書きしているところ（`CONF_FNAME`、`Conf.cgi` のパス、
  `ToDo_Days\t...` のような組み立て）を JSON に直す。**見ている中身
  （どの値が保存され、どの値が残らないか）は変えないこと。**
- `tests/test_migrate.py` — 設定の移行を足す。正常、euc_jp の値、
  `conf.json` が既にある、`Conf.cgi` が無い、`--dry-run`。
  `tests/data/old_format/` には `Conf.cgi` を置かず（合成データは予定の
  壊れ方を再現するためのもの）、テストの中で一時ディレクトリへ書く。

## 4. 文書

- `src/README.md` — `Conf.cgi` を `conf.json` に。形式が JSON になった
  ことを書く。Mermaid の図の中の記述（`load_conf` の Note、`set_conf()`
  の行）も直す。
- `docs/data-format.md` — 30 行目あたりのツリー、179 行目あたり、
  383 行目あたりの TOML を見送った理由の参照。この文書は**予定データの
  形式**が対象で設定は対象外なので、記述を増やさず、名前と「移行ツールが
  設定も変換する」ことだけに留める。
- `tests/README.md` — 17 行目。
- `TODO.md` と `archives/` は main が触る。**手を出さないこと。**

## 走らせるもの

`uv run ruff format` / `ruff check` / `basedpyright` / `mypy` / `pytest`
（または `mise run fmt` / `typecheck` / `lint` / `test`）。
**`mise run upgradeproject` は走らせない。**

## 報告

`archives/agents/TODO-032/implementer-report.md` に書く。返事は
「終わったか・報告のパス・判断が要る点」の 5 行以内。

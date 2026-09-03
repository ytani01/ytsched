# TODO-170 implementer 報告

## 変更したファイル

- `src/ytsched/fix_id.py`（新規） — `IdFixer` / `FixIdStat`。
  `{年}/{月}/{日}.jsonl` と `ToDo.jsonl` を走査し、`sde_id` が
  UUID（小文字ハイフン付き 36 文字、正規表現で判定）でない行だけ
  `SchedDataEnt.new_id()` で差し替える。他のキーは `json.loads` →
  `sde_id` だけ代入 → `json.dumps(ensure_ascii=False)` で戻すので、
  値・並び順とも変わらない。JSON として読めない行・`sde_id` キーが
  無い行・`sde_id` が文字列でない行はそのまま書き戻して数える。
  書き戻しは同じディレクトリの一時ファイル（`tempfile.mkstemp`）→
  `Path.replace()`。変更が無いファイルは一切書かない。`--dry-run` は
  1 バイトも書かない
- `src/ytsched/__main__.py` — サブコマンド `fix-id` を追加
  （`--datadir` / `--dry-run` / `click_common_opts`。`migrate` を手本に
  した）
- `tests/test_fix_id.py`（新規） — 13 件。非 UUID→UUID の置換、
  UUID 行は不変、他キーの値・並び順不変、重複 ID が別々の UUID に
  なる、読めない行の保持、`trash.jsonl` 不変、`--dry-run` で無変更、
  変更なしファイルの mtime 不変、書き換え後を `SchedDataFile` が
  読める、CLI（`CliRunner`）の dry-run と本番実行

## 自分で確かめたこと

- `uv run ruff format` / `ruff check` / `basedpyright` / `mypy`
  （`mise run typecheck`・`mise run lint` 経由）はすべて通った
- `uv run pytest -q` は全 633 件パス（fix_id 分含む）
- 一時ディレクトリ（`~/ytsched/data` は触っていない）に
  非 UUID・UUID・`ToDo.jsonl`・`trash.jsonl` を用意し、
  `ytsched fix-id --datadir <tmp> --dry-run` → 件数のみで無変更、
  続けて本番実行 → 非 UUID だけ UUID に変わり、`trash.jsonl` は
  無変更であることを実際に確認した

## 判断したこと

- クラス名は依頼書に明示が無かったため `IdFixer`（`HolidayRegistrar`・
  `Migrator` に倣った命名）とした
- 一時ファイルの作成に `tempfile.mkstemp()` を使った
  （`migrate.py`・`holiday.py` に前例が無かったため、標準ライブラリの
  素直な方法を選んだ）

## 残したもの（範囲外）

- `docs/`・`README.md` の更新は writer の担当なので触っていない
- 実データへの適用は利用者が行う（依頼書のとおり、実データには
  触っていない）

# GEMINI.md（ytsched）

`~/.gemini/GEMINI.md`（ユーザー全体の指示・プロフェッショナル行動規範）が前提。

## プロジェクト概要

個人用スケジュール帳（Web アプリ）。Python 3.14 / uv / pytest / Tornado / JSON Lines。単一ユーザ専用、認証はリバースプロキシに任せる前提（`README.md` 参照）。

- データディレクトリ（既定 `~/ytsched/data`）の実データは保護する。
- データの保存形式は JSON Lines（仕様は `docs/data-format.md`）。

## コードを触る前に読むこと

構成・データモデル・Web の構成・開発コマンドは、以下に分けてある。**コードを触る前に必ず確認すること。**

- ソースコードの構成、クラス構造（`SchedDataEnt` / `SchedDataFile` / `SchedData`、`HandlerBase` / `MainHandler` / `EditHandler` の関係、フィルタ・検索文字列の扱い）は `src/README.md`
- 技術スタック、開発環境、`mise` のタスクと個別コマンド、テストの走らせ方は `docs/Developer.md`
- 各テストファイルの役割、`helpers.py` の役割、ゴールデンマスターテストの位置づけは `tests/README.md`
- データの保存形式（JSON Lines、壊れた行の扱いなど）は `docs/data-format.md`

## ログ規約

`mylog.py` のラッパを使う。標準の `logging` は使わない（loguru ベース）。クラス本体に `__log = getLogger(__qualname__)` を 1 つ置く。サンプルは `docs/Developer.md` を参照。

## タスク管理と進め方

1. **着手前の項目立案**: コード修正を伴う作業は、着手前に `TODO.md` に項目を追加し、承認を得てから着手する。
2. **完了時の記録**: 完了時は `archives/todo/TODO-NNN. タイトル.md` に結果（見込み・実施・トークン消費・担当割合）を記録する。
3. **コミットの分割**:
   - 項目立案時: `docs(todo): …の件を TODO-NNN として立てる`
   - 完了時: `feat(...): …（TODO-NNN）` / `fix(...): …（TODO-NNN）`

## 開発・検証環境の不変条件

- **アプリの起動・検証時は、`--datadir` に必ず一時ディレクトリ（`tmp_path` 等）を指定する。** `~/ytsched/data` の実データを汚さないため。
- **`mise run upgradeproject` はエージェント側で実行しない。** 依存関係を意図せず更新してテストの再現性を損なわないため。
- **検証コマンド**: `uv run pytest`, `uv run ruff check`, `uv run ruff format`, `uv run basedpyright`, `uv run mypy` または `mise run test` / `lint` を使用する。
- **シェル操作**: `cp`, `mv`, `rm` は `-i` エイリアスによる停止を防ぐため `\cp`, `\mv`, `\rm` または `command ...` を使用する。`pkill` は使用せず `pgrep` で PID を確認して kill する。

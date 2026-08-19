# TODO-004. lint・型チェックと mise タスク

見込み: main = Sonnet 5 / effort medium、担当 = implementer + verifier
実施: main = Sonnet 5 / effort medium、担当 = implementer + verifier

## きっかけ

`tmr` と同じ構成（ruff / mypy / basedpyright、mise タスク一式）に
揃えるため。TODO-006（型ヒントの整備）が mypy / basedpyright を前提と
しているため、先に環境を整える必要があった。

## やったこと

- `pyproject.toml` の `[dependency-groups]` の `dev` に
  `ruff>=0.16.3` / `mypy>=2.3.1` / `basedpyright>=1.39.10` を追加
  （`uv add --group dev` で解決させた版）。
- `[tool.mypy]` / `[[tool.mypy.overrides]]` / `[tool.basedpyright]` を
  `pyproject.toml` に追加。`tmr` の該当セクションを流用しつつ、
  `python_version` は `"3.14"`、`mypy.overrides` の `module` は
  ytsched が実際に使う `click` / `tornado` / `pytest` のみに直した。
  `[tool.ruff]` は作らず、`tmr` と同じくコマンドラインで
  `--line-length 78` を渡す流儀に揃えた。
- `mise.toml` を新規作成。`tmr` と同じ
  `upgradeapt` → `upgrademise` → `upgradeuv` /
  `upgradeproject` → `lint` → `test` → `build` の構成。コマンド名を
  `ytsched` に変更し、各タスク末尾の動作確認は `uv run ytsched -V`
  ではなく `uv run ytsched --help` にした（ytsched の CLI には
  トップレベルの `-V` / `--version` が無いため。**追加しないことに
  決めた**。下記「やらないと決めたこと」参照）。`samples` 関連の
  行（tmr にはあるが ytsched には無い）は入れていない。
- `ruff format --line-length 78` と `ruff check --fix --extend-select I`
  を `src tests` に実行。12 ファイルが整形され、78 文字超の行は 0 に
  なった。import の並べ替えや未使用 import の削除など 14 件を自動修正。
- `mypy` / `basedpyright` の指摘のうち、明らかに軽微なもの 2 件を修正
  （`handler.py` の `conf: dict[str, str] = {}`、`ytsched.py` の
  `_sdf_cache` への型注釈と、それに伴う変数名の衝突解消）。

## やらないと決めたこと

- **`ruff check` に残った 97 件（`UP031` の printf 書式変換が 35 件と
  大半を占める、リファクタリング・書き換え系）は今回直さなかった。**
  TODO-006（型ヒント）とは別物で、範囲外の変更が大きくなるため。
  → 別項目 [TODO-015](TODO-015.%20ruff%20の整形・書き換え系の指摘を解消.md)
  として切り出した。
- **mypy / basedpyright に残った implicit Optional 系のエラー
  （35 件 / 28 件、`ytsched.py` の `time_start`/`time_end`、
  `main_handler.py:458` の `-> (datetime.date, str)` など）は直さなかった。**
  これは TODO-006 の本題そのものなので、そちらで扱う。
- **CLI にトップレベルの `-V` / `--version` を足すのは見送った。**
  機能追加になり今回の範囲外のため。`mise.toml` の動作確認は
  `--help` で代用している。
- **`[tool.ruff.lint]` でルールを絞ることはしなかった。**
  `tmr` の流儀（pyproject.toml に `[tool.ruff]` を持たずコマンドライン
  オプションのみ）に揃えることを優先した。結果として ruff 0.16 の
  既定の広い規則がそのまま効き、`mise run lint` は 97 件で止まる状態
  になっている（`tmr` 側も別の 8 件で同様に通らない）。

## テスト

- `uv run pytest tests` — 161 passed（整形の前後で変化なし）。
- `awk 'length > 78' src/ytsched/*.py tests/*.py` — 0 件。
- `mise tasks` — 依頼した 7 タスクがすべて存在。
- `mise run upgradeproject` — 正常終了。
- `mise run lint` — ruff check の 97 件で `ERROR task failed`
  （既知の状態。上記「やらないと決めたこと」で切り出し済み）。
- `uv run mypy src tests` — 35 errors（5 files）。
- `uv run basedpyright src tests` — 28 errors, 2 warnings。
- webapp を一時データディレクトリ・別ポートで起動し、
  `GET /ytsched/` が 200 であることを確認（プロセスは停止済み）。

以上、implementer の実装内容を verifier が独立に再実行して確認し、
すべて一致・問題なしだった。

詳しい経緯は `archives/agents/TODO-004/` の
`implementer-report.md` / `verifier-report.md` を参照。

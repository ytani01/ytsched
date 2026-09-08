# CLAUDE.md（ytsched）

`~/.claude/CLAUDE.md`（ユーザー全体の指示）が前提。ここには書かない。

## これは何か

個人用のスケジュール帳（Web アプリ）。
10年以上まえに、Perl CGI 相当で作ったものを2013年に Pythonベースに移植したが、
今回、最新のPython 3.14 / uv / pytest の環境へ移行した。
単一ユーザ専用で、認証はリバースプロキシに任せる前提（`README.md` 参照）。

データディレクトリ（既定 `~/ytsched/data`）は変えない。

データ形式は、タブ区切りテキストから **JSON Lines へ移した**
（TODO-018・TODO-020）。仕様は `docs/data-format.md` にあり、形式に
ついての決まりはそちらが置き場所（形式を変えたらあの文書も書き直す）。
既存データは `ytsched migrate` で一度に変換する。

## コードを触る前に読むこと

構成・データモデル・Web の構成・開発コマンドは、この文書ではなく
以下に分けてある。**リンク先は自動では読まれないので、コードを触る前に
必ず開くこと。**

- ソースコードの構成、クラス構造（`SchedDataEnt` / `SchedDataFile` /
  `SchedData`、`HandlerBase` / `MainHandler` / `EditHandler` の関係、
  フィルタ・検索文字列の扱い、`base.html` の autoescape）は
  `src/README.md`
- 技術スタック、開発環境の用意、`mise` のタスクと個別コマンド、
  テストの走らせ方は `docs/Developer.md`
- 各テストファイルが何を見ているか、`helpers.py` の役割、
  ゴールデンマスターテストの位置づけは `tests/README.md`
- データの保存形式（JSON Lines、壊れた行の扱いなど）は
  `docs/data-format.md`

## ログ

`mylog.py` のラッパを使う。標準の `logging` は使わない
（TODO-007 で loguru へ移行済み）。クラス本体に
`__log = getLogger(__qualname__)` を 1 つ置く。サンプルは
`docs/Developer.md` を参照。

## CodeGraph

クエリの書き方（**日本語は無視されるので英語で書く**）は
`~/.claude/CLAUDE.md` にある。ここには、このプロジェクトで測った結果だけを
残す（TODO-191）。

- **トークンは減らなかった。** 同じ問いを、Grep/Read だけの担当と
  `codegraph explore` だけの担当に投げたところ、消費は 77,679 対 77,132 で
  0.7% しか変わらなかった。ツール呼び出しは 22 対 15 に減ったが、
  `codegraph explore` の出力が問いの大小によらず 19〜22KB と大きく、
  往復が減ったぶんを出力量が相殺した。答えはどちらも正しかった
- **効くのは、同名メソッドの区別と影響範囲の把握。** `add_sde` は
  `SchedDataFile`（`ytsched.py:781`）と `SchedData`（同 1051）の 2 つ、
  `save` も 738 と 1107 の 2 つある。grep では、呼び出し側がどちらを
  指すのか分からない
- **grep で答えが出る問いには使わない。** 出力が一定サイズなので、
  小さい問いに使うと桁で損をする
- **ファイル名が概念とほぼ対応している**（`trash` / `sched_load` /
  `main_view` / `edit_handler`）ので、ファイル名を起点に引くと早い

## サブエージェントの分担

基準そのものは `~/.claude/CLAUDE.md` にある。TODO-001〜016 を見直して
その基準を決めたときの材料は `archives/todo/TODO-017` にある。

### トークン消費量の記録

集計の手順（`token-usage.py` の使い方、`--since` の渡し方）は
`todo-close` / `todo-workflow` skill にある。ここには ytsched 固有の
ことだけを残す。

- **`mise run tokens -- TODO-NNN` で呼べる。** 中身は
  `~/.claude/bin/token-usage.py`（TODO-035、admin の TODO-010）
- **概算料金の単価は `~/.claude/bin/token-usage.py` の `PRICING` に持たせてある**
  （TODO-044）。**Sonnet 5 は $2/$10。** 導入価格として告知されたが、
  2026-09-01 に予定されていた $3/$15 への値上げは行われず、そのまま正規の
  単価になった（2026-09-07 に公式のドキュメントで確認、TODO-190）。単価は
  一度も変わっていないので、`archives/todo/` の概算料金は互いに比べられる
- **過去の項目は遡れない。** transcript が 2026-08-22 以降しか残っていない

### 担当への共通の前提

**プロジェクトの前提を `.claude/agents/*.md` へ書き写さない。**
サブエージェントには、この `CLAUDE.md` と `~/.claude/CLAUDE.md` の両方が
そのまま届いている（TODO-022 で実測）。定義ファイルに書くのは、
**その担当の役割と、その担当だけに要る注意**にとどめる。

CLAUDE.md に書きようが無くて、どの担当にも要るものだけをここに置く。

- **アプリの起動を確かめるときは、`--datadir` に必ず一時ディレクトリを
  指定する。** `~/ytsched/data` の実データを汚さないため
- **`mise run upgradeproject` は、担当には走らせない。**
  `rm -f uv.lock` → `uv sync` → `uv pip install -U` が走り、呼ぶたびに
  依存を上げ直す。テストが壊れたときに、変更のせいか依存が上がったせいかが
  分からなくなる（TODO-022）。**`mise run fmt` / `typecheck` / `lint` /
  `test` / `build` は叩かせてよい。** `lint` の `upgradeproject` への
  依存は切ってあるので、依存は上がらない（TODO-023）。
  `uv run ruff format` / `ruff check` / `basedpyright` / `mypy` /
  `pytest` を個別に叩かせてもよい

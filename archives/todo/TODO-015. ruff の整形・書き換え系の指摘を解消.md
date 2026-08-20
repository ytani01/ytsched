# TODO-015. ruff の整形・書き換え系の指摘を解消

見込み: main = Sonnet 5 / effort medium、担当 = implementer + verifier
実施: main = Opus 5 / effort high、担当 = implementer + verifier

分担の理由と各担当の報告は `archives/agents/TODO-015/` にある。

## きっかけ

TODO-004（lint・型チェックと mise タスク）で `mise run lint` を実行した際、
`ruff check` が 97 件のエラーで止まった。うち `RUF013`（implicit-optional）は
TODO-006（型ヒントの整備）で、`UP031` の 1 件は TODO-007（loguru への移行）で
消えており、着手時点で 84 件が残っていた。

`UP031` 33 / `DTZ011` 13 / `FLY002` 13 / `D419` 10 / `RUF012` 5 /
`EXE001` 4 / `C408`・`DTZ005`・`PERF402`・`PLC0206`・`SIM102`・`SIM118`
各 1 件。

## やったこと

- **`DTZ011` / `DTZ005`（14 件）は規則ごと除外した。** `pyproject.toml` に
  `[tool.ruff.lint]` を新設し、`ignore = ["DTZ005", "DTZ011"]` を書いた。
  手帳代わりのソフトで、日付はすべて手元のローカル時刻。14 箇所に tz を
  付けて回ってもノイズにしかならない。**コマンドラインではなく
  `pyproject.toml` に書いた**のは、素の `uv run ruff check` やエディタの
  LSP でも出なくするため。TODO-004 で決めた「`pyproject.toml` に
  `[tool.ruff]` を持たない」流儀からは、ここだけ外れる。
  `"DTZ"` とまとめず 2 個だけ書いてある（他の DTZ 規則まで黙らせないため）
- **`EXE001`（4 件）はシェバンを消した。** `edit_handler.py` /
  `handler.py` / `main_handler.py` / `webapp.py` は単体で実行しない
  モジュールで、相対 import を使っているので直接実行しても動かない。
  入口は `uv tool install` で入る `ytsched`（TODO-008）
- **`UP031`（33 件）は f-string へ書き換えた。** ruff の `--unsafe-fixes` は
  UP031 → UP032 の 2 段（いったん `.format()` を経由する）でしか直せず、
  複数行の `.format()` になった 4 箇所は手で書き換えた
- **`D419`（10 件）は消さずに日本語の docstring を書いた。**
  `is_todo()` / `is_important()` などは「`type` の先頭で判定」「`title` の
  先頭で判定」という、このソフト特有の設計が書ける箇所だった
- **`RUF012`（5 件）は `ClassVar` を付けた。** `field(default_factory=...)`
  は使っていない（dataclass ではないうえ、インスタンスごとに別の
  オブジェクトになると挙動が変わる）。全参照が読み取り専用であることを
  確かめてある
- 残り 6 件（`C408` / `SIM102` / `PERF402` / `PLC0206` / `SIM118`）は
  指摘どおりに書き換えた

決めたこと。

- **`FLY002`（13 件）は、13 箇所すべて `# noqa: FLY002` を付けて
  `"\t".join([...])` のまま残した**（2026-08-20、利用者の判断）。
  13 箇所とも「タブ区切りの 1 行を、項目を縦に並べて組み立てる」形で、
  縦の並びが項目の順序と個数を見せている。リテラルにすると
  `"id-t\t2021/03/01\t:-:\t□買い物\tノートを買う\t\t"` のようになり、
  **末尾の空項目 2 つが `\t\t` に潰れて数えないと分からない**。
  `ytsched.py` の `mk_dataline()`（production 側）も、保存形式を
  組み立てる本体なので同じ理由で残してある。
  **項目には「解消する」と書いていたが、着手して中身を見たうえで
  方針を変えた**
- **URL パターンは `self.URL_PREFIX` をそのまま書く**（2026-08-20、
  利用者の判断）。`r"%s" % self.URL_PREFIX` に対する ruff の出力は
  `rf"{self.URL_PREFIX}"` だが、`URL_PREFIX` に正規表現の特殊文字は
  無く、f-string も `r` も要らない。末尾に `/` や `/edit` が付く
  残り 3 行は、連結が要るので f-string のまま

## 分かったこと

`--extend-select I` は、この版の ruff（0.16.3）では効果が重複している。
`--isolated` でも `I001` が出るので、`I` はすでに既定の select に
含まれているらしい。`mise.toml` はそのままにしてある（害は無く、
将来 ruff の既定が変わったときの備えになる）。

## テスト

`uv run ruff check --extend-select I src tests` と、素の
`uv run ruff check src tests` が両方とも `All checks passed!` になった。
`ruff format --line-length 78 --check` は 14 ファイルとも整形済み、
basedpyright と mypy もエラー無し、`uv run pytest tests` は 174 件すべて通る。

コードの変更は動作を変えていない。verifier が `git diff` を全ファイル
読み合わせ、printf 書式と f-string の対応（`%s`→`{}`、`%02d`→`:02d`、
引数の順序）、`SIM102` でまとめた `if` の真理値、`ClassVar` が実行時に
影響しないことを確かめている。

一時ディレクトリにデータを置いてアプリを起動し、一覧表示・編集画面・
検索・`cmd=add` での保存が動くこと、保存されたデータと `Conf.cgi` が
タブ区切りのままであることも確認した。`/ytsched`（末尾スラッシュ無し）と
`/ytsched/` の両方が 200 を返すことも見てある。

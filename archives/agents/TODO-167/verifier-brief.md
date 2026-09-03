# TODO-167 verifier への依頼

## 目的

implementer の変更が実際に動くかを確かめる。**コードは直さないこと。**
見つけたことは報告に書き、直すかどうかは管理者が決める。

先に読むもの:

- `archives/agents/TODO-167/implementer-brief.md`（何をやるつもりだったか）
- `archives/agents/TODO-167/implementer-report.md`（何をやったか）
- `TODO.md` の「TODO-167」の節（決めたこと）

## 確かめること

1. `uv run ruff format --check` / `uv run ruff check` /
   `uv run basedpyright` / `uv run pytest` が通ること
2. **実際にアプリを起動して確かめる。**
   `--datadir` には必ず一時ディレクトリを指定すること（`~/ytsched/data` を
   汚さないため）。curl で `/` を取り、`class="my-week-panel` の数を数える:
   - `conf.json` 未設定（＝作られた既定値 `LoadWeekPages="4"`）で **9**
   - `"0"` で 1、`"10"` で 21、`"103"`（上限）で 207
   - `"104"` / `"-1"` / `"abc"` は既定へ落ちて 9。警告ログが 1 行出て、
     例外・トレースバックが出ていないこと
3. **`conf.json` が無い一時 datadir で起動したとき**、既定値の入った
   `conf.json` が実際にできること。中身のキーが依頼書の 9 つで、値が
   すべて文字列であること
4. **既に `conf.json` がある datadir では、中身を上書きしないこと。**
   一部のキーしか書いていない `conf.json` を置いて起動し、書いた値が
   そのまま残ること（足りないキーが勝手に足されるかどうかは実装の
   選択なので、どちらだったかを報告に書く）
5. 月間表示（`?view=month`、`LoadMonthPages`）が今までどおりであること
6. `archives/` を除いて `LoadMonths` / `months2weeks` / `load_months` /
   `DAYS_PER_MONTH` が残っていないこと（grep）

## 報告

`archives/agents/TODO-167/verifier-report.md` に書く。返事は 5 行以内で、
終わったか・報告ファイルのパス・判断が要る点だけ。

## 追記（implementer の報告を受けて）

- implementer は依頼書に無かった `tests/test_handler.py`・
  `tests/test_main_handler.py` も直している（`conf.json` を既定値で作る
  ようにした結果、中身の完全一致を見ていたテストが壊れたため）。
  **この直し方が、テストの見ている中身を薄めていないか**を見ること。
  「壊れたから緩めた」だけになっている箇所があれば報告する
- `mise run fmt` は `archives/` 以下の `.md`・`.py` まで書き換える。
  管理者が戻したので、**`archives/agents/TODO-167/` 以外の `archives/` を
  変更しないこと**

# TODO-167 implementer への依頼

## 目的

週間表示の先読み範囲の設定を、月単位の `LoadMonths` から画面（週）数の
`LoadWeekPages` へ変える。あわせて `conf.json` が無いときに既定値を書いた
ものを作る。TODO.md の「TODO-167」の節に決めたことがあるので、先に読むこと。

## やること

### 1. `LoadMonths` → `LoadWeekPages`

- `src/ytsched/main_binder.py`
  - `CONF_KEY_LOAD_MONTHS = "LoadMonths"` → `CONF_KEY_LOAD_WEEK_PAGES = "LoadWeekPages"`
  - `DEF_LOAD_MONTHS = 1` / `LOAD_MONTHS_MIN` / `LOAD_MONTHS_MAX = 24` →
    `DEF_LOAD_WEEK_PAGES = 4` / `LOAD_WEEK_PAGES_MIN = 0` / `LOAD_WEEK_PAGES_MAX = 103`
  - `DisplayArgs.load_months` → `load_week_pages`
  - 読み方（`_get_conf_int()`）は `LoadMonthPages` とまったく同じ形にする
- `src/ytsched/main_view.py`
  - `months2weeks()` と、それだけのために置いてある `DAYS_PER_MONTH` を削除
  - `_mk_weeks()` の range を `range(-args.load_week_pages, args.load_week_pages + 1)` にする
- `src/ytsched/main_handler.py`
  - 再公開の `months2weeks()`（92 行あたり）を削除
- `src/ytsched/ytsched.py`（746 行あたりのコメント）
  - `DEF_CACHE_SIZE` の根拠の説明を `LoadWeekPages`（既定 4、上限 103）で
    書き直す。**日数は変わらない**（前後 103 週 → 207 週 → 1449 日 + ToDo 1 で
    1450）ので `DEF_CACHE_SIZE = 2000` はそのまま
- 旧 `LoadMonths` は読まない（後方互換のコードを入れない）

### 2. `conf.json` が無ければ既定値で作る

- 書き出すのは `ConfFile`（`src/ytsched/conf.py`）の役目。
  `_load()` が `FileNotFoundError` を捕まえたところで、既定値を入れて
  書き出す（`_save()` を使う。`_stat_key` も持ち直る）。
  書けなかったとき（`PermissionError` など）は `save_if_dirty()` と同じく
  警告を 1 行出すだけにして、例外を外へ出さない
- 中身は**画面から自動保存されるキーも含めた全キー**。値は文字列:
  `SearchStr` `""` / `FilterStr` `""` / `ToDo_Days` `"1y"` / `SearchN` `"5"` /
  `MonthCal` `"1"` / `LoadWeekPages` `"4"` / `LoadMonthPages` `"2"` /
  `AutoTurnMsec` `"700"` / `TrashMax` `"100"`
- **既定値の持ち方に注意。** `conf.py` は `main_binder.py` /
  `trash_handler.py` / `handler.py` から使われる側なので、そちらを import
  すると循環参照になりうる。`conf.py` に素の dict として持ち、
  「どのクラスの既定と揃えているか」をコメントで書くこと。
  そのうえで、**dict の値が各クラスの既定と一致していることを見るテストを
  足す**（テスト側からは両方 import できる）。ズレたまま気づかないのを防ぐため
- 既定値を書き出しても、既存の挙動が変わらないこと（`ToDo_Days="1y"` が
  `DEF_TODO_DAYS=365` と同じ、`MonthCal="1"` が `DEF_MONTH_CAL=True` と同じ）を
  確かめること

### 3. 文書

- `docs/User.md`（203 行あたりの表と 209 行の例）— `LoadMonths` の行を
  `LoadWeekPages`（既定 4、範囲 0〜103、意味は「前後何週ぶんの週を HTML に
  含めるか」）へ。`conf.json` が無ければ既定値を書いたものが作られる旨も
  1 行足す。**利用者向け文書なので TODO 番号は書かない**
- `src/README.md`（194 行あたりと 221 行あたり）— キー名と既定・範囲、
  `months2weeks()` が無くなったこと
- `tests/README.md` — `LoadMonths` に触れているところがあれば直す

### 4. テスト

- `tests/test_web.py` の `LoadMonths` テスト群（1062〜1114 行あたり）を
  `LoadWeekPages` 用に書き直す。`months2weeks()` は無くなるので、
  期待値は `DEF_LOAD_WEEK_PAGES * 2 + 1` のように直接数える。
  範囲外の値は `"104"` などに直す
- `tests/test_browser.py`（291・311・435 行あたり）の `LoadMonths` も直す
- `conf.json` が無いときに既定値のファイルができることを見るテストを足す
  （`tests/test_web.py` か、`ConfFile` を直接見るテストがあればそちら）
- 上記 2. の「既定値の dict が各クラスの既定と一致する」テスト

## 完了条件

- `uv run ruff format` / `uv run ruff check` / `uv run basedpyright` /
  `uv run pytest` がすべて通る
- リポジトリ全体（`archives/` を除く）に `LoadMonths` / `months2weeks` /
  `load_months` / `DAYS_PER_MONTH` が残っていない

## 報告

`archives/agents/TODO-167/implementer-report.md` に書く。返事は 5 行以内で、
終わったか・報告ファイルのパス・判断が要る点だけ。

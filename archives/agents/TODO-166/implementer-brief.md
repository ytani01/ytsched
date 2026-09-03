# TODO-166 implementer への依頼

## 目的

月間表示の先読み画面数を `conf.json` の `LoadMonthPages` で変えられるようにする。
仕様は `TODO.md` の TODO-166 の節を読むこと（そちらが正）。

## やること

1. `src/ytsched/main_binder.py`
   - `CONF_KEY_LOAD_MONTH_PAGES = "LoadMonthPages"`、
     `DEF_LOAD_MONTH_PAGES = 2` / `LOAD_MONTH_PAGES_MIN = 0` /
     `LOAD_MONTH_PAGES_MAX = 10` を、既存の `LoadMonths` 一式に倣って足す
   - `DisplayArgs` に `load_month_pages: int` を足し、
     `get_display_args()` で `_get_conf_int()` から入れる
     （`LoadMonths` とまったく同じ形にする）
2. `src/ytsched/main_view.py`
   - `_mk_month_blocks()` のハードコード `for offset in (-1, 0, 1)` を
     `range(-n, n + 1)`（n = `args.load_month_pages`）にする。
     docstring の「3 つ」も直す
   - `build()` の「18 ヶ月ぶんでも」というコメントも実態に合わせる
3. 文書
   - `src/README.md`: 「前後を先読みして 3 ブロック ＝ 18 ヶ月ぶん」を
     設定で変わる旨に書き直す。手で書く設定が `LoadMonths` と
     `AutoTurnMsec` の 2 つだとしている箇所も 3 つに直す
   - `docs/User.md`: 設定表に `LoadMonthPages`（既定 2、範囲 0〜10）を足す
   - `tests/README.md`: 「3 ブロック」の記述を直す
4. テスト
   - `tests/test_main_handler.py:1306` あたりの `_mk_month_blocks()` の
     単体テスト、`tests/test_web.py:843` の「3 ブロック」を、既定 2 ＝
     5 ブロックに合わせて直す
   - `LoadMonthPages` を 0 / 2 / 範囲外にしたときの動きを見るテストを足す
     （`tests/test_web.py` の `LoadMonths` のテスト群（1030 行あたり）が手本）

## やらないこと

- JS・CSS は触らない
- `ytsched.py` の `DEF_CACHE_SIZE` のコメントは触らない（月間表示は
  `load_month_cal()` しか使わないため）
- `TODO.md` と `archives/` は main が書く。触らない

## 完了条件

`uv run ruff format` / `uv run ruff check` / `uv run basedpyright` /
`uv run pytest` が通ること（`mise run fmt` / `lint` / `typecheck` / `test` でもよい）。
`mise run upgradeproject` は走らせない。

## 報告

`archives/agents/TODO-166/implementer-report.md` に、変更点・検証結果・
残る懸念を書く。返事は 5 行以内（終わったか / 報告ファイルのパス /
判断が要る点）。

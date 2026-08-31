# TODO-137 implementer 報告

依頼（`archives/agents/TODO-137/implementer-request.md`）の設計どおりに実装した。

## 変更したファイル

- `src/ytsched/main_binder.py` — `DisplayArgs.view`（`get_view()`。
  `"month"` 以外は `"week"`）と `month_mode` プロパティ
  （`view == "month" and not search_mode`）を追加
- `src/ytsched/main_view.py` — `build()` を `args.month_mode` で分岐。
  共通の値は 1 か所（`common` dict）にまとめ、`**common` で展開。
  `_mk_month_blocks()` を追加（offset -1/0/1 の 3 ブロック、
  `block_index = (year*12+month-1)//6` で年またぎも扱う）。
  テンプレートへ渡す `view` は `args.view` そのものではなく
  `"month" if args.month_mode else "week"`（検索モードでの上書きを
  反映するため）
- `src/ytsched/sched_load.py` — `MonthBlock` dataclass を追加
  （`offset`/`year`/`start_month`/`base_date`/`month_cals`）
- `src/ytsched/webroot/templates/mini_cal.html`（新規） — `main.html`
  にあったミニカレンダーの `<table>` を切り出し。`mc`/`cur_monday`/
  `mini_cal_action`/`mini_cal_caption_action`/`today` を呼び出し側が
  `{% set %}` してから include する約束（`sde.html` と同じ流儀）
- `src/ytsched/webroot/templates/month.html`（新規） — `.my-week-viewport`
  / `#week_wrap` / `.my-week-panel my-month-panel` を使い回し、
  `mini_cal.html` を 6 個ずつ `.my-month-grid` に並べる
- `src/ytsched/webroot/templates/main.html` — `#main` に `data-view`、
  週間表示の本体を `{% if view == 'month' %}{% include month.html %}
  {% else %}...{% end %}` で分岐。ミニカレンダーは `mini_cal.html` を
  include する形に変更（`mini_cal_caption_action = 'month-view'`）
- `src/ytsched/webroot/templates/base.html` — `month.js` を `week.js` の
  次に読み込む
- `src/ytsched/webroot/static/js/month.js`（新規） — `blockKeyOfDate()`
  （内部）・`setActiveBlockOfDate()`・`moveActiveBlock()`
- `src/ytsched/webroot/static/js/week.js` — `moveActiveDate()` と
  `weekOffsetOfDate()` の先頭に `ytsched.view_month` の分岐を追加
- `src/ytsched/webroot/static/js/nav.js` — `scrollToDate()` と
  `popstateHdr()` の先頭に同様の分岐
- `src/ytsched/webroot/static/js/swipe.js` — `swipeMiniCal` を立てる
  2 か所（`touchStartHdr`/`mouseDownHdr`）に `!ytsched.view_month` を追加
- `src/ytsched/webroot/static/js/main-page.js` — `onloadHdr()` で
  `ytsched.view_month` をセット。`actionMouseDownHdr()` に
  `week-date`/`month-view` の case を追加
- `src/ytsched/webroot/static/css/my.css` — 末尾に `.my-month-title` /
  `.my-month-grid` / `.my-month-grid .my-mini-cal` を追加
- `tests/test_main_handler.py` — `TestMonthBlocks`（先頭月・3 ブロック・
  `base_date`・年またぎ）
- `tests/test_web.py` — `TestMonthView`（3 ブロック・6 ヶ月の caption・
  検索モードでの上書き・不正な `view`）。既存の `TestMonthMiniCal.
  test_shows_two_months` の caption 抽出用正規表現を、caption に
  `my-btn`/`data-action` が付くようになった分だけ緩めた（既存挙動の
  意図した変化への追随）
- `tests/test_browser.py` — `test_month_view_round_trip`
  （週間→月間→週間の往復）
- `docs/User.md` / `src/README.md` / `tests/README.md` — それぞれ
  「月間表示」節・`view` の分岐と `month.html`/`mini_cal.html`/
  `month.js`・テストの説明を追加

## 確認したこと

- `uv run pytest tests -q --ignore=tests/test_browser.py` → 522 件成功
- `uv run pytest tests/test_browser.py -q` → 47 件成功（TODO-137 の新規
  1 本を含む）
- `mise run typecheck` / `mise run lint`（ruff format/check・
  basedpyright・mypy・prettier・eslint）→ すべて通過
- `--datadir` を一時ディレクトリにしてアプリを起動し、
  `curl 'http://localhost:PORT/ytsched/?view=month&date=2026-09-01'` で
  `data-block="` が 3 件、`2026/01`〜`2026/09` の caption が出ること、
  `data-view="month"` が付くことを確認

## 単独で決めた判断

1. **`MainViewBuilder.build()` がテンプレートへ渡す `view` を、
   `args.view`（クエリの生値）ではなく `args.month_mode` から
   `"month"/"week"` を作り直した。** 検索中に `view=month` が来ても
   週間表示に倒す（`month_mode` が優先する）仕様なので、テンプレートの
   分岐と `#main` の `data-view`（JS の `ytsched.view_month`）も
   実際に描いたモードに合わせないと、検索中に月間表示用の JS 分岐
   （スワイプでのミニカレンダー無効化など）だけが誤って効いてしまう
   ため
2. **既存テスト `test_shows_two_months` の正規表現を緩めた。**
   caption が `mini_cal_caption_action` 付きで `my-btn`/`data-action`/
   `data-date` を持つようになったのは設計どおりの意図した変更なので、
   壊れた既存テストは新しい形に追随させた（範囲外の項目には手を
   出していない）

## 残る懸念

- 設計から外れた箇所は無い
- `docs/data-format.md` は形式に変更が無いため触っていない

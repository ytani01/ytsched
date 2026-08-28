# TODO-092. テンプレートの掃除

|      | main | 担当 |
|------|------|------|
| 見込み | Sonnet 5 / effort medium | implementer + verifier |
| 実施 | Sonnet 5 / effort medium | implementer + verifier |
| 消費 | output 55,422 / cache_creation 367,212 / 概算 $4.2 |
|      | main 65% + implementer 19% + verifier 9% + wording 7%（料金の割合） |

基本設計のレビュー（2026-08-27）の I・J・K・L。分担の理由と各担当の報告は
[archives/agents/TODO-092/](../agents/TODO-092/) にある。挙動は変えていない。

## きっかけ

- **I**: `{% include sde.html %}` は名前空間を親と共有するので、`sde.html`
  は `main.html` 側で `{% set %}` された変数を宣言なしに使っていた。
  `main.html` 側で `{% set %}` の位置を動かすと黙って壊れる。
- **J**: 期限の近さで背景色のクラス（`class_bg`）を分ける判定が
  `sde.html` の先頭にあり、
  「1 週間以内」の `7` が直接書いてあった。`is_todo()` などは
  `SchedDataEnt` にあるのに、この判定だけ置き場所が違った。
- **K**: どこからも読まれない hidden input・クエリ・変数が残っていた。
- **L**: TODO-050 で日付は `date=YYYY-mm-dd` に一本化済み。`year`+`month`
  +`day` の経路はテンプレートにも `static/js/` にも呼び出しが無かった。

## やったこと

- **I**: `sde.html` の 1 行目の直後に `{# ... #}` を足し、`main.html` から
  受け取る 5 個（`sde` / `sched_date` / `today_flag` / `today` /
  `url_prefix`）と、名前空間を共有していることを書いた。掃除前の 10 個の
  うち `delta_day1` / `date` / `date_from` / `date_to` / `sde_count` は
  この項目で参照が消えたので、コメントには入れていない。
- **J**: `SchedDataEnt` に `TODO_NEAR_DAYS = 7`（クラス定数）と
  `todo_urgency(self, today) -> str` を追加。`over`（期限を過ぎた）/
  `near`（1 週間以内）/ `""` を返す。`is_todo()` の判定はしない。
  `sde.html` の判定を `sde.todo_urgency(today)` を使う形にした（空文字なら
  `my-sde-todo`、それ以外は `my-sde-todo-<戻り値>`）。CSS は触っていない。
  `main_handler.py` の `DELTA_DAY1` 定数と `render()` の `delta_day1=`
  引数を削除。
- **K**: `base.html` の `{% set now = ... %}`、`main.html` の
  `<!-- hidden params -->` の中の `id` の無い `cur_day` と `#search_n`、
  `main.html` / `sde.html` の `sde_count`、`sde.html` の `doGet()` に
  渡していた `cur_date` / `date_from` / `date_to` を削除。`#sde_align` /
  `#date_from` と、`form_search` / `form_filter` の中の `cur_day` は
  読まれているので残した。
- **L**: `main_handler.py` の `get_date()` から `year`+`month`+`day` の
  ブロックを削除し、docstring も直した。メソッド `str2ymd_date` /
  `ymd2date` を削除。`handler_util.check_int_range()` /
  `check_date()` は `str2todo_days()` などがまだ使うので残した。
  `year`/`month`/`day` だけを見ていたテスト（`test_main_handler.py` 3 個、
  `test_web.py` 12 個）を削除。

### 単独で決めた判断

- **`main.html` の検索モードの期間・件数の表示（`<!-- 検索期間・件数 -->`）
  にある `{% set days = date_to - date_from + delta_day1 %}` は、まだ
  使われていた。** 同じブロックの 2 行上が既に
  `date.resolution`（＝`datetime.timedelta(days=1)`）を使っているので、
  それに合わせて `+ date.resolution` へ置き換えた。値・表示（`(in N days)`）
  とも変わらない。これで `DELTA_DAY1` / `delta_day1` を全廃できた。

## テスト

- `mise run test` 474（473 passed + 1 failed）。落ちた 1 個は
  `test_browser.py::test_tap_again_stops_auto_page_turn`
  で、自動ページ送り（TODO-084）のタイミング依存の flaky。単体で再実行
  すると通る。`test_browser.py` はこの項目で触っていない。
  内訳は `test_todo_urgency` +7、`year`/`month`/`day` テスト削除 -15。
- `mise run typecheck` 0 errors（basedpyright / mypy）、`mise run lint` 通過。
- `uv run ytsched webapp --datadir <一時ディレクトリ>` で起動。
  `GET /ytsched/`・`?date=...`・検索モード（`?...&search_str=会議`）が
  ともに 200。未展開の `{{` / `{%` の残りなし。期間・件数の表示は
  `(in 1826 days)` と整数で出る。サーバログに例外なし。

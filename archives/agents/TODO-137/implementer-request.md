# TODO-137 implementer への依頼

## 目的

週間表示に加えて **月間表示モード**を足す。月のカレンダー（既存の
月間ミニカレンダー）を 6 ヶ月分、2 列 × 3 行で並べる。

仕様は `TODO.md` の「TODO-137. 月間表示モード」にある。**この文書は、
その仕様を実装する際の設計を指定するもの**で、下の設計から外れる場合は
勝手に変えず、報告に書くこと。

## 対象範囲

- `src/ytsched/main_binder.py`
- `src/ytsched/main_view.py`
- `src/ytsched/sched_load.py`
- `src/ytsched/webroot/templates/main.html`
- `src/ytsched/webroot/templates/month.html`（新規）
- `src/ytsched/webroot/templates/mini_cal.html`（新規・切り出し）
- `src/ytsched/webroot/static/js/month.js`（新規）
- `src/ytsched/webroot/static/js/week.js` / `nav.js` / `swipe.js` /
  `main-page.js`
- `src/ytsched/webroot/templates/base.html`（`month.js` の読み込み）
- `src/ytsched/webroot/static/css/my.css`
- `tests/test_main_handler.py` / `tests/test_web.py` / `tests/test_browser.py`
- `docs/User.md` / `src/README.md` / `tests/README.md`

`~/ytsched/data` の実データには触らない（動作確認は `--datadir` に
一時ディレクトリを指定する）。

---

## 設計

### 1. サーバ側

**`view` クエリ**（`week` / `month`）で切り替える。`conf.json` には
保存しない。

- `MainBinder.get_display_args()` で `view` を読む。`"month"` 以外は
  すべて `"week"` として扱う（不正な値でエラーにしない）
- `DisplayArgs` に `view: str` を足し、
  `month_mode` プロパティ（`view == "month" and not search_mode`）を持たせる。
  **検索モードが優先**（検索結果は月の区切りに合わず、ミニカレンダーも
  出していないため）
- ミニカレンダーの表示スイッチ（`month_cal`）が off でも、月間表示は出す。
  月間表示はミニカレンダーそのものが目的なので、スイッチには従わない

**ブロックの決め方**（`sched_load.py` に `MonthBlock` を足す）:

```python
@dataclasses.dataclass
class MonthBlock:
    offset: int  # -1, 0, 1
    year: int  # 先頭月の年
    start_month: int  # 1 か 7
    base_date: datetime.date
    month_cals: list[MonthCal]  # 6 個
```

- 先頭月は `1 if date.month <= 6 else 7`。ブロックは
  1〜6 月 と 7〜12 月 の 2 つだけ
- `offset` は -1・0・1 の 3 ブロック（合計 18 ヶ月）。前後を先読みして
  おき、JavaScript がページを読み直さずに送れるようにする
- `base_date` は、**offset 0 だけ `args.date` そのもの**、
  offset ±1 は**そのブロックの先頭月の 1 日**。
  offset 0 を `args.date` にするのは、6 ヶ月送って戻ってきたときに元の
  日付が残るようにするため

**`MainViewBuilder.build()`** は `args.month_mode` で分岐する。

- 月間表示では `load_todo()` / `load_week()` を呼ばない（使わないため）。
  `load_month_cal()` は `_month_cal_cache` が効くので、18 ヶ月ぶんでも
  月ごとに 1 回で済む
- テンプレートが参照する値は週間表示と同じキーで揃える。月間表示では
  `weeks=[]`、`sched=[]`、`date_from=date_to=args.date` とし、
  `view` と `month_blocks` を足す（週間表示では `month_blocks=[]`）
- 共通の値（`today`・`date`・`filter_str`・`search_str`・
  `todo_days_list`・`todo_days_value`・`search_n`・`month_cal`・
  `auto_turn_msec`・`sde_align`・各 `*_error`・`search_mode`）は、
  週間・月間で 1 か所にまとめてから足すこと（同じ辞書を 2 か所に
  書き写さない）

### 2. テンプレート

**`mini_cal.html`（新規）**: いまの `main.html` にあるミニカレンダーの
`<table class="my-mini-cal">` …… `</table>` をそのまま切り出す。
`{% include %}` は呼び出し側の名前空間を共有するので、include の前に
次を `{% set %}` してから呼ぶ約束にする（`sde.html` と同じ流儀）。

| 変数 | 週間表示 | 月間表示 |
|------|----------|----------|
| `mc` | `w.month_cals` の要素 | `b.month_cals` の要素 |
| `cur_monday` | `w.monday` | `date` を含む週の月曜 |
| `mini_cal_action` | `'scroll-date'` | `'week-date'` |
| `mini_cal_caption_action` | `'month-view'` | `''`（押せない） |

- 表示中の週の枠（`my-mini-cal-week-cur`）は `cur_monday` で判定する
  （今の `w.monday` 直書きをこれに置き換える）。月間表示では、
  週間表示から持ってきた基準日（`date`）の週に枠が出る
- `mini_cal_caption_action` が空でないときだけ、caption に
  `my-btn` と `data-action` / `data-date`（`YYYY-MM-01`）を付ける

**`month.html`（新規）**: 週間表示と同じ枠組み
（`.my-week-viewport` / `#week_wrap` / `.my-week-panel`）を使う。
**クラスと id を使い回すのは、パネルの並べ直しと横滑り
（`layoutWeeks()` / `slideWeekWrap()` / `setActiveWeek()`）を
そのまま使うため。** その理由をテンプレートにコメントで書くこと。

```
.my-week-panel my-month-panel   data-offset / data-monday（= base_date）/
                                data-block（"YYYY-MM"、先頭月）
  .my-month-title               "2026/01 〜 2026/06"
  .my-month-grid                6 個の mini_cal.html
```

`#week_wrap` の `data-monday` は `date`。

**`main.html`**: `#main` に `data-view="{{ view }}"` を足し、
週間表示の本体（`.my-week-viewport` 〜 `</div><!-- my-week-viewport -->`）
を `{% if view == 'month' %}{% include month.html %}{% else %}…{% end %}`
で分ける。ヘッダー（週バー・日付入力欄）とフッターは今のまま両方で出す。

### 3. JavaScript

`month.js`（新規、`base.html` で `week.js` のあとに読み込む）に、
月間表示だけの処理を置く。`window.ytsched.view_month`（真偽値）は
`main-page.js` の `onloadHdr()` が `#main` の `data-view` から入れる。

`month.js` が外へ出すもの:

- `blockKeyOfDate(date_str)` → `"YYYY-01"` / `"YYYY-07"`（内部）
- `setActiveBlockOfDate(date_str, push_flag)` → その日を含むブロックの
  パネルが DOM にあれば `setActiveWeek()` で移って true、無ければ false
- `moveActiveBlock(direction, path)` → `moveToMonday()` の月版。
  `slideWeekWrap()` で滑らせてから `setActiveWeek(next_offset)`、
  読み込み範囲の外なら `doGet(path, {date: 次のブロックの先頭月の 1 日,
  view: "month"})`

既存ファイルへ足す分岐は、**次の 5 か所だけ**にする。

1. `week.js` の `moveActiveDate()` の先頭
   → `ytsched.view_month` なら `moveActiveBlock()` を呼んで返す。
   これでフッターの ＜ ＞・キーの ← →・スワイプ・自動ページ送りが
   すべて 6 ヶ月単位になる（どれも `moveActiveDate()` を通っている）
2. `week.js` の `weekOffsetOfDate()` の先頭
   → `ytsched.view_month` なら null を返す（月間のパネルの
   `data-monday` を週の月曜と取り違えないため）
3. `nav.js` の `scrollToDate()` の先頭
   → `ytsched.view_month` なら `setActiveBlockOfDate()` を試し、
   移れたら `ytState.elMain.style.visibility = "visible"` にして true、
   移れなければ `doGet(path, {date, view: "month"})` して false。
   ホームボタン・キーの Home・読み込み直後の位置合わせが、どれも
   ここを通る
4. `nav.js` の `popstateHdr()` の先頭
   → `ytsched.view_month` なら `setActiveBlockOfDate(date, false)` を
   試し、駄目なら `location.reload()`
5. `swipe.js` の `swipeMiniCal` を立てるところ（2 か所）
   → 月間表示では立てない。月間表示では画面全体がミニカレンダーなので、
   そのままだと 1 ヶ月送り（`moveActiveMonth()`、TODO-136）になってしまう

`main-page.js` の `actionMouseDownHdr()` に case を 2 つ足す。

- `week-date`（月間表示の日付セル）
  → `doGet(url_prefix, {date, sde_align: "top"})`（`view` は付けない）
- `month-view`（週間表示のミニカレンダーの `YYYY/MM`）
  → `doGet(url_prefix, {date, view: "month"})`

`pushDateInUrl()` は今の URL の `searchParams` を書き換えるだけなので、
`view=month` はそのまま残る（変更不要）。

### 4. CSS

`my.css` の末尾（ミニカレンダーの節の後ろ）に月間表示の節を足す。

- `.my-month-grid` は `display: grid; grid-template-columns: 1fr 1fr;`
- `.my-month-grid .my-mini-cal` は `flex` が効かないので `width: 100%`
  にする（既存の `.my-mini-cal` は 2 つ並べる前提で `flex: 1 1 0`）
- ミニカレンダーの各セルの見た目（数字・印・祝日/土曜の色・「今日」の
  枠・表示中の週の枠）は既存のものをそのまま使い、**新しい色や大きさを
  作らない**

### 5. テスト

- `tests/test_main_handler.py`
  - ブロックの先頭月が 1 月か 7 月になること（1〜6 月 → 1 月、
    7〜12 月 → 7 月。境界の 6/30・7/1・12/31・1/1 を含める）
  - 1 ブロックが 6 ヶ月で、前後を含めて 3 ブロック並ぶこと
  - offset 0 の `base_date` が `date` そのもの、±1 が先頭月の 1 日
    であること
  - 年をまたぐこと（例: 2021-07 のブロックの次が 2022-01）
- `tests/test_web.py`
  - `GET /?view=month&date=...` が 200 で、`my-month-panel` が 3 つ、
    caption が期待する 6 ヶ月ぶん出ること
  - 検索中（`search_str` が入っているとき）は `view=month` でも
    週間表示になること
  - `view` に不正な値を渡しても 200 で週間表示になること
- `tests/test_browser.py`
  - 週間表示の `YYYY/MM` を押す → 月間表示になる → 日付を押す →
    その日の週の週間表示に戻る、の 1 本
  - ブラウザが無ければ skip される既存の作りに合わせる

### 6. 文書

- `docs/User.md`「月間ミニカレンダー」の後ろに「月間表示」の節を足す。
  **利用者向けの文書には TODO 番号を書かない**（機能の現状だけを書く）
- `src/README.md` に `view` の分岐と `month.html` / `mini_cal.html` /
  `month.js` を足す
- `tests/README.md` の各テストファイルの説明を、足したテストに合わせて
  1 行ずつ更新する

---

## 完了条件

1. 上の設計どおりに動く（週間 ⇄ 月間の往復、6 ヶ月単位の移動）
2. **既存の週間表示の動きを変えない**（週送り・検索モード・
   ミニカレンダーのスワイプ・自動ページ送り）
3. `mise run fmt` → `mise run typecheck` → `mise run lint` →
   `uv run pytest tests` がすべて通る
4. 新しいコードのコメントは、周りの密度・書き方に合わせる。
   「なぜそうしたか」を書き、TODO 番号（TODO-137）で参照する

## 検証方法

- `uv run pytest tests` を通す
- `--datadir` に一時ディレクトリを指定してアプリを起動し、
  `curl 'http://localhost:PORT/?view=month&date=2026-09-01'` が
  6 ヶ月ぶんの caption を含むことを確かめる

## 報告

`archives/agents/TODO-137/implementer-report.md` に書く。内容は
**変更点・検証結果・残る懸念**に絞る。返事は 5 行以内で、
「終わったか・報告ファイルのパス・判断が要る点」だけにすること。

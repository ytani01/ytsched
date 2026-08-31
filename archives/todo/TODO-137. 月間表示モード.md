# TODO-137. 月間表示モード

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort high | implementer + verifier + reviewer |
| 実施 | Opus 5 / effort high | implementer + verifier + reviewer |
| 消費 | output 39,165 / cache_creation 488,236 / 概算 $10.6 |
|      | implementer 55% + main 30% + reviewer 11% + verifier 4%（料金の割合） |

分担の詳細は [archives/agents/TODO-137/README.md](../agents/TODO-137/README.md)。

## きっかけ

「月間表示モードを作る」という利用者からの依頼。ミニカレンダーを
6 ヶ月分並べ、週間表示のミニカレンダーの `YYYY/MM` から切り替える、
という仕様が示された。

着手前に、仕様のうち決まっていなかった 6 点を利用者に聞いて決めた。

- **ブロックの区切りは 1〜6 月と 7〜12 月**（依頼の「1 月または 6 月」は
  7 月の書き間違いだった）
- **`main.html` にモードを足す**（新しいハンドラは作らない）。データの
  読み込み（`load_month_cal()`）と設定・フィルタをそのまま使えるため
- **ヘッダー・フッターは週間表示と同じものを出す**
- **前後 6 ヶ月も先読みして、指に追従させて滑らせる**（週間表示と同じ
  作り。毎回サーバから取り直す案もあった）
- **月間表示であることは URL のクエリだけで持ち、`conf.json` には
  保存しない**
- **フッターの ＜ ＞ とキーの ← → も 6 ヶ月単位**（スワイプと揃える）

## やったこと

### サーバ側

`view` クエリ（`week` / `month`）で切り替える。`MainBinder.get_view()`
が読み、`DisplayArgs.month_mode`（`view == "month" and not search_mode`）
が実際のモードを決める。**検索モードが優先**で、検索中は `view=month`
が来ても週間表示に倒す（検索結果は月の区切りに合わず、ミニカレンダー
そのものを出していないため）。

`MainViewBuilder.build()` を `month_mode` で分岐させ、月間表示では
`load_todo()` / `load_week()` を呼ばずに `MonthBlock`（`sched_load.py`
に追加）を 3 ブロック組み立てる。ブロックは 6 ヶ月ぶんで、前後を
先読みするので合計 18 ヶ月。`load_month_cal()` は `_month_cal_cache`
が効くので、月ごとに 1 回しか読まない。

ブロックの区切りは、`(year * 12 + (month - 1)) // 6` という通し月数で
求める。年をまたぐときの繰り上がり・繰り下がりを個別に扱わずに済む。
パネルの基準日（`base_date`）は、offset 0 だけ `date` そのもの、
±1 は先頭月の 1 日にした。6 ヶ月送って戻ってきたときに、元の日付が
残るようにするため。

### テンプレート

ミニカレンダー 1 か月分を `mini_cal.html` に切り出し、週間表示
（`main.html`）と月間表示（`month.html`）の両方から `{% include %}`
する。日付セルと caption の `data-action` は、呼び出し側が
`{% set %}` した変数で決める（`sde.html` と同じ流儀）。

`month.html` は、`.my-week-viewport` / `#week_wrap` / `.my-week-panel`
を週間表示と**同じクラス・id で使い回す**。パネルの並べ直しと横滑り
（`layoutWeeks()` / `slideWeekWrap()` / `setActiveWeek()`）を、週も月も
同じ仕組みでそのまま使うため。

### ブラウザ側

月間表示だけの処理を `month.js`（新規）に置いた。
`setActiveBlockOfDate()` と `moveActiveBlock()`（`moveToMonday()` の
月版）の 2 つ。

既存のファイルへ足した分岐は 5 か所だけ。`window.ytsched.view_month`
（`main-page.js` の `onloadHdr()` が `#main` の `data-view` から入れる）
を見る。

| 場所 | 月間表示のときの動き |
|------|----------------------|
| `week.js` `moveActiveDate()` | `moveActiveBlock()` を呼ぶ |
| `week.js` `weekOffsetOfDate()` | null を返す（`data-monday` の取り違え防止） |
| `nav.js` `scrollToDate()` | その日を含むブロックへ移る |
| `nav.js` `popstateHdr()` | 同上。移れなければ読み直す |
| `swipe.js` `swipeMiniCal`（2 か所） | 立てない |

**フッターの ＜ ＞・キーの ← →・スワイプ・自動ページ送りは、どれも
`moveActiveDate()` を通っている。** そのため、そこ 1 か所で分けるだけで
全部が 6 ヶ月単位になり、呼び出し元をひとつも書き換えずに済んだ。

`swipeMiniCal`（TODO-136 の、ミニカレンダーの上での 1 ヶ月送り）を
月間表示で立てないのは、月間表示では画面全体がミニカレンダーなので、
そのままだと 6 ヶ月送りではなく 1 ヶ月送りになってしまうため。

### CSS

`.my-month-grid` を `grid-template-columns: 1fr 1fr` で 2 列にした。
`.my-mini-cal` は既定が `flex: 1 1 0`（横に 2 つ並べる前提）で grid の
中では効かないので、`width: 100%` を足した。色・大きさは既存の
ミニカレンダーのものをそのまま使い、新しくは作っていない。

## テスト

- `tests/test_main_handler.py` — ブロックの先頭月が 1 月か 7 月になること
  （境界の 6/30・7/1・12/31・1/1）、3 ブロック並ぶこと、`base_date`
  の決め方、年をまたぐこと
- `tests/test_web.py` — `view=month` が 3 ブロックと 6 ヶ月ぶんの
  caption を出すこと、検索中は週間表示になること、`view` に不正な値を
  渡しても週間表示になること
- `tests/test_browser.py` — 週間表示の `YYYY/MM` を押して月間表示になり、
  日付を押してその日を含む週の週間表示に戻ること
- `uv run pytest tests` は 569 件成功。`mise run lint` も通る
- verifier が playwright で実際に操作し、6 ヶ月移動でページの読み直しが
  起きないこと（先読みが効いていること）、既存の週送り・
  ミニカレンダーの 1 ヶ月送り・検索が壊れていないことを確かめた
- reviewer の指摘は無し

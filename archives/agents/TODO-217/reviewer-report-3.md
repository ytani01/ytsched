# TODO-217 reviewer の報告（3 回目）

対象: 2 回目のあとに直した分（`week.js` の `isSliding()` / `cancelSlide()` /
`finishSlide()`、`setActiveWeek()` の先頭、`nav.js` の `scrollToDate()` /
`popstateHdr()`、`swipe.js` の `swipeDragTo()`、`main-page.js` のダブルタップ、
`gauge.js` の `followGauge()`）。動作は実測していない。

## 要修正

無し。

## 検討

### 1. ダブルタップの `cancelSlide()` で、元のページの `transform` とクラスが流した先のまま残る

- 場所: `main-page.js` の `homeButtonHdr()` のダブルタップの分岐
  （`ytsched.cancelSlide(); reloadHome(monday_str);`）と、`week.js` の
  `cancelSlide()`
- 内容: `cancelSlide()` は `transform` を戻さない（コメントのとおり、
  戻すのは `setActiveWeek()` かページの読み直し）。ダブルタップでは、
  読み直しが戻す役になる。ただ、元のページの DOM には次の状態が残る。
  - `transition` のクラスが外れるので、`#week_wrap` は
    `translateX(-rel * win_w)` へその場で飛ぶ。画面には今日の週が映る
  - `my-week-wrap-dragging` と、中間の週の `my-week-near` は付いたまま
  - `activeWeekOffset` / `activeMonday` / URL は流す前の週のまま
  - 針は、追従が止まった途中の位置にある
- 起きる条件: 今日の週以外（今日の週が DOM にある）からホームをダブルタップし、
  読み直したページで「戻る」を押したとき。元のページが bfcache から
  そのまま戻ると、上の食い違った状態で出る。
  - `spinner.js` に `pageshow` の `persisted` の後始末があるので、
    このアプリで bfcache の復元は起きうる
  - `beforeunload` は登録されているが、`unload` は無い
  - 戻ったあと ←→ を押すと、`moveToMonday()` は元の週 + 1 を行き先にする。
    今の `transform`（今日の週の位置）から元の週の隣へ滑って戻る、
    という動きになる
  - 読み直しの応答が来る前に何も押さない限り、見えるのは「その場で今日の週へ飛ぶ」だけ
- 実害は未確認（bfcache に入るかどうか、ブラウザごとの違いも確かめていない）。
  直す前の版（`on_done` が走る版）と TODO-217 より前（1 回目のタップで
  同期で移る）では、元のページの状態は揃っていた

## 好みの範囲

### 2. `finishSlide()` の呼び出しで、ミニカレンダーの上のスワイプでも走っている分が済む

- 場所: `swipe.js` の `swipeDragTo()`。`finishSlide()` は、
  `swipeMiniCal` と検索モードの場合も含めて、追従を始めるたびに呼ばれる
- 内容: 週を追従させない経路（ミニカレンダーの月送り）でも、
  流している分を前倒しで済ませる。そのあと `moveActiveMonth()` は
  `activeMonday`（済ませた先の週）から月を数えるので、結果は
  「流し終えてから月送り」と同じ。困る経路は見つからなかった。
  検索モードでは `slideWeekWrap()` がその場で `on_done` を呼ぶので、
  走っている分が無く、何も起きない

## 問題が無かった観点

- **`finishSlide()` が ←→・スワイプ自身の分に効く経路:** 困るものは
  見つからなかった
  - `cancelSwipeDrag()` で 0 へ戻している途中に次のドラッグを始めたとき:
    `on_done` が `transform = ""` にし、`my-week-wrap-dragging` を外す。
    そのあと `swipeDragTo()` が `my-week-wrap-dragging` を付け直し、
    `translateX(dx)` を掛ける。前の版では、`.my-week-wrap-sliding` が付いた
    まま追従が始まり、300ms 後の `on_done` がドラッグの途中で
    `transform` と `my-week-wrap-dragging` を外していた。今回で直った側に入る
  - ←→・スワイプの送り（`moveToMonday()` / `moveActiveBlock()`）の途中で
    続けて払ったとき: 前の分の `on_done`（`setActiveWeek(next)`）が済んで
    から、新しい週を起点に追従が始まる。前の分は落ちない。
    `on_done` が `doGet()` になるとき（読み込んだ範囲の外）は、読み直しが
    最大 300ms 早く始まるだけ
  - 再入: `finish()` は `cancelActiveSlide` / `finishActiveSlide` を
    `on_done()` より先に null にする。そのため `on_done` の中の
    `setActiveWeek()` → `cancelSlide()` は何もしない。どの `on_done` も
    `slideWeekWrap()` を呼ばないので、`finishSlide()` のあとに新しい分が
    走り出すことも無い
  - `swipeDragTo()` での位置: `finishSlide()` は `swipeDragging = true`
    より前、`translateX(dx)` を掛ける前に呼ばれるので、指の位置は
    済ませた先の週を起点に掛かる
- **`cancelSlide()` のあと `transform` が戻らない経路:** 呼び出し元は 2 つ。
  - `setActiveWeek()`: 直後に `transform = ""`、`SLIDE_CLASSES`、
    `my-week-wrap-dragging` を外すので、残らない
  - ダブルタップ: 上の 1 だけ
  - `slideWeekWrap()` の先頭の取り消しは前からある形で、新しい分が
    `transform` を掛け直す。取り消した分の `finishActiveSlide` は、
    同じ呼び出しの中で新しい `finish` に差し替わる
- `nav.js` の `isSliding()` の条件: `finish()` の中から呼ばれる
  `scrollToDate()`（ホームの `on_done`）では、もう `isSliding()` が false
  なので、余計に `setActiveWeek()` を通ることは無い。滑らせている途中に
  同じ週へ移るときは、`setActiveWeek(offset, false)` が取り消しと元の位置
  への戻しを両方する。`cancelSwipeDrag()` の 0 へ戻す途中なら、その
  `on_done` と同じ後始末になる。
  月間表示は `setActiveBlockOfDate()` → `setActiveWeek()` を必ず通るので、
  同じ条件は要らない
- `followGauge()` の順番の入れ替え: ドラッグ中は `null` でも
  `transition` を戻さない。戻すのはドラッグの側（`gaugeBarPointerUpHdr()` /
  `gaugeBarPointerCancelHdr()`、ボタンが離れていた場合の
  `gaugeBarPointerMoveHdr()`）で、どれも `setGaugeNoTransition(false)` を
  呼ぶ。ドラッグが流し終えるより先に終わった場合は、そのあとの
  `follow()` がまた付け、流し終えたときの `followGauge(null)` が外す。
  付いたまま残る経路は無い
- 依存関係コメント: `week.js` / `nav.js` / `swipe.js` / `main-page.js` の
  冒頭に、足した関数が載っている

## 作り込みすぎ

作り込みすぎ: なし。`isSliding()` は `cancelActiveSlide !== null` の 1 行だが、
`cancelActiveSlide` を week.js の外へ出さないために要る。

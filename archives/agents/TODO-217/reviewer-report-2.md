# TODO-217 reviewer の報告（2 回目）

対象: 1 回目のあとに足した分（`git diff -- src` のうち、`week.js` の
`setActiveWeek()` の取り消し、ループの範囲、`HOME_SLIDE_MSEC = 1000`、
`homeFollowId` と針の追従、`gauge.js` の `followGauge()`、`my.css` の 1s）。
動作の実測はしていない。

## 前回の指摘の扱い

- 1（行き先の週が見えない）: 直っている。`i !== rel + step` で、
  `rel=3` なら 1, 2, 3 に付く
- 2（直に移ったときに `on_done` が上書きする）: `setActiveWeek()` が
  呼ばれる経路は直っている。呼ばれない経路が残る（下の 2）
- 3（流す経路のテストが無い）: `tests/` に変更が無く、まだ無い
- 4・5・6・7: 変わっていない（4 の `slideWeekWrap()` /
  `weekOffsetOfDate()` の行も前のまま）

## 要修正

無し。

## 検討

### 1. ゲージをドラッグしている途中で流し終えると、針の `.my-gauge-r-no-transition` が外れる

- 場所: `week.js` の `slideToWeekOfDate()` の `follow()` の止める分岐と
  `on_done` の `ytsched.followGauge(null)`。`gauge.js` の
  `followGauge()` の `if (!date_str)` の分岐
- 内容: `followGauge()` がドラッグ中（`gaugeBarDragStart`）に針へ
  触らないのは、値を渡したときだけ。`null` を渡したときは、ドラッグ中でも
  `setGaugeNoTransition(false)` を呼ぶ。ドラッグを始めたとき
  （`gaugeBarPointerDownHdr()`）に付けた `.my-gauge-r-no-transition` が、
  ドラッグの途中で外れる。外れたあとは、`pointermove` の
  `setGaugeNeedles()` に 0.3s の transition が掛かり、針が指から遅れる。
  離せば `gaugeBarPointerUpHdr()` が外すので、外れたまま残ることは無い
- 起きる条件: ホームの単押し・Home のあと、流している 1 秒の間に
  ゲージのドラッグを始め、指を離す前に次のどれかが起きたとき。
  (a) 流し終える（`on_done`）、(b) ドラッグの一定時間の追従
  （`startGaugeBarFollowTimer()` → `scrollToDate()` → `setActiveWeek()`）で
  流す分が取り消され、次のフレームの `follow()` が止める分岐に入る。
  (a) では、ドラッグの途中で週が今日の週へ移る（`dispGauge()` はドラッグ中
  なので針には触らない）。実害は未確認

### 2. 移り先がいまの週と同じだと、`setActiveWeek()` を通らないので取り消されない

- 場所: `nav.js` の `scrollToDate()` と `popstateHdr()` の
  `offset !== ytsched.ytState.activeWeekOffset` の条件
- 内容: 流している間、`activeWeekOffset` は流し始める前の週のまま
  （`on_done` まで変わらない）。だから、流し始める前の週へのゲージの
  クリック、ミニカレンダー、戻る/進むは `setActiveWeek()` を呼ばず、
  取り消しも起きない。1 秒後に `on_done` → `scrollToDate(今日)` が走り、
  利用者が選んだ先を上書きして履歴を積む。前回の 2 と同じ形で、
  `setActiveWeek()` での取り消しだけでは、この経路が抜ける。
  流している間は、画面では行き先の週へほぼ移って見えるので、元の週を
  選ぶことはありうる
- 起きる条件: 流している 1 秒の間に、流し始める前の週の日付へ移る
  操作をしたとき。実害は未確認

### 3. 流している間にスワイプを始めると、指への追従に 1 秒の ease が掛かり、途中で位置が飛ぶ

- 場所: `swipe.js` の `swipeDragTo()`（`slideWeekWrap()` も
  `setActiveWeek()` も通らない）
- 内容: 前回の 2 で挙げた形のうち、スワイプの分は今回の変更でも
  変わらない。`.my-week-wrap-homing` が付いたまま `translateX(dx)` が
  掛かるので、追従が 1s の cubic-bezier で遅れる。そのあと `transitionend`
  か `msec + 100` のタイマーで `finish()` → `on_done` → `setActiveWeek()`
  が走り、ドラッグの途中で `transform` と `my-week-wrap-dragging` が外れる。
  流す時間を 1 秒にしたので、起きうる時間は前回の 450ms から 1.1 秒に延びた。
  `follow()` は `-x / win_w` で指の位置も週として読むので、追従している間は
  針も指につられて動く
- 起きる条件: ホームの単押し・Home のあと 1.1 秒以内に、週の上で横に
  スワイプ・ドラッグを始めたとき。実害は未確認

## 好みの範囲

### 4. `slideToWeekOfDate()` の JSDoc が `let homeFollowId` の上にある

- 場所: `week.js`。JSDoc（`@param date_str` / `on_done`）のすぐ下が
  `let homeFollowId = 0;` で、関数はその後ろにある。
  JSDoc を読む道具やエディタは、`homeFollowId` の説明として扱う。
  `let` を JSDoc の上へ移せば解ける

### 5. 依存関係コメントの抜け

- `gauge.js` 冒頭の「外から使うもの」で、`calcDays() (nav.js) -- setGaugePosition`
  に `followGauge` が抜けている（`getLocaltimeDateString` / `mondayOf` の行も、
  もしあれば同様）。`nav.js` の `calcDays() -- gauge.js (setGaugePosition)` も同じ
- `week.js` 冒頭: `followGauge()` の行は合っている。
  `slideWeekWrap()` / `weekOffsetOfDate()` の行は前回の 4 のまま

## 問題が無かった観点

- **rAF が回り続ける経路:** 見つからなかった。`follow()` が回り続けるのは、
  `.my-week-wrap-homing` が付いていて、`follow_id` も変わっていない間だけ。
  `.my-week-wrap-homing` は、`finish()`・`setActiveWeek()`・次の
  `slideWeekWrap()` のどれかで必ず外れる。`finish()` はタイマーで必ず
  来るので、`transitionend` が来ない場合も止まる。
  `hasAdjacentWeek()` が false で `on_done` がその場で呼ばれる場合は、
  先に `homeFollowId` が進んで、最初のフレームで止まる。
  タブが隠れて rAF が止まっても、戻ったときの最初のフレームで止まる
- **`.my-gauge-r-no-transition` が付いたまま残る経路:** 見つからなかった。
  付けるのは `followGauge()` に値を渡したときだけで、追従の止め方は
  どれも `followGauge(null)` を通る。外れるのが早すぎる経路は上の 1。
  - 次の `slideToWeekOfDate()` が来たとき: 同じフレームで、古い
    `follow()`（外す）、新しい `follow()`（付ける）の順に走るので、
    付いたまま続く
  - ダブルタップ: 2 回目の `reloadHome()` でページが入れ替わるまで追従が
    続き、残ったとしても読み直しで消える
- **ラベルの丸めの向き:** 合っている。`target_x = -rel * win_w` なので
  `weeks = -x / win_w` は `rel` と同じ符号で、`calcDays(this_monday,
  cur_monday) + weeks * 7` は今日の週に近づく向きに変わる。
  `Math.round(rel_days / 7) * 7` は近いほうの週に丸める
  （.5 ちょうどは +∞ 側。`-2.5 → -2`）。`-0` になっても
  `days === 0` で `±0` が出る
- **`setActiveWeek()` の先頭の取り消しで `on_done` が落ちるか:** 落ちない。
  `finish()` は `cancelActiveSlide = null` を `on_done()` より先に
  済ませる。そのため、←→（`moveToMonday`）・`moveActiveBlock`・
  ホームの `on_done` が呼ぶ `setActiveWeek()` は、自分を取り消さない。
  `cancelSwipeDrag()` の `on_done` は `setActiveWeek()` を呼ばない。
  取り消されるのは、滑らせている途中に別の経路（ゲージ・戻る/進む・
  ミニカレンダー）から `setActiveWeek()` が呼ばれたときだけで、
  これは狙いどおり。取り消された側の後始末（`transform`、`SLIDE_CLASSES`、
  `my-week-wrap-dragging`）は `setActiveWeek()` 自身がする。
  `panel` が無くて `false` を返すときは、取り消しより前で返るので、
  滑らせている分は続く
- 流し終えたときの針: `followGauge(null)` で transition を戻してから、
  `setActiveWeek()` → `dispGauge()` が最後の位置を書く。直前のフレームで
  ほぼ行き先にいるので、残りの短い距離にだけ transition が掛かる
- `HOME_SLIDE_MSEC = 1000` と `my.css` の `1s` は合っている

## 確信度の低いもの

### 6. ダブルタップの `pushState` が、ほぼ必ず遷移の途中に来る（前回の 6 が強まった、実害は未確認）

- 流す時間が 1 秒になったので、ダブルタップ（350ms 以内）の 2 回目は
  必ず流している途中に来る。読み直しの応答が 1 回目のタップから
  約 1.1 秒より遅いと、`doPost()` の遷移を待っている間に、1 回目の
  `on_done` が `setActiveWeek()` と `history.pushState` を走らせる。
  これが遷移を取り消すかは確かめていない。verifier の実測に、
  「今日の週以外からダブルタップして読み直しが起きるか」と
  「サーバの応答を 1.5 秒ほど遅らせたとき」を足すと分かる

## 作り込みすぎ

作り込みすぎ: なし。`homeFollowId` と `.my-week-wrap-homing` の 2 つで止める
のは冗長に見えるが、片方は次の `slideToWeekOfDate()`、もう片方は
`setActiveWeek()` と他の `slideWeekWrap()` を受け持っていて、どちらも要る。

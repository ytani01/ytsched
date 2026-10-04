# TODO-217 reviewer の報告

対象: `git diff -- src`（`week.js` / `main-page.js` / `keyboard.js` / `my.css`）。
動作の実測はしていない（verifier の担当）。ループの範囲だけ `node` で確かめた。

## 要修正

### 1. 行き先の週が流している間ずっと見えない（`|rel| >= 2` のとき）

- 場所: `week.js` の `slideToWeekOfDate()`、`for (let i = step; i !== rel; i += step)`
- 内容: ループが `i === rel`（行き先の週）の手前で止まるので、行き先の週には
  `my-week-near` が付かない。`layoutWeeks()` が `my-week-near` を付けるのは
  `|rel| === 1` の週だけで、`.my-week-panel` の既定は `display: none` /
  `visibility: hidden`。このため行き先の週は、流している間は描かれない。
  `node` で確かめたループの範囲: `rel=3 → [1,2]`、`rel=-3 → [-1,-2]`、
  `rel=2 → [1]`。
- 起きる条件: 今日の週が DOM にあり、いまの週から 2 週以上離れているとき
  （ホームボタンの単押し・キーの Home）。強めの ease-out なので、最初のほうで
  ほぼ行き先まで動き、残りの時間は空白の枠が見える。`on_done` →
  `scrollToDate()` → `setActiveWeek()` で `my-week-cur` が付いて、初めて
  中身が出る。`rel = ±1` のときは `layoutWeeks()` が付けた `my-week-near`
  があるので起きない。

## 検討

### 2. `slideWeekWrap()` を通らない操作が重なると、450ms 後に今日の週へ引き戻される

- 場所: `week.js` の `slideWeekWrap()`（タイマー `msec + 100`）と、
  `setActiveWeek()` / `swipe.js` の `swipeDragTo()`
- 内容: 流している途中の取り消しは、次の `slideWeekWrap()` の先頭でしか
  行わない。ゲージのクリック（`gauge.js` → `scrollToDate()`）、戻る/進む
  （`popstateHdr()`）、ミニカレンダーでの月送り（`moveActiveMonth()` →
  `scrollToDate()`）は `setActiveWeek()` を直に呼ぶ。`setActiveWeek()` は
  `SLIDE_CLASSES` と `transform` を外すが `cancelActiveSlide` は呼ばない。
  transition が打ち切られて `transitionend` は来なくなり（`transitioncancel`
  になる）、残ったタイマーが `finish()` → `on_done` → `scrollToDate(今日)`
  を呼ぶ。利用者が選んだ週が、今日の週で上書きされ、履歴も 1 つ積まれる。
  スワイプの追従を始めた場合は、`.my-week-wrap-homing` が残ったまま
  `translateX(dx)` が掛かるので、指への追従が 0.35 秒の ease で遅れる。
  タイマーが来たところで `setActiveWeek()` が `transform` を外し、
  ドラッグの途中で位置が飛ぶ。
- 起きる条件: ホームの単押し・Home の直後、450ms 以内に上の操作をしたとき。
  ←→ の `moveToMonday()` にも前からある形（300ms）で、今回、窓が
  450ms に延び、Home の経路にも広がった。実害は未確認。
- 重なっても崩れない組み合わせ: ←→ やフッターの ◀▶（`moveToMonday()`）、
  `cancelSwipeDrag()`、もう一度のホーム・Home は `slideWeekWrap()` を
  通るので、前の分は取り消され、クラスは `SLIDE_CLASSES` で入れ替わる。
  この場合は後の操作が勝つ（既存の決まりどおり）。

### 3. 流す経路のテストが無い

- 場所: `tests/test_browser.py`
- 内容: 既存の `test_home_button_moves_the_view` は、今日が DOM に無い
  状態（読み直し）から始める。`test_home_button_keeps_today_in_view` は
  今日の週から始めるので `rel = 0`。今回足した「DOM の中で流す」経路は、
  どのテストも通らない。今日の 2〜3 週前を開いてホームを押し、次を
  確かめるテストが 1 本あると、`on_done` が呼ばれないときや、クラス・
  `transform` が残るときに落ちる。
  - 終わったあと: 今日の週が `my-week-cur`。`#week_wrap` に
    `my-week-wrap-homing` / `my-week-wrap-dragging` が残らず、
    `style.transform` は空。`my-week-near` は ±1 の週だけに付いている
  - 流している途中: 行き先の週が `display: none` でない（1 の検出用）

## 好みの範囲

### 4. `week.js` 冒頭の依存関係コメントが一部古い

- `weekOffsetOfDate() -- nav.js (popstateHdr / scrollToDate)` に、
  このファイルの `slideToWeekOfDate` が足りない（`moveToMonday()` の行は
  「(このファイル)」も書く形）
- `slideWeekWrap() -- swipe.js (cancelSwipeDrag)` に、`slideToWeekOfDate`・
  `moveToMonday`（このファイル）と `month.js (moveActiveBlock)` が足りない。
  後ろの 2 つは今回より前から抜けていた
- `main-page.js` / `keyboard.js` の冒頭と `nav.js` の `scrollToDate()` の行は合っている

### 5. `my-week-near` が中間の週に残る経路がある（実害なし）

- 場所: `slideToWeekOfDate()` のコメント「流し終えたあとの
  `setActiveWeek()` の `layoutWeeks()` が付け直す」
- 起きる条件: 流している途中でスワイプを始め、送らずに離すと
  （`cancelSwipeDrag()`）、流す分が取り消される。この経路の `on_done` は
  `layoutWeeks()` を呼ばないので、中間の週の `my-week-near` が残る。
  `my-week-wrap-dragging` が外れて見えなくなり、残った週も ±2 週より外に
  あるので、次の `setActiveWeek()` までは目に見える影響は無いと読んだ。
  コメントは「`on_done` が呼ばれれば」と読める書き方のほうが正確。

## 問題が無かった観点

- `slideToWeekOfDate()` の分岐: `weekOffsetOfDate()` が null（DOM に無い・
  月間表示）でも、`rel === 0` でも、すぐ `on_done` を呼び、今までどおり
  `scrollToDate()` に任せる。検索モードは週パネルが 1 枚なので、`rel` は
  必ず 0。仮に 0 でなくても `hasAdjacentWeek()` が false で、すぐ `on_done`
  になる。検索画面のホームボタンは、この関数より前で `return` している。
  ダブルタップは `reloadHome()` へ行き、流さない
- 既存の呼び出し（`cancelSwipeDrag` / `moveToMonday` / `moveActiveBlock`）:
  既定の値は `"my-week-wrap-sliding"` / 200 で、タイマーは今までどおり
  300ms。`remove(...SLIDE_CLASSES)` → `add(同じクラス)` は同じタスクの中なので、
  スタイルは変わらない。`finish()` で外すクラスも今までどおり
- `setActiveWeek()` で外すクラスを `SLIDE_CLASSES` にした点: 流し終えた
  ときも、取り消されたときも、どちらのクラスも残らない
- Home キーの押しっぱなし（キーの自動リピート）: `activeWeekOffset` は
  変わらないので、`rel` も行き先も同じ。走っている transition がそのまま
  続き、最後の呼び出しの `onEnd` で終わる

## 確信度の低いもの

### 6. ダブルタップの 2 回目のあとに `pushState` が走る（実害は未確認）

- 場所: `main-page.js` の `homeButtonHdr()` の単押しの分岐
- 内容: 前は 1 回目のタップで `scrollToDate()` が同期で終わっていた。
  今は 350ms 流してから呼ぶので、350ms 以内の 2 回目で `reloadHome()`
  （`doPost()` の form submit）が始まったあとに、1 回目の `on_done` →
  `setActiveWeek()` / `pushDateInUrl()`（`history.pushState`）が走る。
  遷移を待っている間の `pushState` が、ブラウザによってはその遷移を
  取り消すかもしれない。取り消されると、ダブルタップの読み直しが
  黙って起きない。仕様とブラウザの実装は確かめていない
- 起きる条件: いまの週が今日の週ではなく、今日の週が DOM にある状態で、
  ホームをダブルタップしたとき。verifier の実測に「ダブルタップで
  読み直しが起きるか（今日の週以外から）」を足すと分かる

### 7. 流している間、文書の縦の長さが伸びるかもしれない（実害は未確認）

- `my.css` のコメントにあるとおり、絶対位置の週も縦にはみ出した分だけ
  スクロールを伸ばす。今回は中間の週を全部 `display: flow-root` にするので、
  流している間は、間にある週のうち一番背の高い週の分まで文書が伸びる。
  縦のスクロールバーが一瞬出入りして、`clientWidth` や見た目がずれるかは
  測っていない。`|rel|` が大きいときは、表示する週も多くなる

## 作り込みすぎ

作り込みすぎ: なし（`slide_class` / `msec` の引数、`SLIDE_CLASSES` は
どちらも 2 か所以上で使われていて、ほかに短い書き方が無い）。

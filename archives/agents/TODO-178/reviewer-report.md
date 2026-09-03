# TODO-178 レビュー報告（reviewer）

## 確信度の高い指摘

### 1. 履歴の push/replace のタイミングが設計書と食い違う

- `src/ytsched/webroot/static/js/gauge.js` の `startGaugeBarFollowTimer()`
  と `gaugeBarPointerUpHdr()`
- 設計（`archives/agents/TODO-178/README.md` 3節）は「1 秒ごとの追従は
  `push_flag` を **常に false**（replace）」「指を離したときは
  **常に true**（push）」としている。
- 実装は逆で、**ドラッグ中に最初に発火した追従が push（履歴を1つ積む）**
  になり、それ以降の追従・指を離したときは `gaugeBarHistoryPushed` を
  見て replace になる（`push_flag = !gaugeBarHistoryPushed`）。
- 追加したテスト `test_gauge_drag_follow_does_not_push_history` の名前と
  docstring は「1 秒後の追従では履歴が積まれない（`replaceState` なので
  戻ると元の画面へ一度で戻れる）」と書いてあるが、実装では**最初の追従で
  push が起きている**。テストは「`go_back()` で1回戻れば元の週に戻る」と
  いう結果だけを見ていて、push がどのタイミングで起きたかは確かめていない
  ため、この食い違いに気づかない作りになっている。
- 「ドラッグ 1 回で履歴が 1 つだけ増える」という結果自体は実装でも
  設計どおりでも同じになるが、**push が起きる瞬間が違う**
  （実装は「最初の 1 秒経過時点」、設計は「指を離した時点」）。たとえば
  最初の追従が起きた直後、指を離す前にブラウザの戻る操作をした場合の
  挙動が設計と実装で変わる。狙った動きかどうか、main の判断が要る。

### 2. `hasBlockOfDate()` が `setActiveBlockOfDate()` から切り出されていない

- `src/ytsched/webroot/static/js/month.js`
- 設計は「`hasBlockOfDate()` は `setActiveBlockOfDate()` の前半（パネルの
  探し方）と同じなので、そこから切り出す」と指示している。
- 実装は切り出さず、`blockKeyOfDate()` → `elWeekWrap.querySelector(...)`
  の 2 行をそのまま `hasBlockOfDate()` にコピーしている。
  `setActiveBlockOfDate()` の冒頭と完全に重複したコードが並んでいる。
  設計からの逸脱であり、既存ロジックの再実装（重複）にあたる。

### 3. `gauge.js` 冒頭コメントの「外から使うもの」に実態と合わない行がある

- `src/ytsched/webroot/static/js/gauge.js` 29 行目
  `setActiveBlockOfDate() (month.js) -- gaugeBarPointerMoveHdr (月間表示での追従判定)`
  とあるが、`gaugeBarPointerMoveHdr` が実際に呼んでいるのは新設の
  `hasBlockOfDate()` だけで、`setActiveBlockOfDate()` はこのファイルの
  どこからも呼ばれていない。書き漏れ（コピペ後の消し忘れ）と思われる。

## 確信度が中程度の指摘

### 4. `pointerId` を見ておらず、ドラッグ中に別の指が触れると状態が上書きされる

- `gaugeBarPointerDownHdr` / `gaugeBarPointerMoveHdr` / `gaugeBarPointerUpHdr`
  はどれも `event.pointerId` を見ていない。1本目の指でドラッグ中に
  2本目の指が `.my-gauge-bar` の上に触れると、`gaugeBarPointerDownHdr` が
  再度発火し、`gaugeBarDragStart` / `gaugeBarDragMonday` が
  2 本目の指の位置で上書きされる。以降 `pointermove` / `pointerup` は
  どちらの指の分でも同じ状態を触るため、意図しない位置へ動く可能性がある。
- 既存の `pageTurnPointerDownHdr` などページ送り関連も `pointerId` を
  見ておらず、パターンとしては一貫している。ただしページ送りボタンは
  小さく複数指が同時に乗りにくいのに対し、帯は横に広く、依頼文にある
  「押している途中で別の指が触れた」場面が起きやすい。

### 5. `gaugeBarPointerDownHdr` が右クリックでも無条件に `preventDefault()` する

- `event.button` のチェックが無いため、右ボタンでの `pointerdown` でも
  ドラッグ状態に入り、`event.preventDefault()` が効いてコンテキスト
  メニューを抑制する可能性がある。既存の `pageTurnPointerDownHdr` には
  この `preventDefault()` 呼び出しは無い。実害は小さいと思われる
  （ゲージをマウス右クリックで触る操作は想定しにくい）。

## 指摘なし・確認した点

- `swipe.js` の `mouseDownHdr()` が `.my-gauge-bar` の上で
  `stopPropagation()` を呼ばずに戻る変更は、既存の `[data-page-turn]`
  と同じ並びで一貫しており、コメントの理由づけも妥当。
- `pointerdown` の window 登録が `mousedown` の登録より後にあるが、
  ブラウザは `pointerdown` を先に実イベントとして発火するので、
  リスナーの登録順（capture）は問題にならない。
- `pointercancel` で `dispGauge(ytState.activeMonday)` を呼ぶ実装は、
  すでに追従（`scrollToDate`）が起きていれば `activeMonday` も
  追従先に更新されているため、画面と針がずれることはない。
- `.my-gauge-bar` の高さ変更・`touch-action: none` は設計どおり。
- `test_gauge_drag_does_not_move_screen_while_dragging` /
  `test_gauge_drag_follows_after_1_second_stop` /
  `test_gauge_tap_moves_to_the_tapped_week` は、狙った動きを実際に
  確かめている（空振りのテストではない）。

# TODO-178 の分担

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort high | implementer + verifier + reviewer |

- **implementer**: 設計（下記）にそって `gauge.js` / `swipe.js` / `month.js` /
  `main-page.js` / `main.html` / `my.css` を直し、ブラウザテストを足す。
  4 ファイル以上にまたがり、既存のスワイプ・タップの経路と噛み合わせる
  必要があるので、main とは分けた
- **verifier**: `mise run lint` / `test` を走らせ、実際にアプリを起動して
  ドラッグと 1 秒後の追従を確かめる。実装した本人には確かめさせない
- **reviewer**: ゲージの操作の挙動そのものが変わるので入れる
  （`~/.claude/CLAUDE.md` の「挙動や分岐が変わる項目には入れる」）

報告は `implementer-report.md` / `verifier-report.md` / `reviewer-report.md`。

---

## 設計（main が決めた）

### 1. タップとドラッグを、どちらも pointer イベントで扱う

いまの帯は `data-action="gauge-click"` を持ち、`swipe.js` の
`mouseDownHdr()` / `mouseUpHdr()` が「動かずに離したらクリック」と判定して
`gaugeBarClickHdr()` を呼んでいる（TODO-074）。ドラッグを足すと、この経路は
週送りのスワイプと二重に効くので、**帯の上だけ pointer イベントに寄せる**。

- `main.html`: `.my-gauge-bar` から `data-action="gauge-click"` を外す
- `main-page.js`: `actionMouseDownHdr()` の `case "gauge-click"` を消す
- `swipe.js`: `touchStartHdr()` と `mouseDownHdr()` の見送りセレクタ
  （いまの `input, textarea, select, [data-page-turn]` /
  `input, textarea, select, label, a, [data-page-turn]`）に
  `.my-gauge-bar` を足す。帯の上で始めた横の動きを週送りとして
  拾わせないため。理由をコメントに残すこと
- `gauge.js`: `gaugeBarClickHdr()` を、pointer の
  down / move / up / cancel の 4 つに置き換える。ページ送りボタン
  （TODO-084、`main-page.js` の `pageTurnPointerDownHdr()` など）と同じく
  **window への委譲**にし、`setPointerCapture()` は使わない。
  ハンドラの本体は `gauge.js` に置いて `window.ytsched` へ出し、
  `window.addEventListener()` は `main-page.js` の既存の登録のところへ足す
  （`pointerdown` は capture）
- 動かさずに離したときは、いままでと同じくその位置の週へ移る。
  「動いていてもクリックと見なす」（`mouseUpHdr()` の割り切り）は、
  ドラッグがある帯では要らない

### 2. ドラッグ中は針とラベルだけを動かす

- `pointerdown` が `.my-gauge-bar` の上なら、ドラッグの状態を持つ
- `pointermove` で `clientX` から週を出し、針を置く。
  位置の計算は、いまの `gaugeBarClickHdr()` の中身
  （`getBoundingClientRect()` → `xPercent2days()` → 今週の月曜から
  `shiftDays()` → `mondayOf()`）をそのまま関数に切り出して、
  down / move / up で使い回す
- ドラッグ中は `.my-gauge-r` の `transition`（0.3s）が効くと指に遅れて
  付いてくるので、ドラッグの間は `my-gauge-r-no-transition` を付けたままに
  する。離したら外す
- ドラッグ中に `dispGauge()` が呼ばれると（追従で `setActiveWeek()` を
  通るため）針が勝手に動く。**ドラッグ中の `dispGauge()` は針に触らない**
  ようにする（`sessionStorage` への記録だけ済ませて返す）

### 3. 1 秒止まったら、先読み済みの週にかぎり追従する

- `pointerdown` と `pointermove` のたびに `clearTimeout()` →
  `setTimeout(…, 1000)`。発火したら、そのときの週へ画面を移す。
  `pointerdown` でも張るのは、押したまま一度も動かさないと
  `pointermove` が来ず、いつまでも追従しないため
- **移り先が DOM にあるときだけ移る。** 週間表示は
  `weekOffsetOfDate(monday) !== null`、月間表示は `month.js` に
  `hasBlockOfDate(date_str)` を足して、それで見る
  （`.my-month-panel[data-block=...]` があるか。`setActiveBlockOfDate()` の
  前半と同じ探し方なので、そこから切り出す）。
  DOM に無いときは追従せず、針だけ動かし続ける
- 追従は `scrollToDate()` を `push_flag = !gaugeBarHistoryPushed` で呼ぶ。
  **最初の追従だけ push、以降は replace**。理由：push を常に false にすると
  始めた週の履歴が消えてしまい、戻ったときに元の画面へ帰れなくなる。
  push したら `gaugeBarHistoryPushed = true` を立てる。
  `behavior` を `"instant"` にするのは、追従中に smooth のスクロールが
  重ならないようにするため
- 指を離したときは、最後の週へ `scrollToDate()` を同じく
  `push_flag = !gaugeBarHistoryPushed` で呼ぶ。既に push していれば replace。
  DOM に無ければ `scrollToDate()` が `doGet()` で読み直す
- `pointercancel` では移らず、`dispGauge(ytState.activeMonday)` で針を
  いまの週へ戻す

### 4. 帯を高くする

- `.my-gauge-bar` の `height` を 33px から **44px** にする。
  中の要素（軸・今週のしるし・針・目盛りのラベル）の位置は変えず、
  余ったぶんは下の当たり判定にする
- タッチで縦にスクロールしないよう、`.my-gauge-bar` に
  `touch-action: none` を足す
- 週バーの高さは `main-page.js` の `onloadHdr()` が測って
  `body` の `padding-top` に入れているので、そちらの直しは要らない
  （確かめること）

### 5. テスト

`tests/test_browser.py` に足す。既存の `_tap()`（`page.mouse` で
`down` → `up`）と同じ書き方で、`page.mouse.move()` を挟む。

- ドラッグの途中では画面が動かず、針とラベルだけが動く
- 動きを 1 秒止めると、先読み済みの週へ画面が移る（URL の `date` が変わり、
  ページの読み直しは起きない）
- 追従では履歴が積まれない（`replaceState` なので、戻ると元の画面へ
  一度で戻れる）
- 動かさずに離したときは、いままでどおりその位置の週へ移る（TODO-074 の
  動きが残っている）

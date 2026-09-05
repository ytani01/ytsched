# TODO-184 reviewer 報告

対象: 作業ツリーの未コミットの変更（`git diff`）。
`src/ytsched/webroot/static/js/main-page.js`、`week.js`。

## 確信度が高い指摘

### 1. `setActiveWeek()` で `fillMainHeight()` を `scrollToId()` の後に呼んでいるため、`scrollToId()` の高さ判定が前の週の `minHeight` の影響を受ける

`week.js` の `setActiveWeek()`（185〜190行目）:

```js
ytsched.dispGauge(monday);
ytsched.scrollToId(`date-${monday}`, "top", "instant");

// 週の高さは .my-week-panel の切り替えで変わるので、そのたびに
// #main の高さも合わせ直す (TODO-184)
ytsched.fillMainHeight();
```

`scrollToId()`（`nav.js` 336〜342行目）は、その時点の `body.clientHeight` /
`documentElement.clientHeight` を比べて `body_h <= win_h` なら
「画面に収まっている」としてスクロールせず `true` を返す。この判定は
`fillMainHeight()` より**先**に行われるため、`#main` の `minHeight` が
直前の週の値のまま残った状態で行われる。

具体的には、前の週で `minHeight` が大きめにセット済み（例: 500px）の
状態から、それより短いが「本来なら画面に収まる」週（例: 実コンテンツ
420px、画面 450px）へ移ると、`minHeight` が残っているせいで
`body.clientHeight` が 500px 相当のまま計算され、`body_h <= win_h`
（450px）が偽になる。その結果 `scrollToId()` は「収まっていない」と
誤判定し、本来不要なスクロール（`scrollTo(...)`）を実行してしまう
可能性がある。

`fillMainHeight()`（`minHeight` のリセットを含む）を `scrollToId()` より
先に呼べば、この経路は無くなる。実機・ブラウザでは確認しておらず、
コードの読みからの推測（確信度は中程度、ただし実装依頼の中で名指しで
懸念されていた箇所でもある）。

## 確信度が中程度の指摘

### 2. `fillMainHeight()` に `ytsched.ytState.elMain` の null チェックが無い

`resize` / `orientationchange` は `main-page.js` 末尾で `window` に直接
登録される（691〜692行目）。`ytsched.ytState.elMain` は `onloadHdr()`
（`window` の `load` イベント）で初めてセットされる（311行目）ので、
それより前にこれらのイベントが発火すると `elMain` が `null` のまま
`fillMainHeight()` が呼ばれ、`ytsched.ytState.elMain.style.minHeight = ""`
で `TypeError` になる。

`resize` が `load` 前に発火することは通常考えにくいが、
`orientationchange` はページの読み込み中（画像待ちなどで `load` が
まだのとき）にユーザーが端末を回転させれば発火しうる。実害は、そのとき
一度コンソールに例外が出て高さ合わせがスキップされる程度で、他のイベント
ハンドラには波及しない（`addEventListener` のハンドラごとに独立して
例外処理されるため）。依頼の中で名指しされていた懸念点であり、対策
（null チェックや `onloadHdr` 完了後だけ登録する、など）は入っていない。

## 確信度が低い指摘（気になる程度）

### 3. `resize` に間引きが無い

モバイルでアドレスバーが出入りするたびに `resize` が飛ぶ想定がコメント
（688〜690行目）に書かれているが、`fillMainHeight()` 自体には
debounce・throttle が無く、素の `addEventListener` で毎回、
`minHeight` のリセット → `clientHeight` の読み取り → 再設定という
読み書きが走る。見た目が壊れるような実害は無さそうだが、頻度が高い
環境ではレイアウトの再計算が増える。

### 4. `onloadHdr()` の `body_h` / `win_h` の計算と `fillMainHeight()` 内の
再計算が二重

355〜356行目で計算した `body_h` / `win_h` は 371行目の分岐にだけ使われ、
`fillMainHeight()` 呼び出し（375行目）の中でまた同じものを計算し直す。
間（343〜370行目）に高さへ影響しそうな DOM 操作（`dispGaugeMarks()` など）
は見当たらず、二重計算による挙動の食い違いは確認できなかった。冗長という
程度。

## 確認できて問題が無かった点

- `moveActiveMonth()`（週間表示のミニカレンダーの月移動）・
  `moveActiveBlock()`（月間表示のブロック送り）・`setActiveBlockOfDate()`
  （月間表示、`popstateHdr` 経由も含む）は、いずれも最終的に
  `week.js` の `setActiveWeek()` を経由するので `fillMainHeight()` が
  呼ばれる。検索モードは週送りのたびにページを読み直す
  （`doGet()`／`moveActiveDate()` の検索分岐）ので `onloadHdr()` 経由で
  カバーされる。依頼で挙げられていた経路のうち、これらは漏れていない
- ファイル冒頭コメント（外へ出すもの・外から使うもの）の書き方は、
  既存の他の項目のパターンと大きくは外れていない
- `fillMainHeight()` 自体のロジック（`fill_h` の式、短くないときに
  `minHeight` を空のままにする点）は、`onloadHdr()` にあった元の式を
  そのまま切り出したもので、変更は無い

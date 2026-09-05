# TODO-184 実装依頼（implementer）

## 目的

一覧画面（main.html）で、週送りのあとや画面の高さが変わったあとに、
フッターとの間へ `body` の白が残ることがある。これを、そのたびに
高さを合わせ直すことで直す。

## いまの作り

- 一覧の地の色 `--my-cal-ground` は `#main` にだけ付く（`src/ytsched/webroot/static/css/my.css:186`）。
  `body` は白（同 78 行目）
- 中身が画面より短いときに白が残らないよう、`main-page.js` の `onloadHdr()` が
  `#main` の `minHeight` を計算して伸ばす
  （`src/ytsched/webroot/static/js/main-page.js:331-359` あたり）
- これが読み込み時に一度しか走らず、しかも `body_h < win_h` のときだけ走る。
  週の高さは `.my-week-panel` の切り替えで変わる（通常フローに居るのは今の週だけ）
  ので、読み込み時に予定の多い週を見ていると `minHeight` が付かず、
  そこから予定の少ない週へ送ったときに白が残る

## やること

1. `onloadHdr()` の中の高さ合わせを関数へ切り出す。名前は
   `window.ytsched.fillMainHeight()`（main-page.js に置き、外へ出す）。
   ファイル冒頭のコメント（「外へ出すもの」「外から使うもの」）も、
   このファイルの書き方に合わせて直すこと
2. 関数の中では、**測る前に `#main` の `style.minHeight` を空文字へ戻す**。
   前回の値が残っていると `body_h` を正しく測れない。そのうえで
   `body_h < win_h` なら今と同じ式で `minHeight` を入れる
   （短くならなかった場合は空のまま）
3. `setActiveWeek()`（`src/ytsched/webroot/static/js/week.js:152-188`）の
   **末尾（`scrollToId()` のあと、`return true` の前）**で呼ぶ。
   `scrollToId()` は `body_h <= win_h` を見て早く返す作りなので、
   その判定より先に高さを足さないこと
4. `window` の `resize` と `orientationchange` でも呼ぶ。登録は
   main-page.js 末尾の、他のリスナーを並べてある所へ足す
5. `onloadHdr()` は、今の `if (body_h < win_h) { ... return; }` の代わりに
   この関数を使う形へ書き換える。**読み込み時の挙動を変えないこと**。
   いまは短いときだけ `visibility: visible` にして `dispGauge()` を呼び
   `return` し、長いときは `scrollToDate()` を通ってから `dispGauge()` を
   呼んでいる。この分かれ方は保つ

## 変えないこと

- CSS は触らない（`#main { min-height: 100dvh }` の案は、`body` に週バーと
  メニューバーぶんの padding が入るため見送りと決めてある）
- 編集画面（`edit-page.js`）・ゴミ箱（`trash-page.js`）は対象外
- Python 側は触らない

## 完了条件

- `mise run fmt` / `mise run lint` が通る
- 上の 1〜5 が入っている

## 報告

`archives/agents/TODO-184/implementer-report.md` に、変更したファイルと
変更点、判断が要る点を書く。返事は 5 行以内で、報告ファイルのパスを示すこと。

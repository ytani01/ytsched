# TODO-184 実装報告（implementer）

## 変更したファイル

- `src/ytsched/webroot/static/js/main-page.js`
  - `window.ytsched.fillMainHeight()` を新設。測る前に `#main` の
    `minHeight` を空文字へ戻してから `body_h < win_h` を判定し、
    短ければ従来と同じ式で `minHeight` を入れる（短くなければ空のまま）
  - `onloadHdr()` の `minHeight` 設定部分をこの関数呼び出しに置き換え。
    `body_h < win_h` による分岐そのもの（短いときは `visibility` を
    `visible` にして `dispGauge()` を呼び `return`、長いときは
    `scrollToDate()` を通る）は変えていない
  - ファイル末尾で `window` の `resize` / `orientationchange` にも
    `ytsched.fillMainHeight` を登録
  - 冒頭コメントの「外へ出すもの」に `fillMainHeight()` を追記
- `src/ytsched/webroot/static/js/week.js`
  - `setActiveWeek()` の末尾、`scrollToId()` のあと `return true` の前で
    `ytsched.fillMainHeight()` を呼ぶ
  - 冒頭コメントの「外から使うもの」に `fillMainHeight()` (main-page.js) を追記

## 確かめたこと

- `mise run fmt` / `mise run lint`（`fmtjs` の prettier・`lintjs` の
  eslint を含む）/ `mise run typecheck` がすべて通ることを確認
- 依頼の 1〜5 が入っていることを diff で確認（上記の変更点の通り）

## 判断が要る点

- `onloadHdr()` 側は、分岐のために依然として `body_h`/`win_h` を自前で
  計算してから `fillMainHeight()` を呼んでいる（`fillMainHeight()` の
  内部でも同じ計算をやり直す形になり、二重になる）。依頼の 5 で
  「短いときだけ visible にして dispGauge() を呼び return し、長いときは
  scrollToDate() を通る、という分かれ方は保つ」とあり、この分岐自体は
  `fillMainHeight()` の外に残す必要があるため、二重計算は許容した。
  `console.log` の重複を避けるため、`onloadHdr()` 側の `console.log` は
  削除し、`fillMainHeight()` 内の 1 箇所だけに残した

## 残したもの・気づいたこと

特になし（依頼の範囲内で完結）。

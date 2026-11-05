# TODO-227 implementer 報告

## 変更
- `src/ytsched/webroot/static/js/edit-page.js`: `window.addEventListener("resize", changeDetailHeight)` を 1 行足した。計算式・最小 100px・間引きは変えていない。ファイル先頭のコメントを、resize からも呼ぶ実態に直した。
- `TODO.md`: 「`changeDetailHeight()` を呼び直す」のチェックのみ入れた。

## 確かめたこと
- 前提の読み合わせ: `base.html` の viewport は `interactive-widget=resizes-content`（7 行目）。Chrome の仕様では、この指定でキーボード表示時に layout viewport が縮み `resize` が起きる。`changeDetailHeight()` が使う `documentElement.clientHeight` も縮む見込み。**実機では未確認**。
- `rg -n changeDetailHeight src docs tests`: 該当は `edit-page.js` だけ。説明は更新済み。
- `mise run fmt`: 変更なし、ruff も通った（JS は対象外）。

## 残る懸念
- `resize` は iOS Safari では、キーボードで layout viewport が縮まないため起きない見込み（`keyboard.js` の `followKeyboard()` が担当で、触っていない）。
- キーボードを閉じたときに戻ることは、同じ `resize` で再計算されるため読み合わせでは戻る。実測は verifier と実機に任せる。

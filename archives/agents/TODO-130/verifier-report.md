# TODO-130 verifier 報告

## 1. 差分の確認

`git diff` は `src/ytsched/webroot/static/css/my.css` の 2 箇所のみ。

- `.my-mini-cal-dot` の `width`/`height`: 4px → 5px
- `.my-mini-cal-sq` の `width`/`height`: 4px → 5px

依頼どおりで、他のファイル・箇所の変更なし。

## 2. はみ出しの検討

`my.css` の関連ルール:

- `.my-mini-cal-day`: `width: 24px; height: 24px;`（セル。border は別に 1px）
- `.my-mini-cal-daynum`: `line-height: 14px;`
- `.my-mini-cal-marks`: `display: flex; justify-content: center; align-items: center; gap: 1px; margin-top: 1px;`

`main.html`（235〜296 行あたり）を見ると、1 セルに出る印は
`.my-mini-cal-dot`（予定、`has_sched` のとき）と `.my-mini-cal-sq`
（ToDo、`has_todo` のとき）の最大 2 個で、それ以外に増える仕組みはない
（`{% if %}` で各 1 個ずつ足すだけ）。

2 個並んだときの横幅は `5px + gap(1px) + 5px = 11px`。セル幅 24px・
`.my-mini-cal-marks` は `justify-content: center` で中央寄せなので、
4px → 5px にしても余裕（24px 中 11px）があり、はみ出しや折り返しは
起きない。`.my-mini-cal-daynum` の `line-height: 14px` は日付数字用の
行で、`.my-mini-cal-marks` はその下に `margin-top: 1px` で別行として
積まれる構造。縦方向も `daynum` の高さ＋`margin-top`＋印の高さ 5px が
セルの高さ 24px に収まるかは目視のほうが確実だが、CSS 上の数値だけ見ても
余裕があり、懸念は無い。

## 3. lint / test

```
mise run lint
```
→ ruff format（38 files unchanged）、ruff check（All checks passed!）、
eslint（エラーなし）、basedpyright（0 errors, 0 warnings, 0 notes）、
mypy（Success: no issues found in 35 source files）。すべて通過。

```
mise run test
```
→ `553 passed in 127.57s`。失敗なし。

## 4. 残る懸念

- CSS の数値上ははみ出さないと判断したが、実際のブラウザ描画（アンチ
  エイリアシングによる丸の見え方、印が奇数サイズになったことでの視認性向上の
  実感）は目視確認していない。必要なら別途スクリーンショットでの確認を
  勧める。

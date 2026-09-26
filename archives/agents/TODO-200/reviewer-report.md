# TODO-200 reviewer 報告

## 対象

`git diff`（未コミット）:
- `src/ytsched/webroot/static/js/main-page.js`
- `src/ytsched/webroot/templates/main.html`

## 確認した内容

- `rg -n 'submit-form|submit-on-change' src/ytsched/webroot` の結果、
  `data-action` を持つ要素は 3 つだけ：
  - `main.html:370` 検索アイコン（`<svg>`）— `submit-form`（変更なし）
  - `main.html:427` ToDo 日数の `<select>` — `submit-on-change`（今回変更）
  - `main.html:448` フィルタアイコン（`<svg>`）— `submit-form`（変更なし）
- `actionMouseDownHdr`（main-page.js:195-269）の `switch` に
  `submit-on-change` の `case` は無く、`default` も無い。したがって
  `<select>` を `mousedown` しても何も起きない（意図どおり）。
- `actionChangeHdr`（main-page.js:271-289）の `case "submit-on-change"` が
  `ytsched.doSubmit(el.dataset.formId)` を呼ぶので、`change` イベント
  （選び直したとき）だけ送信される。
- 検索・フィルタの `<svg>` は `submit-form` のまま残っており、
  `actionMouseDownHdr` の `case "submit-form"`（main-page.js:262）で
  引き続き拾われる。`change` イベントは `<svg>` には発生しないので
  `actionChangeHdr` 側の削除の影響も受けない。
- `actionElement`（main-page.js:188-193）は `event.target.closest("[data-action]")`
  で最も近い `data-action` 要素を探す実装。`<select>` 自身に
  `data-action` が付いているので、他の要素を誤って拾う余地は無い。
- 他に `submit-form` / `submit-on-change` を使う要素は無く、今回の
  リネームで壊れる箇所は見当たらない。

## 結論

分岐の意味は正しい。`<select>` は `change` でのみ送信され、
検索・フィルタのアイコンは `mousedown` での送信を保っている。
他に影響を受ける要素も無い。

## 指摘

無し。

## 判断が要る点

無し（境界線上の判断も特になし）。

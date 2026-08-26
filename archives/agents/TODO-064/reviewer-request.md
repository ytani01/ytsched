# TODO-064 reviewer への依頼

`git diff HEAD` の内容（`my.js` と `main.html`）を見てほしい。

## 何をしたか

PC のマウスの左右ドラッグでも週を送れるようにした。`mousedown` を
`window` に **capture** で登録し、`stopPropagation()` で伝播を止めて、
日付セルなどの `onmousedown`（押した瞬間に遷移する）が発火しないように
している。動かずに離したときは `mouseUpHdr` が
`closest("[onmousedown]")` の `onmousedown` を自前で呼ぶ。

タッチの挙動は変えない方針で、タッチ由来の `mousedown` は
`lastTouchMsec` を見て素通しさせている。

背景は `TODO.md` の TODO-064 の節にある。

## 特に見てほしいところ

- **`stopPropagation()` で伝播を止めることの副作用。** 一覧画面で、
  クリックが効かなくなる要素は無いか。`main.html` と `sde.html` を
  読んで確かめてほしい（除外しているのは
  `input, textarea, select, label, a` の上だけ）
- **`mouseUpHdr` が `onmousedown` を自前で呼ぶやり方**の危うさ。
  `el.onmousedown(event)` の `this` や、渡している `event` が
  `mouseup` のものであることが問題にならないか
- **タッチとマウスで `swipeStart` / `swipeDragging` を共有している**
  ことによる取り違え
- `lastTouchMsec` による見分けが外れる場面
- `swipeDragTo()` / `swipeFinish()` への切り出しで、**タッチ側の挙動が
  変わっていないか**（元のコードは `git show HEAD:src/ytsched/webroot/static/js/my.js`）
- 後始末の漏れ（ウィンドウの外でボタンを離した、ドラッグ中に別のイベントが
  来た）

## 報告

`archives/agents/TODO-064/reviewer-report.md` に書く。返事は 5 行以内。
**コードは直さない。**

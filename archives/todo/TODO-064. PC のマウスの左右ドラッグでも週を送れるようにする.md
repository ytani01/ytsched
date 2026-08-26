# TODO-064. PC のマウスの左右ドラッグでも週を送れるようにする

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort high | main のみ + verifier + reviewer |
| 実施 | Opus 5 / effort high | main + verifier + reviewer + wording |
| 消費 | output 31,995 / cache_creation 218,181 / 概算 $3.6 |
|      | main 78% + verifier 13% + reviewer 6% + wording 4%（料金の割合） |

## きっかけ

2026-08-26 に、利用者から「PC の左右マウスドラッグには対応してますか？」と
聞かれた。**対応していなかった。**

週送りのスワイプ（TODO-054・TODO-057）は `touchstart` / `touchmove` /
`touchend` / `touchcancel` だけに登録してあり、`mousedown` 系は見ていない。
PC で週を送る手段は ←→ キー（`keyHdr`）と、前週・次週ボタンの 2 つだった。

## 素直に `mousedown` を足すだけでは効かない

一覧の日付セル・スケジュール項目・追加ボタンは
`onmousedown="doGet(...)"` で**押した瞬間に**遷移する。セルの上でボタンを
押した時点で画面が変わってしまい、ドラッグを始められない。一覧は表で
埋まっているので、`onmousedown` を持たない余白はほとんど無い。

着手前に利用者と相談し、**セルの上からでもドラッグできるようにする**と
決めた（一覧画面でマウスを使ったときだけ、遷移のきっかけを「押した瞬間」
から「離した瞬間」へ変える）。

## やったこと

### 1. 追従と判定を、タッチとマウスで共通にした

`my.js` から 2 つを切り出し、タッチ側（`touchMoveHdr` / `touchEndHdr`）も
これを使うようにした。**タッチの挙動は変えていない。**

- `swipeDragTo(dx, dy)` — 横の動きと判定してから `translateX()` を掛ける。
  追従を始めたかどうかを返す。タッチはこれが true のときだけ
  `preventDefault()` して縦スクロールを止める
- `swipeFinish(dx, dy, elapsed_msec)` — 画面幅の 1/3 以上動いたか、速く
  払ったかを見て、週を送るか 0 へ戻すかを決める

### 2. `mousedown` を capture で拾う

`window` に **capture** で登録し、`stopPropagation()` で伝播を止める。
capture で止めると target まで届かないので、要素の `onmousedown` は
発火しない。

```javascript
window.addEventListener('mousedown', mouseDownHdr, true);
window.addEventListener('mousemove', mouseMoveHdr);
window.addEventListener('mouseup', mouseUpHdr);
```

`mousedown` では `preventDefault()` もしている（ドラッグ中に文字が
選択されないように）。

次の 3 つは伝播を止めず、今までどおり動かす。

- **タッチ由来の `mousedown`。** ブラウザはタッチのあとにこれを作って
  投げてくる。`lastTouchMsec`（最後にタッチのイベントを見た時刻）から
  700ms 以内なら素通しさせる。**タッチでの挙動は変えない**
- **左ボタン以外**
- **入力欄・ラベル・リンクの上**（`input, textarea, select, label, a`）。
  検索欄で文字を選べるように。ラベルはメニューの開閉（`menu-sw`）に
  使っている

### 3. 離したときに `onmousedown` を自前で呼ぶ

`mouseDownHdr` が `closest("[onmousedown]")` で覚えておいた要素の
`onmousedown` を、`mouseUpHdr` が呼ぶ。テンプレートの `onmousedown` は
書き換えていない。変更は `my.js` と、リスナーを登録する `main.html` の
`<script>` に閉じている。

## reviewer の指摘で直した 2 つ

どちらも「黙って何も起きない」経路だった。

### クリックとドラッグの間に、何も起きない範囲があった

最初は「5px 以内ならクリック」としていた。追従が始まるのは 60px からなので、
**5px 超〜60px 未満だけ動かして離すと、クリックとしても週送りとしても
扱われず、何も起きなかった。** マウスは指と違い、押した位置と離した位置が
この範囲でずれることは普通に起きる。

**「追従を始めていなければ、どれだけ動いていてもクリック」に変えた。**
マウスには縦スクロールのためのドラッグが無いので、追従していない動きは
クリックでよい。

### `mouseDownHdr` の後始末が無かった

`touchStartHdr` は先頭で `cancelSwipeDrag()` を呼んでいるのに、
`mouseDownHdr` には無かった。ウィンドウの外でボタンを離すと `mouseup` が
来ず、
`swipeDragging` が true のまま残る。その状態で動かさずにクリックすると
「追従していた」と見なされ、**その 1 回目のクリックが効かない。**
`mouseDownHdr` の先頭にも同じ後始末を置いた。

## 見送ったもの

reviewer の確信度の低い指摘 2 つは、そのままにした。

- **タッチ対応ノート PC で、タッチの直後 700ms 以内に本物のマウス操作を
  すると、マウス側もタッチ扱いで素通しされる。** そのときは今までどおり
  押した瞬間に遷移するだけで、害は無い
- **`el.onmousedown(event)` に渡しているのが `mouseup` の event である
  こと。** 今のテンプレートの `onmousedown` はどれも `event` を見ていない。
  見るものを足すときに気づけるよう、コードにコメントを残した

追従を始める閾値（`SWIPE_MIN_X` = 60px）そのものは TODO-062 の話なので、
ここでは変えていない。マウスでも同じ値を使っている。

## テスト

`mise run lint` / `typecheck` / `test`（439 passed）と
`node --check` が通ることに加えて、verifier が playwright で実際に触った
（`archives/agents/TODO-064/verifier-report.md`・`verifier-report2.md`）。

- 日付セルを左へ 200px ドラッグ → 次週、右へ → 前週
- **動かさずにクリック → 今までどおり編集画面へ**（ここが壊れると一覧から
  何も開けなくなる）
- 10px・30px・59px 動かして離しても編集画面へ（何も起きない範囲が
  残っていないことの確認）
- 縦に 100px 動かして離してもクリック扱い（意図どおり）
- 追加ボタン、前週・次週ボタン、検索ボタン、検索欄への入力
- タッチイベントを合成しての週送り（タッチの挙動が変わっていないこと）
- 編集画面のボタン（リスナーは一覧だけに登録しているので影響が無いこと）

**「ウィンドウの外で `mouseup` を出さずに離す」状況は、headless
chromium では作れなかった。** 再読み込みを挟む近似の手順でしか確かめられていない。

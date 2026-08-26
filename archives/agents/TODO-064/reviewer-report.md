# TODO-064 reviewer 報告

## 確信度の高い指摘

### 1. クリックとドラッグの間に「死角」があり、クリックが無音で消える

`my.js` の `mouseUpHdr` は、クリックと見なす条件を
`CLICK_SLOP_PX`（5px）で判定し、それ以外は `swipeFinish()` へ渡す。
`swipeFinish()` は `SWIPE_MIN_X`（60px）未満なら `cancelSwipeDrag()` して
何もせず戻る。

つまり、**押してから離すまでの間に 5px 超〜60px 未満だけ動いた場合**
（縦の動きも `SWIPE_X_PER_Y` 込みで同様に判定される）、クリックとしても
週送りとしても扱われず、`onmousedown` は一度も呼ばれない。マウスは
指と違い、押した位置と離した位置がこの範囲でずれることは普通に起きる
（手ぶれ、光学マウス以外の追従特性、トラックパッドなど）。

再現条件: 日付セル・スケジュール項目・追加ボタン・メニューバーの
アイコンなどのいずれかの上で、マウスボタンを押してから 5〜59px
動かして離す。何も起きない（遷移もせず、週も送られない）。

`TODO.md` の確かめ方には無い状態（微動あり・ドラッグと呼べるほどでは
ない）だが、実際の使用では頻繁に起きうる。黙って失敗する経路になっている。

### 2. `mouseDownHdr` に `touchStartHdr`相当の後始末が無い

`touchStartHdr` は先頭で `cancelSwipeDrag(); // 前の指が離れ損なっていた
ときの後始末（念のため）` を呼んでいるが、`mouseDownHdr` には対応する
呼び出しが無い。

前回のドラッグが `mouseup` を伴わずに終わった場合（ウィンドウの外へ出て
ボタンを離し、その後 `mousemove` が一度も来ていない状態）、
`swipeDragging` は `true` のまま、`elWeekWrap` には
`translateX()` と `my-week-wrap-dragging` が残る。この状態で次に
**動かさずにクリックだけ**すると、`mouseUpHdr` の「クリックと見なす」
条件は `! swipeDragging` を含むため素通りせず、`swipeFinish(0, 0, …)` に
回ってしまう。結果、その回のクリックの `onmousedown` は呼ばれず
（`cancelSwipeDrag()` で見た目だけ直る）、ユーザーから見ると「1 回目の
クリックが効かない」という形で現れる。

`mousemove` が一度でも先に来れば `mouseMoveHdr` の
`! (event.buttons & 1)` チェックで自然に直るので、常に再現するわけでは
ないが、`touchStartHdr` が明示的に備えている「念のため」の後始末が
マウス側に無いのは非対称。

## 確信度が低い指摘（参考）

- `MOUSE_AFTER_TOUCH_MSEC`（700ms）による見分けは、タッチとマウスの
  両方を持つ機器（タッチ対応ノート PC など）で、タッチ操作の直後
  700ms 以内に本物のマウス操作をすると、マウス側もタッチ扱いで
  素通しされる。実害は小さいと思われる
- `mouseUpHdr` が `el.onmousedown(event)` に `mouseup` の event を渡す点。
  現状 `main.html` / `sde.html` の `onmousedown` 属性はどれも `event` を
  参照していないので今は問題にならないが、将来 `event.shiftKey` などを
  使う属性が増えると壊れる作りではある

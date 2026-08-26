# TODO-057. スワイプで隣の週を指に追従させる

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort high | implementer + verifier + reviewer |
| 実施 | Opus 5 / effort high → medium | implementer ×2 + reviewer + verifier ×2 + wording |
| 消費 | output 46,370 / cache_creation 952,715 / 概算 $12.0 |
|      | main 54% + verifier 22% + implementer 21% + reviewer 3% + wording 1%（料金の割合） |

`--since '2026-08-26 11:27:04'`（TODO-060 の完了時刻）で切った。立てたのは
2026-08-26 の朝で、間に TODO-058〜060 を挟んでいるため。

分担の理由と各担当の報告は `archives/agents/TODO-057/` にある。

## きっかけ

TODO-054 で左右のスワイプによる週送りを入れたとき、「中身が指について
きてほしい」を別の項目にすると決めた。TODO-049 の「前後の週を先読みして
DOM に持つ」も、ひと続きなのでここで扱った。

TODO-054 と分けたのは、閾値を超えたら `moveToMonday()` を呼ぶだけなら
`my.js` の中で閉じるのに対し、指に追従させるには隣の週の中身が先に DOM に
無いといけないから。

## 決めたこと

着手する前に、6 つを決めた。

| 決めること | 決定 |
|---|---|
| 隣の週の中身 | サーバが最初から 3 週分を出す（`load_sched()` を 3 回呼ぶ） |
| どこまで並べるか | 3 週。中央だけ通常フロー、前後は `position: absolute` で画面の外 |
| 送ったあと | 滑らせて確定してから、今までどおり `doGet()` で読み直す |
| ゲージと URL | 確定してから合わせる（読み直しで揃うので、足すコードは無い） |
| 他の経路 | メニューバーの ◀▶ とキーの ←→ も、同じアニメーションを通す |
| 送る判定 | 画面幅の 1/3 以上動いたか、速く払ったとき。時間の制限は外す |

**隣の週を絶対配置で画面の外に置くのは、縦スクロールを今のままにして
おくため。** 3 週を `flex` で並べて各パネルを `overflow-y: auto` にすると、
`body` が縦に動かなくなり、`scrollToId()`・`scrollToDate()`・`onloadHdr` の
高さ計算・`followKeyboard()` を全部書き直すことになる。中央の週だけを通常
フローに残せば、`body` の高さは今までどおり中央の週が決める。

**送ったあとに読み直すのは、状態を合わせる先を増やさないため。**
URL・`cur_day`・ゲージ・`blink`・ToDo の「今日」扱い・履歴が、どれも今の
経路のまま動く。読み直さず DOM を差し替える形にすると、これを全部
JavaScript 側で合わせることになり、TODO-049 で起きた「URL だけ変わって
画面が変わらない」種類の不具合が入りやすい。

**送る判定から `SWIPE_MAX_MSEC`（800ms）を外したのは、追従させると操作が
変わるから。** 中身が指について動くと、ゆっくり引っ張って位置を見ながら
決める操作が自然になる。縦との切り分け（`SWIPE_X_PER_Y`）と画面端の除外
（`SWIPE_EDGE_PX`）は TODO-054 のままにした。

## やったこと

### サーバが 3 週分を出す（`main_handler.py`）

通常モードでは `load_sched()` を `date-7日`・`date`・`date+7日` の 3 回
呼び、`weeks`（`{"pos": "prev"|"cur"|"next", "sched": [...]}`）を
`render()` へ渡す。検索モードは今までどおり 1 回だけ呼び、`weeks` は
`cur` の 1 要素。既存の `sched`・`date_from`・`date_to` は中央の週の値の
まま変えていない（週バーと検索モードの行が使っている）。

`load_todo()` は 1 回だけ呼び、結果を 3 回の `load_sched()` に渡す。
`todo_today_sde` は日付が一致した週にしか付かないので、重複しない。

### テンプレートを 3 パネルに分ける（`main.html`）

日付ブロックのループを `#week_wrap` と `weeks` のループで包み、各週を
`my-week-panel my-week-{prev,cur,next}` の `div` にした。

**日付ブロックの `id="date-..."` は、中央のパネルにだけ付ける。**
隣のパネルは `data-date="..."` にした。`my.js` の `scrollToId()` は
`getElementById('date-YYYY-MM-DD')` で探すので、隣の週にも同じ `id` が
あると「画面内にある」と判断して読み直しを飛ばす。**TODO-049 の退行
（URL だけ変わって画面が変わらない）とまったく同じ形になる**ところで、
この項目でいちばん外しやすかった。

`touchmove` の登録を `{passive: false}` に変えた。横の動きと判定した
あと `preventDefault()` で縦スクロールを止めないと、追従できない。
他の 3 つは `passive` のまま。

### CSS（`my.css`）

`.my-week-wrap` を `position: relative`、前後のパネルを
`position: absolute; top: 0; left: ∓100%; visibility: hidden` にした。
`body` に `overflow-x: hidden` を足して、画面の外のパネルで横スクロール
バーが出ないようにした。

**縦のずれを別に補正する必要は無かった。** 項目を立てたときは「縦に
スクロールした状態でスワイプすると、隣の週が上にずれて見えるので、
ラッパーを `translateY` で補正するか、スワイプの始めにスクロール量を
渡す」と書いていたが、ラッパーが `position: relative` なら隣のパネルの
`top: 0` は中央のパネルと同じ上端に並び、スクロールしてもラッパーごと
動く。verifier が、縦長の週でスクロールしたあとにドラッグして、
`.my-week-cur` と `.my-week-next` の `getBoundingClientRect().top` が
一致することを確かめた。

### 追従と、送りの経路（`my.js`）

`slideWeekWrap(target_x, on_done)` を新しく置き、`moveToMonday()` が
これで隣の週まで滑らせてから `doGet()` するようにした。**スワイプ・
メニューバーの ◀▶・キーの ←→ が、どれもここを通る。**

`touchMoveHdr` で横の動きと判定したら `translateX(dx)` を掛けて
`preventDefault()`。`touchEndHdr` は「画面幅の 1/3 以上動いたか、速く
払ったとき」に送り、それ以外は 0 へ戻す。`SWIPE_MAX_MSEC` を消して、
代わりに `SWIPE_FAST_PX_PER_MSEC`（0.5 px/msec ＝ 500px/秒）を足した。
**この数値は決めごとに無く、implementer が決めたものをそのまま採った。**
実機で触って違和感があれば変えられる。

## reviewer の指摘で直した 3 点

- **`slideWeekWrap()` の呼び出しが重なると `on_done()` が二重に呼ばれる。**
  `transitionend` のリスナーを足すだけで前のを外さず、タイマーも積み
  重なるので、◀▶ を連打すると 1 回目と 2 回目の `finish()` が両方走った。
  **新しい呼び出しが来たら、前の呼び出しを取り消す形**にした（前のリスナーを
  外し、タイマーを消し、その `on_done()` は呼ばない）。あとから指示された
  ほうが勝つ
- **送り終えた直後に、元の週へ巻き戻って見える。** `finish()` が
  `transform` を空にしてから `doGet()` を呼んでいた。`doGet()` は
  `location.href` を変えるだけで、新しいページが来るまで今のページが
  映っているため。**`finish()` では `transform` を戻さない**ようにし、
  後始末は 0 へ戻す側（`cancelSwipeDrag()`）へ移した
- **検索モードで、滑らせた分が余白として見える。** 検索モードでは
  `.my-week-prev` / `.my-week-next` が CSS で隠れているのではなく、
  **そもそも DOM に無い**。`search_mode` で分岐させるのではなく、
  `hasAdjacentWeek()` を足して**「隣の週が DOM に無ければ滑らせない」**
  にした。隣が無いという事実にそのまま対応するので、将来も外れにくい

## テスト

`mise run fmt` / `typecheck` / `lint` / `test`（439 件）はすべて通った。
**ブラウザで動かすテストは、まだ `tests/` に無い**（TODO-056）ので、
verifier が playwright を手で動かして確かめた。

- 変更の前後のキャプチャ（412px・800px）が一致した。隣の週は
  `visibility: hidden` なので、静止画は変わらないのが期待どおり
- 指への追従、送りの判定（1/3 以上・1/3 未満・速く払う）、縦スクロール、
  縦にスクロールした状態でのずれ、スワイプ / ◀▶ / ←→ の 3 経路、
  ホームボタン（今日から離れた週で押したとき）、検索モード、検索欄での
  文字の選択 — いずれも期待どおり
- **連打で `doGet()` が二重に呼ばれないこと**は、`moveToMonday()` を
  同じ `page.evaluate()` の中で重ねて呼ぶ形で確かめた。`onloadHdr` が
  ちょうど 1 回だけ発火し、最終の URL も 1 回分だけ進んだ

**「送り終えた直後の巻き戻り」の視覚での確認だけは、できていない。**
ヘッドレスではページ遷移が約 100ms と CSS の `transition`（0.2s）より
速く終わり、`MutationObserver` の記録も実行コンテキストごと破棄されて
しまう。ただし**`transform` のリセットそのものをコードから無くした**ので、
原因のほうは構造的に消えている。

### 確認の環境について

CDP の `Input.dispatchTouchEvent` は、この環境では `touchmove` の座標が
指定値と一致せず（同じ値に固まる、順序が入れ替わる）使えなかった。
ページ内で `new Touch()` / `new TouchEvent()` を組み立てて
`window.dispatchEvent()` する形に替えたら安定した。また
`is_mobile=True` を付けると viewport が無視されたので、`has_touch=True`
だけにした。**TODO-056 でブラウザを動かすテストを書くときに、そのまま
使える。**

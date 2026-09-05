# TODO-188 reviewer 報告

対象: `git diff`（未コミット）の
`src/ytsched/webroot/static/js/main-page.js` と `tests/test_browser.py`。
コードは直していない。

## 先に、問題が無いと確認できたところ

- **`swipe.js` との二重は起きない。** `touchStartHdr()` / `mouseDownHdr()` が
  `[data-page-turn]` を `closest()` で見送るので、ボタンの上から始めた
  払い・ドラッグは swipe.js 側では最初から拾われない。新しい
  `pageTurnPointerMoveHdr()` は長押しタイマーを消すだけで、週を送らない
- **検索画面（TODO-123 の sessionStorage 経路）に影響しない。**
  `pageTurnPointerDownHdr()` が `ytsched.search_date_to` で早く返るので
  長押しタイマーが張られず、長押しから `startAutoPageTurn()` が
  呼ばれるのは非検索時だけ。`SEARCH_*_KEY` の読み書きの経路は変わっていない
- **`stopAutoPageTurn()` に `clearPageTurnHoldTimer()` を入れたので、
  キー入力・画面が隠れたとき・ボタン外を押したときは、長押しタイマーも
  一緒に消える。** `pointerup` でも早い return より前に消している

以下は、それでも残る穴。

---

## 確信度の高い指摘

### 1. ボタンの外で離すと、長押しで始めた自動送りが止まらない

`main-page.js` `pageTurnPointerUpHdr()`（差分後 641〜665 行あたり）。

```js
clearPageTurnHoldTimer();
if (!start) { return; }
const el = ... closest("[data-page-turn]");
if (!el) { return; }              // ← ここで返る
if (autoTurnTimerId !== null) { stopAutoPageTurn(); return; }
```

`el` が無いときの return が、自動送りを止める分岐より **先**にある。

- 再現する状態: **マウス**で ▶ を押しっぱなしにして自動送りが始まったあと、
  ボタンの外へカーソルを動かしてから離す。`pointerup` の `event.target` が
  ボタンでなくなるので `!el` で返り、`setInterval` が走り続ける
- タッチでは、`pointerdown` の暗黙のポインタキャプチャで `pointerup` の
  target が押した要素のままになるため、この経路には入りにくい。
  つまり **PC だけで起きる**
- TODO.md の「長押しで始めた自動送りは、指を離したら止まる
  （`pointerup` の既存の停止分岐が効く）」は、**ボタンの上で離したときだけ**
  成り立つ。ダブルタップ由来の自動送りは「手を離しても続く」のが仕様なので
  今まで問題にならなかったが、長押し由来はポインタに紐づくので前提が違う
- 画面のどこかを押せば `pageTurnPointerDownHdr()` の分岐で止まるので、
  復帰はできる。ただし「離したのに送り続ける」は目に見える

同じ根で、**マウスをウィンドウの外まで持っていって離した**ときも
`pointerup` が来ないので止まらない。`swipe.js` の `mouseDownHdr()` には
まさにこの後始末のコメントがある（「ウィンドウの外でボタンを離していた
ときの後始末 (念のため)」）ので、こちらだけ手当てが無いのは不揃い。

### 2. `pointercancel` で、長押しで始めた自動送りが止まらない

`pageTurnPointerCancelHdr()` は `pageTurnStart = null` と
`clearPageTurnHoldTimer()` だけで、`autoTurnTimerId` に触らない。

`pointercancel` が飛んだあと、そのポインタの `pointerup` は**来ない**
（仕様上そう決まっている）。したがって、

- 500ms を過ぎて自動送りが始まった **あと** に `pointercancel` が起きると、
  止める機会がどこにも無くなる。指を離しても送り続ける
- 起きうる場面: 長押し中にブラウザが自前のロングプレス動作
  （コンテキストメニュー、選択ハンドル）へ切り替えたとき、
  スクロールに取られたとき。ボタン（`#back_button` / `#forward_button`）には
  `touch-action` も `user-select` も指定が無い（`my.css` で
  `touch-action: none` を持つのは `.my-gauge-bar` だけ）ので、
  ブラウザ側のジェスチャに取られる余地が残っている
- **判定時間 500ms が、ブラウザのロングプレス判定とほぼ同じ**なので、
  ちょうど競合しやすい時間帯にいる

なお、`pageTurnPointerCancelHdr()` で単純に `stopAutoPageTurn()` を呼ぶと
**直せない**。このハンドラは `window` に張ってあり、ボタンと無関係な指の
キャンセルでも発火するので、ダブルタップで始めた（手を離しても続くはずの）
自動送りまで止まってしまう。直すなら「長押しで始めたかどうか」のフラグが要る。
指摘 1 の「ボタン外で離した」も同じフラグで一緒に処理できる。

### 3. 自動送り中に「止めるつもりで長押し」すると、逆に週が進む

`pageTurnPointerDownHdr()` は、自動送りが走っているかどうかを見ずに
長押しタイマーを張る。

- 再現する状態: ダブルタップで自動送りが走っている → 止めようと ▶ を押す →
  押している時間が 500ms を超える → 長押しのコールバックが
  `moveActiveDate()` を呼び、`startAutoPageTurn()` で張り直す →
  離してようやく止まる
- 結果、**「もう一度タップで止める（週は送らない）」が壊れる**。
  1 週ぶん余計に進み、さらに押している間 `auto_turn_msec` ごとに進む。
  `pageTurnPointerUpHdr()` の docstring と `src/README.md` に書いてある
  「止めるだけ (週は送らない)」と食い違う
- 「ゆっくり押す」だけで踏むので、指摘 1・2 より当たりやすい
- 素直な直し方は、`pointerdown` で `autoTurnTimerId !== null` なら
  長押しタイマーを張らないこと

### 4. `PAGE_TURN_HOLD_MSEC` のコメントの理由付けが誤っている

`main-page.js` 478〜484 行。

```
// ダブルタップの判定
// (``PAGE_TURN_DOUBLE_TAP_MSEC`` = 350) より長いので、ふつうの
// ダブルタップが先に長押しと判定されることはない
```

`PAGE_TURN_DOUBLE_TAP_MSEC` は**タップとタップの間隔**、
`PAGE_TURN_HOLD_MSEC` は**1 回の押下が続いた時間**で、比べても意味が無い。
2 回目を 500ms 以上押していれば、間隔が 350ms 以内でも長押しが先に掛かる。

TODO.md の懸念「ダブルタップの 2 回目を長めに押すと、長押しの判定に先に
掛かる」と正面から矛盾しているので、**コメントのほうが誤り**。
そのまま残すと、あとで読んだ人が「ダブルタップは長押しに取られない」と
信じてしまう。

（実挙動としては、2 回目を長く押した場合、離した時点で止まる＝ダブルタップの
「手を離しても続く」が効かない。TODO.md が「実害は無い」としているのは
「どちらも同じ方向へ送り始める」点についてだけで、離したあとの挙動は違う。
そこまで含めて許容するかは main の判断。）

### 5. 文書が更新されていない

- `src/README.md` の「### フッターの ◀▶ とダブルタップ（TODO-084）」に
  「止まるのは次の 4 つ」と列挙がある。長押しで始める経路と、その止まり方が
  ここに無い。`CLAUDE.md` が「コードを触る前に読むこと」として名指ししている
  文書なので、ずれたままだと次に触る人が誤る
- `docs/User.md` 14〜16 行「フッターの ◀▶ でも送れる。**◀▶ を
  ダブルタップすると自動で送り続け**、…」に、押しっぱなしのことが無い。
  利用者向けなので TODO 番号は書かない
- どちらも TODO-188 のチェックリストには挙がっていない。**足すかどうかは
  main の判断**（範囲外と見るなら別項目に立てる）

---

## 確信度の低い指摘（気になる程度）

### 6. テストが、TODO.md に書いた「理由付きの `pytest.skip`」になっていない

TODO.md の懸念に「押しっぱなしのテストは負荷で落ちやすい。落ちるときは
理由付きの `pytest.skip` にする」とあるが、追加された 3 件はどれも
無条件の `assert` / `wait_for_function`。

いちばん危ういのは `test_short_tap_does_not_start_auto_page_turn`。
`_tap()` の `mouse.down()` → `mouse.up()` は CDP の往復 2 回で、
これが 500ms を超えると**タップが長押しになって落ちる**。TODO-181 で
決めた形（実測した経過時間を理由に付けた条件付き skip）に倣うなら、
`_tap()` の前後で時間を測り、`PAGE_TURN_HOLD_MSEC` 相当を超えたら
skip する余地がある。

確信度を下げているのは、`test_releasing_the_button_stops_auto_page_turn`
の 400ms / 1200ms が既存の `test_tap_again_stops_auto_page_turn` と
まったく同じ値で、**既存に合わせた選択**とも読めるため。

### 7. 「500ms 経過時にまず 1 週送る」を見ているテストが無い

TODO.md のチェックリスト 3 つ目（`setInterval` だけだと最初の 1 週まで
間が空く）が、テストで区別できていない。

`test_holding_the_button_starts_auto_page_turn` は「10 秒以内に +3 週に
届くか」しか見ておらず、即時の 1 週送りが無くても
500 + 300×3 = 1.4 秒で届いてしまう。つまり
`ytsched.moveActiveDate(direction, ...)` の行を消しても緑のまま。

### 8. 「指がずれたら長押しをやめる」「検索画面では張らない」のテストが無い

- 既存の `test_swipe_from_button_does_not_move_a_week` は、払い終わるまで
  500ms 掛からないので、`pageTurnPointerMoveHdr()` が無くても通る
  （`pointerup` 側で消えるため）。move ハンドラの回帰は捕まえられない
- 検索画面で長押しタイマーを張らないこと（チェックリスト 5 つ目）を
  見るテストも無い

チェックリストは「テストを足す」としか書いていないので、どこまで見るかは
main の判断。

### 9. `test_releasing_the_button_stops_auto_page_turn` が別の理由で緑になる余地

`+3 週`で `wait_for_function` を抜けてから `page.mouse.up()` が届くまでに
負荷で遅れると、読み込み済みの範囲（`LoadWeekPages: 9`）を出て
`doGet()` のページ読み直しになる。読み直せば自動送りは当然止まるので、
「離したから止まった」ではなく「読み直したから止まった」を緑にしうる。

ただしこれも既存の `test_tap_again_stops_auto_page_turn` と同じ構図で、
通常の速度なら +3 と +4 の間で離せる。

### 10. `pageTurnPointerMoveHdr()` が `pointerId` を見ていない

2 本目の指が別の場所を動かすと、その `pointermove` の座標が
`pageTurnStart` から 30px 以上離れているので、押している指が動いて
いなくても長押し判定が消える。

ただし `pageTurnPointerUpHdr()` も `pageTurnStart` も同じく `pointerId` を
持っていない作りなので、**既存と整合はしている**。◀▶ を 2 本指で扱う
場面も考えにくい。直すなら TODO-188 の範囲を超える。

---

## main の判断が要る点（まとめ）

- 指摘 1・2・3 を TODO-188 の中で直すか、別項目に分けるか。
  1 と 2 は「長押しで始めたか」のフラグ 1 つでまとめて直せる。
  3 は `pointerdown` の 1 行のガードで済む
- 指摘 4（コメントの誤り）は、直さないと誤解を残す。1 行の書き換え
- 指摘 5（`src/README.md` / `docs/User.md`）を、この項目に含めるかどうか

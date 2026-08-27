# TODO-084 reviewer 報告

`git diff`、`week.js`/`swipe.js`/`main-page.js`/`main_handler.py` の該当箇所、
`tests/test_web.py`・`tests/test_browser.py` の追加分を読んだ。
依頼書の 6 点それぞれについて確かめた。**コードは直していない。**

## 確信度の高い指摘

無し。6 点とも、コードを辿った限りでは仕様どおりに実装されている。
以下、点ごとに確かめた内容（指摘ではなく確認結果）。

### 1. `slideWeekWrap()` の重なりと、下限 300 msec

`slideWeekWrap()` は呼ばれるたびに `cancelActiveSlide()` で前の呼び出しの
後始末だけをして `on_done()` を呼ばない設計なので、重なっても「前の回の
`setActiveWeek()`/`doGet()` が呼ばれず 1 回飛ぶ」だけで、二重に送られたり
止まらなくなったりする経路は無い（`finish()` はどの回でも 1 度しか
効かない `done` フラグで守られている）。

ただし、**通常動作では 300 という下限にほぼ余裕がある**ことも確認した。
`transitionend` は `SWIPE_SLIDE_MSEC`（200）ごろに来て `finish()` を呼ぶので、
次の `setInterval` の tick（300）までに約 100msec の余裕がある。300 と
ぴったり衝突しうるのは、`transitionend` が来ずに `setTimeout(finish,
SWIPE_SLIDE_MSEC + 100)`（＝300）のフォールバックに落ちたとき
（描画が詰まった・タブがバックグラウンドで抑制された、など）に限られる。
このときだけ、次の tick とほぼ同時刻になり、どちらが先に処理されるかで
「送れる／1 回飛ぶ」が変わりうる。実害は「1 回飛ぶ」だけなので設計判断
としては妥当だが、**この余裕の話は依頼書にもコメントにも無いので、
「300 で足りているか」の判断材料として書いておく**（低い確信度の指摘の
節ではなく、確認結果の補足）。

### 2. `cancelSwipeDrag()` の割り込み

`cancelSwipeDrag()` の `slideWeekWrap(0, on_done)` も同じ
`cancelActiveSlide` を共有するので、自動ページ送りの回と重なっても
「後から来た呼び出しが勝つ」だけで、1 と同じく **1 回飛ぶだけ**で済む。
状態が残って止まらなくなる・二重に送られる経路は見当たらなかった。

### 3. `onmousedown` → `pointerdown`/`pointerup`

`touchStartHdr()`/`mouseDownHdr()`（`swipe.js`）はどちらも
`[data-page-turn]` を `closest()` で見送るのが `stopPropagation()`/
`preventDefault()` より前にあるので、ボタン上のタッチ・マウス操作を
邪魔しない。`main-page.js` 側は `mousedown` ではなく `pointerdown`/
`pointerup` だけを見ているので、タッチ後にブラウザが投げる互換用
`mousedown`（`MOUSE_AFTER_TOUCH_MSEC`）とは型が違い、そもそも当たらない
（`mouseDownHdr()` 側の 700msec ガードも従来どおり効く）。二重に効く
経路も、後始末が抜けている経路も見当たらなかった。

### 4. `window` への委譲

`pageTurnPointerDownHdr()` はボタン以外を押したときに
`stopAutoPageTurn()` を呼ぶだけで、`preventDefault()`/`stopPropagation()`
はしていない。入力欄のフォーカス、メニューのラベルクリック、ゲージの
タップなど、他の操作を妨げる経路は無い。

### 5. `get_conf_int()` の共通化

`get_load_months()` は `get_conf_int(CONF_KEY_LOAD_MONTHS, DEF_LOAD_MONTHS,
LOAD_MONTHS_MIN, LOAD_MONTHS_MAX)` を呼ぶだけになっており、内部で
`int(v)` → `check_int_range()` → `convert_value()` という組み立ては、
削除された `str2load_months()` と同じ。警告の出し方・既定値へ落とす
条件は変わっていない。クロージャを `convert_value()` に渡す形も、
`get_conf_arg()` が受け取る `convert: Callable[[str], T]` と同じ枠組みで、
浮いた書き方ではない。

### 6. テストの壊れ方

`test_browser.py` の新規 3 本は、`page.wait_for_function(..., timeout=…)`
か「止めたあと変わらないこと」のポーリング待ちで判定しており、固定の
`sleep` で「とりあえず待って通っている」形にはなっていない。実装を
戻せば `wait_for_function` がタイムアウトして落ちる、または「止まる」
テストで週が動いてしまい `assert` が落ちる、という素直な壊れ方になる。
既存の `#forward_button` 連打テスト
（`test_week_move_reloads_outside_the_loaded_range`）に足された
400msec の待ちも理由が明記されており、他に `#forward_button`/
`#back_button` を連打しているテストは無いことも確認した。

## 確信度の低い指摘

- 1 の余裕の話（上記）以外は、特に無い。

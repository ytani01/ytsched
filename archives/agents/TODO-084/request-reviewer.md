# TODO-084 reviewer への依頼

TODO-084（フッターの ◀ ▶ をダブルタップして自動ページ送り）の実装を見る。
**コードは直さない。** 見つけたことを報告する。

読むもの: `TODO.md` の TODO-084 の節、
[`request-implementer.md`](request-implementer.md)、
[`implementer-report.md`](implementer-report.md)、`git diff`。

## 特に見てほしいところ

1. **`slideWeekWrap()` の呼び出しが重なったときの挙動。**
   `week.js` の `slideWeekWrap()` は、前の呼び出しが終わっていないと
   その後始末だけして **`on_done()` を呼ばない**。`on_done()` の中に
   `setActiveWeek()` があるので、重なった回は**週が送られずに飛ぶ**。
   自動ページ送りは `setInterval(auto_turn_msec)` で `moveToMonday()` を
   繰り返すので、間隔がアニメーション（`SWIPE_SLIDE_MSEC` = 200 と
   後始末の +100）より短いと起きる。下限を 300 にしたのはそのためだが、
   **300 で足りているか**を見てほしい。
2. **自動ページ送りの最中に `swipe.js` の `cancelSwipeDrag()` が
   割り込む経路。** カレンダー本体で横ドラッグを始めて `swipeDragging` が
   真になったあと、`swipeFinish()` が「送らない」と判定すると
   `cancelSwipeDrag()` が `slideWeekWrap(0, ...)` を直に呼ぶ。ここで
   自動ページ送りの回と重なると 1 の現象が起きる。**1 回飛ぶだけで
   済むか、それとも止まらなくなる・二重に送るなどの状態が残るか。**
3. **`onmousedown` から `pointerdown` / `pointerup` へ移したことの影響。**
   `swipe.js` の `mouseDownHdr()` は capture で `stopPropagation()` /
   `preventDefault()` をしている。ボタンを見送るようにしたことで、
   ボタンの上から始めたドラッグ・タッチが**二重に効かないか**、逆に
   **必要な後始末が抜けていないか**。タッチのあとにブラウザが作る
   `mousedown`（`MOUSE_AFTER_TOUCH_MSEC`）との兼ね合いも。
4. **`window` への委譲にしたこと**（implementer の判断 2）。capture の
   `pointerdown` で、ボタン以外を押したら自動ページ送りを止めている。
   入力欄・メニューの開閉・ゲージのタップなど、他の操作を邪魔しないか。
5. **`get_conf_int()` の共通化**（implementer の判断 1）。
   `get_load_months()` の挙動が変わっていないか（警告の出し方、
   既定値へ落とす条件）。クロージャを渡す形が `handler_util` の
   `convert_value()` の使い方として妥当か。
6. テストが、**壊れたら落ちる形**になっているか。特に
   `tests/test_browser.py` に足した 3 本が、実装を戻したときに
   ちゃんと落ちるか（固定の待ち時間に頼って、たまたま通っているだけでないか）。

## 報告

`archives/agents/TODO-084/reviewer-report.md` に書く。
返事は 5 行以内（終わったか・報告ファイルのパス・判断が要る点）。

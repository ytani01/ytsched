# TODO-084. フッターの ◀▶ をダブルタップして自動ページ送り

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort high | implementer + verifier + reviewer |
| 実施 | Opus 5 / effort high | implementer + verifier + reviewer + writer + wording |
| 消費 | output 37,201 / cache_creation 537,135 / 概算 $7.7 |
|      | main 55% + implementer 21% + verifier 9% + writer 6% + reviewer 5% + wording 3%（料金の割合） |

分担の理由と各担当の報告は
[`archives/agents/TODO-084/`](../agents/TODO-084/README.md) にある。

## きっかけ

フッターの ◀▶（週送り）はシングルタップでしか動かせず、何週も先へ
進みたいときに何度も押す必要があった。ダブルタップで自動的に送り続ける
ようにする。

## 仕様を 2 度変えている

最初は「押しっぱなし（リピート）で送り続ける」か「連打をキューに溜めて
1 週ずつ順に送る」で決めようとしていたが、2026-08-28 に**ダブルタップで
自動ページ送りを始める**仕様へ書き換えた。押しっぱなし（リピート）と、
連打を溜めておく扱いは、どちらも取りやめた。

旧仕様での作業は git の stash にあったが、コミット後に捨てた。ただし、
そこで分かったことは今回の実装に残っている。

- `slideWeekWrap()`（`week.js`）は呼び出しが重なると、前の回の
  `on_done()` を呼ばずに後始末だけして終わる。間隔が短いと**送り先へ
  移らずに週が飛ばされる**ことが分かり、自動ページ送りの間隔の下限
  （`AUTO_TURN_MSEC_MIN`）を 300（`SWIPE_SLIDE_MSEC` の 200 と、
  その後始末の +100）にした
- 滑っている最中に `swipe.js` の `cancelSwipeDrag()` が割り込むことも
  ある。今回は連打をキューに溜める仕組みを持たないので、割り込まれても
  1 回飛ぶだけで済む（reviewer の確認 2）

## やったこと

### `conf.json` の設定

キー名は `AutoTurnMsec`、既定 700、範囲 300〜10000。`LoadMonths`
（TODO-069）と同じく、画面から変える UI は無く利用者が手で書く値
なので、`get_conf_arg()` を通さず読むだけにし、`set_conf()` で消さない。

`get_load_months()` とほぼ同じ形のメソッドが 2 つ並ぶことになるため、
共通の `MainHandler.get_conf_int(key, default, min_value, max_value)` を
新設し、`get_load_months()` もそちらを呼ぶだけに書き直した。読めない値
（数字にならない、範囲の外）で警告を 1 行出して既定値へ落とす挙動は
変えていない。使われなくなった `str2load_months()` は削除した。

`get_conf_int()` の中の変換関数は、`handler_util.convert_value()` に
渡すクロージャ（`min_value`/`max_value` を閉じ込めた `convert()`）に
した。`LoadMonths`/`AutoTurnMsec` で範囲が違うため、固定範囲の
`str2todo_days()` のような形にはできなかった。

### ブラウザ側

- ボタン（`#back_button` / `#forward_button`）は `onmousedown` を
  やめ、`data-page-turn="-1"` / `"1"` を持つだけにした
- リスナーの登録とハンドラは `main-page.js` に置いた。**ボタン要素へ
  直に付けるのではなく、`window` で `pointerdown` / `pointerup` を
  拾って `closest()` で判定する**形にした。`main-page.js` は
  `<header>` の中で読まれ、フッターのボタンより先に評価されるので、
  ボタンがまだ DOM に無い時点でスクリプトが動く。`swipe.js` の
  `mouseDownHdr()` と同じやり方に揃えた
- シングルタップは 1 週送る。同じボタンを 350msec 以内にもう一度
  タップ（ダブルタップ）すると、`setInterval` で `moveToMonday()` を
  繰り返す自動ページ送りが始まる。350msec は `homeButtonHdr()` の
  ダブルクリック判定と同じ値
- 止まるのは 4 つ。もう一度タップ、他の場所をタップ、キー操作、
  画面が隠れたとき（`visibilitychange`）。読み込んだ範囲の外へ出て
  `doGet()` に倒れたときも、ページごと読み直すので止まる
- **ボタンの上から始めたスワイプ・ドラッグは、週送りとして拾わない。**
  `swipe.js` の `touchStartHdr()` / `mouseDownHdr()` の見送り対象
  （`closest()` の対象）に `[data-page-turn]` を足した。
  `mouseDownHdr()` 側は `stopPropagation()` / `preventDefault()` の
  前で返すようにし、`pointerdown` を邪魔しないようにした

`static/js/` は 8 本のまま、新しいファイルは作っていない。

## テスト

- `tests/test_web.py` に `AutoTurnMsec` の分を 4 本足した（既定値・
  `conf.json` の値・不正な値が既定値へ落ちること・手で書いた値が
  消えないこと）
- `tests/test_browser.py` に新規 3 本を足した。ダブルタップで自動送りが
  続くこと、次のタップで止まること、ボタンの上からの横払いで週が
  動かないこと。既存の `#forward_button` 連打テスト
  （`test_week_move_reloads_outside_the_loaded_range`）は、クリックの
  間隔が 350msec 未満だとダブルタップと誤認されるようになったため、
  `page.wait_for_timeout(400)` を足した
- verifier が、`mise run fmt` / `typecheck` / `lint` / `test`（482 件）
  に加えて、新規 3 本の実装を戻すと実際に落ちることを確認した
  （`window` の `pointerup` リスナーをコメントアウト、`swipe.js` の
  見送り対象から `[data-page-turn]` を外す、の 2 パターン）。アプリを
  起動して `conf.json` の `AutoTurnMsec` を書き換えたときの挙動（既定値・
  範囲の外・数字でない値）と、実際のダブルタップでの自動送り・停止も
  playwright で確かめた

## reviewer の確認結果

指摘なし。依頼書の 6 点（`slideWeekWrap()` の重なりと下限 300msec、
`cancelSwipeDrag()` の割り込み、`onmousedown` → `pointerdown`/
`pointerup`、`window` への委譲、`get_conf_int()` の共通化、テストの
壊れ方）をすべて確かめ、実装どおりだった。**通常動作では 300 という
下限にほぼ余裕がある**（`transitionend` は 200msec ごろに来るので
約 100msec の余裕があり、300 とぶつかるのは後始末のタイマーへ
落ちたときだけ）という指摘（実害は「1 回飛ぶ」のみ）は、
`AUTO_TURN_MSEC_MIN` のコメントへ書き足した。

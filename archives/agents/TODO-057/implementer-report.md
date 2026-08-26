# TODO-057 implementer 報告

## 変えたファイル

- `src/ytsched/main_handler.py` — `get()` の中で、通常モードは
  `load_sched()` を `date-7日`・`date`・`date+7日` の 3 回呼び、
  `weeks`（`{"pos": "prev"|"cur"|"next", "sched": [...]}` の 3 要素）を
  作って `render()` へ渡す。検索モードは今までどおり 1 回だけ呼び、
  `weeks` は `cur` の 1 要素にした。既存の `sched`・`date_from`・
  `date_to` は変えていない（中央の週のまま）
- `src/ytsched/webroot/templates/main.html` — `{% for sched_ent in
  sched %}` を `id="week_wrap"` の `div` と `weeks` のループで包み、
  各週を `my-week-panel my-week-{{ pos }}` の `div` にした。日付ブロック
  の `id="date-..."` は `pos == 'cur'` のときだけ付け、それ以外は
  `data-date="..."` にした。`onloadHdr` で `elWeekWrap` を拾うよう
  1 行足し、`touchmove` の登録を `{passive: false}` に変えた
- `src/ytsched/webroot/static/css/my.css` — `.my-week-wrap` /
  `.my-week-panel` / `.my-week-prev` / `.my-week-next` /
  `.my-week-wrap-dragging` / `.my-week-wrap-sliding` を追加（決めごと
  どおり、前後は `position: absolute; top: 0`、中央だけ通常フロー）。
  `body` に `overflow-x: hidden` を追加
- `src/ytsched/webroot/static/js/my.js` — `elWeekWrap` を宣言。
  `slideWeekWrap(target_x, on_done)` を新設し、`moveToMonday()` は
  これで隣の週まで滑らせてから `doGet()` するようにした（スワイプ・
  メニューバーの◀▶・キーの←→がすべてここを通る）。`touchMoveHdr` で
  横の動きと判定したら `elWeekWrap` に `translateX(dx)` を掛けて
  `preventDefault()`。`touchEndHdr` は「画面幅の 1/3 以上動いたか、
  速く払ったとき」で送り、それ以外は `cancelSwipeDrag()`（`slideWeekWrap`
  で 0 へ戻す）。`SWIPE_MAX_MSEC` は削除し、代わりに
  `SWIPE_FAST_PX_PER_MSEC`（0.5 px/msec）を追加。`SWIPE_MIN_X`・
  `SWIPE_X_PER_Y`・`SWIPE_EDGE_PX` はそのまま

## 確かめたこと

- `mise run fmt` / `typecheck` / `lint` / `test` すべて通った
  （439 件成功）。`upgradeproject` は走らせていない
- `/tmp` 配下の一時 `--datadir` でアプリを起動し、playwright で
  `TouchEvent` を直接 dispatch して以下を確認（すべて期待どおり）。
  スクリプト・キャプチャは確認後に削除済み
  - DOM: `.my-week-panel` が `prev`/`cur`/`next` の 3 つ、
    `id="date-..."` は中央週の 7 個だけ、隣の週は `data-date` の
    14 個（`getElementById` が隣の週を拾わないことを確認）
  - スワイプで指の動きに合わせて `#week_wrap` に `translateX()` が
    掛かり、隣の週が見える（キャプチャで確認）
  - 60px 未満の小さいドラッグでは追従も送りも起きない
  - 1/3 以上の距離のスワイプで次週・前週へ実際に `doGet()` で遷移
    （URL・`date_from` の変化で確認）
  - メニューバーの `forward_button`（▶）、キーボードの `ArrowLeft` の
    どちらも `moveToMonday()` を経由して同じように遷移
  - 今日から離れた週（2026-01-05）でホームボタンを 1 回押すと、今日を
    含む週（2026-08-24〜30）へ正しく遷移（TODO-049 の退行箇所）
  - 検索モード（`search_str` を送って `search_mode` にした状態）では
    `.my-week-panel` が `my-week-cur` の 1 つだけ
  - 1 日に 15 件の予定を入れて縦スクロールが必要な週を作り、
    `wheel` で下へスクロールしたあとにスワイプしても、隣の週の日付欄が
    同じ縦位置に並んだ（キャプチャで確認）。**縦のずれの補正は不要
    だった**（依頼書の見立てどおり）。縦の動きが優勢なドラッグ
    （dx=10, dy=-100）では `transform` が付かず、送りも起きないことも
    確認

## 決めごとと違う作りにしたところ

無し。依頼書・決めごとのとおりに実装した。

## 判断が要ると思ったところ

- **「速く払った」のしきい値 `SWIPE_FAST_PX_PER_MSEC = 0.5`（500px/秒）
  は、決めごとに具体的な数値が無かったので自分で決めた。** 動かして
  みて不自然でなかったので、この値のままにしている。verifier・利用者
  が実機で触って違和感があれば変えられる
- **検索モードでも、スワイプ・◀▶・キーの送りを同じ `moveToMonday()`
  （滑らせるアニメーション）に通した。** 検索モードは `weeks` が
  `cur` の 1 要素だけなので、スワイプ中は隣に何も無い分、画面の端に
  一瞬白い余白が見える。決めごとの「メニューバーの◀▶とキーの←→も、
  同じアニメーションを通す」に検索モードの除外が書かれていなかった
  ので、分岐を増やさずそのまま通した。気になるようなら、検索モードだけ
  `slideWeekWrap` を使わず即 `doGet()` にする分岐を足せる

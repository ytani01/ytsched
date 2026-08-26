# TODO-057 reviewer 報告

読んだ順: `TODO.md` の TODO-057 の節 → `request-implementer.md` →
`implementer-report.md` → `git diff`（`main_handler.py` /
`main.html` / `my.css` / `my.js`）。

決めごとどおりに作られているか、`getElementById('date-...')` が隣の週を
拾わないか、`load_sched()` を 3 回呼ぶ影響は、確認した範囲で問題無い
（`id="date-..."` は中央パネルだけ、隣は `data-date`。`todo_today_sde`
は日付が一致した週にしか付かないので重複の余地も無い）。

以下、確信度の高いものから書く。

## 1. `slideWeekWrap()` の呼び出しが重なると、古い呼び出しの後始末が
新しい呼び出しへ割り込む（確信度: 高）

`src/ytsched/webroot/static/js/my.js` 526〜562 行目の `slideWeekWrap()`
は、呼ばれるたびに

- `elWeekWrap` へ `transitionend` リスナー `onEnd`（550〜555 行目）を
  **追加するだけで、前の呼び出しで登録したリスナーを外さない**
- `setTimeout(finish, SWIPE_SLIDE_MSEC + 100)`（558 行目）という
  独立したタイマーを積む

`onEnd` は `event.target === elWeekWrap && event.propertyName ===
"transform"` としか見ておらず、「自分が登録した呼び出しの transition か」
は区別しない。1 つの DOM イベントに複数のリスナーが付いていれば、
発火したときに**全部**呼ばれる。

具体的に壊れる手順:

1. スワイプまたは ◀▶・キーで 1 回目の送りが起きる
   （`touchEndHdr` 877〜878 行目 or `moveToMonday()`）。
   `slideWeekWrap(target_x, () => doGet(...))` が呼ばれ、リスナー A と
   タイマー A が仕込まれる
2. その `transitionend`（200ms 後）が来る**前**に、もう一度
   ◀▶ を連打する、またはもう一度素早くスワイプする
3. 2 回目の `moveToMonday()` が `slideWeekWrap()` を呼び、リスナー B・
   タイマー B が追加で仕込まれる（`elWeekWrap.style.transform` は
   空でないので、A が動かした途中の位置から続けて動く。539〜548 行目の
   `finish()` はまだ `done=false` のまま生き残っている）
4. 2 回目の transition が完了して `transitionend` が発火すると、
   **リスナー A と B の両方**が呼ばれる。A の `finish()` はまだ
   `done=false` なので実行され、`elWeekWrap.style.transform = ""`
   （547 行目）でラッパーを強制的に中央へ戻し、**A の `on_done()`
   （1 回目の `doGet()`）を呼ぶ**。続けて B の `finish()` も実行され、
   同様に `on_done()`（2 回目の `doGet()`）を呼ぶ

`doGet()`（302〜305 行目）は `location.href` を書き換えるだけなので、
1 回目の遷移が始まった直後に 2 回目の代入で上書きされる形にはなるが、
**`transform=""` によるラッパーの中央への巻き戻しが 2 回起きる**ことと、
**`on_done()` が呼ばれる回数が呼び出し回数と一致しない**（1 回目の
`finish()` がタイマー A ではなく B の `transitionend` でも
呼ばれてしまう）ことは、依頼書が気にしていた「二重に `on_done()` が呼ばれ
ないか」にそのまま当てはまる。`cancelSwipeDrag()`（748〜753 行目）も
`swipeDragging` の真偽だけを見ており、**「前の `slideWeekWrap()` が
まだ終わっていない」状態を追う変数が無い**ため、この経路を防げない。

## 2. 検索モードでもスワイプ・◀▶・キーが `slideWeekWrap()` を通るが、
隣のパネルが DOM に無い（確信度: 高。main の懸念どおり）

`src/ytsched/main_handler.py` の `get()` は、検索モードでは
`weeks = [{"pos": "cur", "sched": sched}]` の 1 要素だけを作る
（342〜344 行目）。`main.html` の `{% for w in weeks %}`（251 行目）も
1 回しか回らないので、**`.my-week-prev`・`.my-week-next` の `div` 自体が
DOM に存在しない**（CSS で隠しているのではなく、そもそも無い）。

一方 `my.js` 側は `touchStartHdr`・`touchMoveHdr`・`touchEndHdr`・
`moveToMonday()` のどこにも `search_mode` の分岐が無い。検索モードで
スワイプすると、存在する唯一のパネル（`my-week-cur`、`position` は
指定していないので通常フロー）を含む `#week_wrap` ごと
`translateX()` で動かすことになり、**パネルが動いた分だけ画面の端に
中身の無い余白が見える**。実装報告の「判断が要ると思ったところ」で
本人も認識しており、意図的にそのままにしている。決めごと自体には
検索モードの除外が書かれていないので**決めごと違反ではない**が、
main の「気にしている 2 点」の 2 つ目はそのまま該当する。分岐を足すか
どうかは main の判断。

## 3. `finish()` が `transform` を空にしてから `on_done()`（`doGet()`）
を呼ぶ（確信度: 中。main の懸念どおりだが、実際に見えるかは未確認）

`slideWeekWrap()` の `finish()`（539〜549 行目）は `style.transform =
""`（547 行目、隣の週を再び画面外へ戻す）を**先に**実行してから
`on_done()`（548 行目）を呼ぶ。`on_done` は `moveToMonday()` の場合
`doGet()` で、`doGet()`（302〜305 行目）は `loadingSpinner(true)` の
あと `location.href` を書き換えるだけ。

`loadingSpinner` が使う `#loadingSpinner`（`.my-spinner`、
`src/ytsched/webroot/static/css/my.css` 412〜419 行目）は
`opacity: 0.3` の中央寄せアイコンで、**画面全体を覆う不透明な
オーバーレイではない**。`transform=""` から `location.href` の代入まで
は同期処理だが、実際のページ遷移（新しいページの読み込み）には時間が
掛かるので、ブラウザがその間に一度でも再描画すれば、**隣の週まで
滑り切った直後に一瞬「元の週（中央）」へ戻る絵**が見える可能性が
ある。ブラウザの描画タイミング次第で確実に起きるとは言い切れず、
実機・実ブラウザでの確認はしていない（確信度は中）。気になるなら、
`on_done()` を先に呼んで `transform` のリセットは省く（どうせ
ページが差し替わる）、または `visibility: hidden` を `on_done()` の
後にする、といった順序の入れ替えが選択肢になる。

## 気になるが確信度が低いもの

- `main.html` の `{% set year=0 %}`（234 行目）が `weeks` ループの外に
  1 回だけ置かれ、`{% if search_mode %}` の年表示ブロック（258〜262
  行目）はループの中で回る。検索モードは `weeks` が 1 要素なので今回は
  実害が無いが、将来 `weeks` を複数出す変更が検索モードにも及ぶと、
  年表示のリセットが週ごとに要ることを忘れそうな作り。今回の変更範囲
  では問題なし

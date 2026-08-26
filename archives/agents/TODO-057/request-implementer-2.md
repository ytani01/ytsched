# TODO-057 implementer への依頼（2 回目）

`reviewer` の指摘（`archives/agents/TODO-057/reviewer-report.md`）を
受けて、3 点を直す。**直し方は main が決めたので、そのとおりに作る。**

読む順: `reviewer-report.md` → この依頼書。1 回目の依頼書
（`request-implementer.md`）と `TODO.md` の決めごとは、そのまま生きている。

触るのは `src/ytsched/webroot/static/js/my.js` だけのはず。

## 1. `slideWeekWrap()` の呼び出しが重なると `on_done()` が二重に呼ばれる

reviewer 指摘 1（確信度: 高）。`transitionend` のリスナーを足すだけで
前のを外さず、タイマーも積み重なるので、◀▶ を連打すると 1 回目と
2 回目の `finish()` が両方走る。

**新しい呼び出しが来たら、前の呼び出しは取り消す。**

- 走っている滑らせを追う変数をモジュールの階層に持つ
  （リスナーとタイマーの id）
- `slideWeekWrap()` の先頭で、前の呼び出しが残っていれば
  **リスナーを外し、タイマーを消す。その `on_done()` は呼ばない**
- 2 回目の送りが起きたら 1 回目の `doGet()` は捨てる。あとから
  指示されたほうが勝つのが正しい

## 2. 送り終えた直後に、元の週へ巻き戻って見える

reviewer 指摘 3（確信度: 中）。`finish()` が `transform` を空にしてから
`on_done()`（`doGet()`）を呼ぶ。`doGet()` は `location.href` を変える
だけで、新しいページが来るまで今のページが映っているので、隣の週まで
滑り切った直後に中央へ戻る絵が出うる。

**`finish()` では `transform` を戻さない。**

- `finish()` は「リスナーとタイマーの後始末 → `my-week-wrap-sliding`
  を外す → `on_done()` を呼ぶ」だけにする
- `transform` を空にするのと `my-week-wrap-dragging` を外すのは、
  **元へ戻す側（`cancelSwipeDrag()`）の `on_done()` の中でやる**。
  こちらは `translateX(0px)` まで滑らせたあとなので、戻しても
  見た目は変わらない
- 送る側（`moveToMonday()`）は、滑らせた位置のままページが差し替わる

## 3. 検索モードでは滑らせない

reviewer 指摘 2。検索モードでは `.my-week-prev` / `.my-week-next` が
**CSS で隠れているのではなく、DOM に無い**（`weeks` が 1 要素）。
そのまま滑らせると、動いた分が中身の無い余白として見える。

**`search_mode` で分岐させるのではなく、「隣の週が DOM に無ければ
滑らせない」にする。** そのほうが、隣が無いという事実に素直に対応する。

- `slideWeekWrap()` の先頭で、`.my-week-prev` と `.my-week-next` の
  どちらも無ければ、`on_done()` をすぐ呼んで戻る（いまの
  `elWeekWrap` が無いときと同じ扱い）
- `touchMoveHdr` の追従も同じ条件で見送る。隣が無いのに指について
  動いても、余白が見えるだけなので

## 変えないこと

- しきい値 `SWIPE_FAST_PX_PER_MSEC = 0.5` は、そのままでよい
- 決めごと（`TODO.md`）と 1 回目の依頼書は変わっていない

## 確かめること

`mise run fmt` → `typecheck` → `lint` → `test` を通す。
**`mise run upgradeproject` は走らせない。**

アプリを起動して確かめるときは、`--datadir` に必ず一時ディレクトリを
指定する。

- ◀▶ を**連打**しても、送りが 1 回ずつ正しく進むこと（指摘 1）
- 送り終えたときに、元の週へ巻き戻って見えないこと（指摘 2）
- 検索モードでスワイプ・◀▶・キーを使っても、余白が見えないこと（指摘 3）
- 1 回目に確かめたこと（追従・送りの判定・縦スクロール・ホームボタン）が
  壊れていないこと

## 報告

`archives/agents/TODO-057/implementer-report-2.md` に書く。
**返事は 5 行以内。**

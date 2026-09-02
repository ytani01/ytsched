# TODO-162 reviewer 報告

## 確信度の高い指摘

### 1. `main-page.js` の `onloadHdr()`: 初回読み込みの位置合わせが、
   月曜以外の指定日を無視するようになった

`src/ytsched/webroot/static/js/main-page.js` の `onloadHdr()`（変更後
250〜252 行目付近）:

```js
const date = ytsched.search_date_to || ytsched.ytState.activeMonday;
```

- `ytsched.ytState.activeMonday` は同関数内で
  `ytsched.ytState.elWeekWrap.dataset.monday`（`#week_wrap` の
  `data-monday`、テンプレート側は `{{ date_from }}` = **その週の月曜**）
  から入る。**リクエストされた日付そのもの（`args.date`）ではない。**
- 削除前の `header_date.value` は `main.html` で
  `value="{{ date }}"`（`date` = `args.date`、月曜とは限らない
  リクエスト日そのもの）だった。つまり非検索モードの初回読み込みでは、
  週の月曜ではなく **リクエストされた正確な日** で `scrollToDate()` が
  呼ばれていた。
- `scrollToDate()`（`nav.js`）は `date-${date}` という ID の要素へ、
  `sde_align`（`top`/`bottom`）で寄せてスクロールする。今回の変更で、
  非検索モードの初回読み込みは常に「その週の月曜」の行へ寄せるように
  なり、**月曜以外の日を指定して開いた場合、意図した日ではなく月曜が
  上端（など）に来る**。

具体的に影響を受ける経路（どちらも `sde_align: "top"` を付けて特定の日を
フルページ GET で開く。フルページ GET なので毎回 `onloadHdr()` を通る）:

- `src/ytsched/webroot/static/js/trash-page.js`（TODO-149。ゴミ箱の
  日付欄クリック → `date: el.dataset.date`＝ゴミ箱項目の実際の日付、
  月曜とは限らない）
- `src/ytsched/webroot/static/js/main-page.js` の `case "week-date"`
  （TODO-137。月間表示の日付セルクリック → `date: el.dataset.date`）

どちらも「クリックした特定の日を上端に寄せる」ための仕組み
（コメントにもそう書いてある）だが、この変更後は常に月曜に寄ってしまう。
`tests/test_browser.py` の `test_trash_date_column_click_moves_to_that_week`
・`test_month_view_round_trip` は、対象日の要素が
DOM 上に存在する（`count()`／`visible`）ことしか見ておらず、スクロール
位置・どの日が上端に来ているかは検証していないため、テストは通るが
実際の見た目は変わる。

**代替案**: `#cur_day`（`main.html` に既存の hidden input、
`value="{{ date }}"`）が、初回読み込み時点では `header_date` と同じ
「リクエストされた正確な日」を持っている（`week.js` の
`setActiveWeek()` がクライアント側の週移動のたびに月曜へ書き換えるのは
そのあと）。`onloadHdr()` からは
`document.getElementById("cur_day").value` を使えば、既存の挙動
（特定日への位置合わせ）を保ったまま `header_date` を消せたはず。

## 確信度が低い指摘

無し。

## その他（指摘ではなく確認済みの点）

- CSS の `.my-menu-nav-center` 追加・`.my-menu-nav-left { gap: 0; }`・
  `.my-menu-nav-col-gap` の値変更・`my-align-middle` の追加は、
  いずれもこのページの当該要素にしか掛からないクラスで、他画面・他箇所
  への影響は無いことを `grep` で確認した。
- `header_date` / `date-get` への参照が、テンプレート・JS・CSS・
  `src/README.md` から漏れなく除かれていることを確認した。
- テストの改名・書き換え自体（`test_week_move_updates_cur_day_and_hides_date_inputs`）
  は、週移動時の `#cur_day` 更新と、`header_date`/`footer_date` が
  存在しないことを確かめており、対象範囲では妥当。上記 1. の懸念は、
  この改名したテストとは別の経路（初回読み込み）の話。

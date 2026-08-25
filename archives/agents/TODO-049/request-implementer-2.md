# TODO-049 implementer への依頼（2 回目 / reviewer の指摘を直す）

reviewer の報告
（[reviewer-report.md](reviewer-report.md)）を読むこと。verifier
（[verifier-report.md](verifier-report.md)）は全項目 green だったので、
直すのは reviewer の指摘だけ。

**下の 4 つを直すこと。それ以外は触らないこと。**

## 1. `sessionStorage` を守る（reviewer 指摘 1・いちばん重い）

`my.js` の `dispGage()` が `sessionStorage` を素で読み書きしている。
Safari の「すべての Cookie をブロック」や `allow-same-origin` の無い
`<iframe>` では `SecurityError` を投げる。

投げると何が起きるか: `main.html` の `onloadHdr()` の

```js
if ( body_h < win_h ) {
  const date_from_str = document.getElementById("date_from").value;
  dispGage(date_from_str);
  elMain.style.visibility = "visible";   // ← ここへ届かない
  return;
}
```

で `#main` が `visibility: hidden` のまま止まり、**画面が白いまま**に
なる。**週表示にしたことでこの分岐に入る頻度が上がっている**
（前は前後 45 日あったので 1 画面に収まることはほぼ無かった）ので、
放置できない。

直し方:

- **読み書きを `try`/`catch` で包む。** 読めなければ「前の週は不明」
  （＝ 針の動きが出ないだけ）、書けなければ黙って諦める。
  小さな関数 2 つに分けてよい
- **併せて、`onloadHdr()` のこの分岐で `elMain.style.visibility =
  "visible"` を `dispGage()` より先に持ってくる。** ゲージの都合で
  画面が出ないのはおかしい。`body_h >= win_h` のほうは
  `scrollToId()` が先に `visible` にしているので、これで両方が
  揃う

## 2. 打ち消しクラスを詳細度で勝たせる（reviewer 指摘 2）

`my.css` の `.my-gage-r-no-transition` は `.my-gage-r` と同じ詳細度
（クラス 1 つ）で、今は**後ろに書いてあるから勝っているだけ**。将来
`my.css` を並べ替えたときにエラーも出さずに効かなくなる。

`.my-gage-r.my-gage-r-no-transition` に変えて、詳細度で勝たせること。
「なぜ 2 つ重ねているか」をコメントに書くこと。

## 3. ToDo の境界のテストを、曜日によらず効くようにする（reviewer 指摘 3 ＋ main が見つけた対の 1 件）

`tests/test_main_handler.py` の `TestTodoDisplay` にある、対になった
2 件が、どちらも週表示では曜日によって意図が薄まる。

- `test_todo_days_boundary_is_inclusive`（期限 = `today + 3`、
  `todo_days=3`、`assert self.TITLE in body`）
  → 期限の日がその週に入っていると、**今日の欄に出す仕組みが壊れていても
  「その日の欄」に出るので通ってしまう**
- `test_todo_one_day_over_the_boundary_is_not_shown`（期限 =
  `today + 4`、`todo_days=3`、`day_block(body, today)` を見る）
  → 木〜日に走らせると期限の日が翌週へ出て、「今日の欄にだけ出ない」
  ではなく「週の外だから何も出ない」を見ているだけになる

**どちらも `day_block(body, datetime.date.today())` で見る形に
揃えること。** そうすると、

- 期限 `today + 3` / `todo_days=3` → **今日の欄に出る**（今日の欄に出したときだけ真）
- 期限 `today + 4` / `todo_days=3` → **今日の欄に出ない**

の対比になり、曜日によらず「`todo_days` の境界で今日の欄に出るかどうか」を
見ることになる。docstring も、この対比が読み取れるように直すこと。

## 変えないこと

- 週の範囲の決め方（`load_sched()`）、`--days` を消した跡、
  `my.js` から消したもの、`main.html` の `date_to` の削除 —
  reviewer も verifier も問題なしとしている
- `mondayOf()` の日付の扱い（reviewer が既存の `moveToMonday()` と
  一致していることを確認済み）

## 確かめること

- `mise run fmt` / `typecheck` / `lint` / `test`
- **`sessionStorage` が使えない状況で、画面が出ること。**
  playwright なら、`page.add_init_script()` で
  `sessionStorage.getItem`/`setItem` を投げるように差し替えてから
  開けば試せる。ここは実際に試して、結果を報告に書くこと
- 週送りで針が動く仕掛けが、今までどおり効いていること

## 報告

`archives/agents/TODO-049/implementer-report-2.md` に書くこと。返事は
「終わったか・報告ファイルのパス・判断が要る点」の 5 行以内。

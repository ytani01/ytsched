# TODO-183. ゴミ箱の戻るボタンで、直前に表示していた週へ戻る

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort medium | implementer + verifier |
| 実施 | Opus 5 / effort high | implementer + verifier |
| 消費 | output 39,954 / cache_creation 250,903 / 概算 $5.3 |
|      | implementer 51% + main 37% + verifier 11%（料金の割合） |

分担の理由と報告は [archives/agents/TODO-183/](../agents/TODO-183/README.md)。

## きっかけ

ゴミ箱の戻るボタン（`trash.html`）は `href="{{ url_prefix }}"` で、
`date` を付けていなかった。そのため、どの週からゴミ箱へ入っても、戻ると
今日を含む週が開いてしまう。直前に表示していた週へ戻したい。

週間表示の URL は、週を移るたびに `?date={その週の月曜}` へ書き換わる。
表示中の週の月曜は `ytState.activeMonday` にある（TODO-093）ので、
これをゴミ箱へ渡し、戻るボタンで返せばよい。

## やったこと

- `main.html` — フッターのゴミ箱リンクは素の `<a href>` で日付を持てない
  ので、ミニカレンダーの見出しと同じ `data-action="trash"` の形にした。
  件数が 0 のときに属性を付けない（押せない）のは今までどおり
- `main-page.js` — `actionMouseDownHdr()` に `case "trash"` を足し、
  `doGet(url_prefix + "trash", {date: ytState.activeMonday})` を呼ぶ
- `trash_handler.py` — `_back_date()`（`date` 引数を `handler_util.str2date`
  で検証し、`datetime.date | None` を返す）と `_back_query()`（`?date=…`
  の断片、無指定なら空文字）を足した。`get()` の描画と `_delete_many()`
  のリダイレクト（ゴミ箱へ戻るときも、空になって週間表示へ移るときも）
  の両方で使う
- `trash.html` — 戻るボタンの `href` と、削除フォームの hidden に
  `date` を条件付きで付けた

**無指定・不正な日付は「引き継がない」**（`None`）にして、URL に
`?date=` を付けない。今日の週へ戻るという結果は TODO-183 より前と同じで、
既存のリダイレクト先も変わらない。

`_restore()` は変えていない。**復活は今までどおり、復活した予定の日付の
週へ移る**（利用者と確認済み）。復活したものを見せるための遷移なので、
直前の週へ戻しては用を成さない。

## テスト

- `tests/test_web.py` に 4 件追加。`date` あり／無し・不正のときの
  戻るボタンの `href` と hidden、`delete_many` で 1 件残る場合・
  全部消える場合の Location。`date` を渡さない既存の 2 件はそのまま通る。
  フッターの件数を見るテスト（TODO-143）は `trash">` を当てにしていたので
  `data-action="trash"` を見るように直した
- `tests/test_browser.py` に 1 件追加。週間表示のフッターのゴミ箱を押すと
  `trash?date={その週の月曜}` へ移り、戻るボタンでその週へ戻る。
  **フッターのアイコン行はハンバーガーメニュー（`.my-bar-content`）の
  中にあり、既定では画面外に置かれている**ので、
  `label[for="menu-sw"]` を押して開いてからでないとクリックできない
- `mise run fmt` / `lint` / `typecheck` ○、`pytest` **679 passed**
- verifier が実機（`--datadir` は一時ディレクトリ）で、週間表示・
  月間表示・検索表示のそれぞれからゴミ箱へ入って戻る動き、1 件だけ削除・
  全部削除・復活の遷移先、0 件のときにフッターが押せないこと、
  `url_prefix` 付きでの動作を確認

## 振り返り

- **`activeMonday` が空にならないかを、月間表示と検索表示でも実際に
  確かめさせた。** 空だと `?date=` になって今日の週へ戻ってしまう。
  月間表示は `2026-09-21`、検索表示は結果の一番古い日が入り、どちらも
  空にはならなかった
- ブラウザテストで、フッターがハンバーガーメニューの中にあって既定では
  画面外という既存の構造に implementer が突き当たった。依頼書に書いて
  いなかった手順だが、`Element is outside of the viewport` から自力で
  たどり着いている

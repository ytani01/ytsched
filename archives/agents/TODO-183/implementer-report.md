# TODO-183 implementer 報告

## 変更したファイル

- `src/ytsched/webroot/templates/main.html`: フッターのゴミ箱リンクを
  `href="{{ url_prefix }}trash"` から `data-action="trash"` に変更
  （ミニカレンダー見出しと同じ形）。
- `src/ytsched/webroot/static/js/main-page.js`: `actionMouseDownHdr()` に
  `case "trash"` を追加。`ytsched.doGet` で `trash` へ、表示中の週の
  月曜（`activeMonday`）を `date` として渡す。
- `src/ytsched/trash_handler.py`: `handler_util` を import。
  `_back_date()`（`date` 引数を読んで `datetime.date | None` へ、
  無指定・不正なら `None`）と `_back_query()`（`?date=...` の断片、
  無指定なら空文字）を追加。`get()` に `date=self._back_date()` を渡し、
  `_delete_many()` のリダイレクト先（ゴミ箱に戻る/週間表示に戻る、
  両方）に `_back_query()` を付けた。`_restore()` は依頼どおり変更なし。
- `src/ytsched/webroot/templates/trash.html`: 戻るボタンの `href` に
  `?date={{ date }}` を条件付きで追加。削除フォームに
  `<input type="hidden" name="date" value="{{ date }}">` を条件付きで追加。
- `tests/test_web.py`: `test_trash_count_with_entries` を
  `data-action="trash"` を見るように修正。`TestTrashHandler` に
  `date` あり/なし/不正のときの戻るボタン・hidden の確認、
  `delete_many` で `date` を渡したときの Location 確認（1 件残る場合・
  全部消える場合の両方）を追加。既存の `date` を渡さない 2 つのテストは
  そのまま。
- `tests/test_browser.py`: `test_footer_trash_goes_to_trash_and_back_returns_to_same_week`
  を追加。週間表示のフッターのゴミ箱を押すと
  `{server}trash?date={その週の月曜}` へ移り、戻るボタンでその週へ戻る
  ことを確認する。

## 自分で確かめたこと

- `mise run fmt` → `lint` → `typecheck` → `test`（`upgradeproject` は
  走らせていない）を通し、全 679 件成功。
- 追加したブラウザテストを単体でも実行し、成功を確認した。

## 判断が要った点（自分で決めた）

- 追加したブラウザテストが、初回実装時に
  `Element is outside of the viewport` で失敗した。調べたところ、
  フッターのアイコン行（ゴミ箱含む）はハンバーガーメニュー
  （`#menu-sw` トグル）の中にあり、`.my-bar-content` は既定で
  `bottom: -60px`（画面外）に置かれていて、メニューを開いて
  初めて `bottom: 42px` へ動く仕組みだった（TODO-183 より前からの
  既存の挙動）。テストでは `label[for="menu-sw"]` をクリックして
  メニューを開いてからゴミ箱アイコンを押すようにした。
  依頼書のテスト仕様には無かった手順だが、実際の UI 構造に合わせる
  ための最小限の追加と判断した。

## 残る懸念

- 特になし。

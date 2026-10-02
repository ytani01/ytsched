# TODO-213 implementer 報告

## 変更
- `src/ytsched/main_handler.py`: `exec_cmd()` を `(date, flash_sde_id, edit_url)` の 3 要素に変更。add/fix は sde_id、del/update/cmd 無しは None。`post()` が `flash_date` / `flash_sde_id` を `mkurl` に足す（空は mkurl が落とす）。update は編集画面の URL のまま。
- `src/ytsched/webroot/static/js/main-page.js`: `flashUpdated()` を追加し load で実行。`#date-<date>` と `[data-sde-id=...]` 全部に `my-flash` を付け、`history.replaceState` で flash_* だけ URL から消す。
- `src/ytsched/webroot/static/css/my.css`: `.my-flash` と `@keyframes my-flash`（3 秒、黄色で 3 回点滅）。
- `src/README.md`: POST-Redirect-GET の段落に 2 行。
- `tests/test_web.py`（リダイレクトのテストのクラス内）: add / fix / del / cmd 無しの 4 テスト。`parse_qs, urlsplit` を import。既存の `test_post_redirects_to_get` が cmd 無しの Location 完全一致を既に見ている。

## 検証
- `mise run fmt` / `lint` / `typecheck` / `test` すべて通過（716 passed）。
- ブラウザでの点滅の実表示は未確認（JS・CSS は読み合わせのみ）。verifier で実機確認を。

## 判断
- テストは `tests/test_main_handler.py` ではなく `tests/test_web.py` に置いた。リダイレクトのテスト（`post_no_redirect`, `add_sde`）がそこにあるため。
- fix は版が上がり sde_id が変わるので、新しい（次の版の）sde_id を渡す。
- `get` 側は触っていない（未知のクエリは `_argument` で名前を指定して読むだけ）。

## 残る懸念
- `data-sde-id` は `sde_editable` のときだけ付く。編集不可の予定は点滅しない。
- `data-sde-id` を持つのは `.my-sde-content-col` なので、点滅するのは予定の行全体ではなく内容欄。行全体にしたい場合はテンプレートの変更が要る。
- 週表示で対象日が表示範囲外なら該当要素が無く、何も起きない。

## 追記（reviewer 指摘 4 と実測）
- `tests/test_browser.py` に 2 テスト: `test_flash_marks_date_and_sde_and_cleans_url`（日付の欄と予定の行に my-flash、他に付かない、flash_* だけ URL から消え date・sde_align は残る）、`test_flash_class_is_removed_after_animation`（animationend 後に class が外れる）。
- 壊すと落ちるか: `closest(".my-sde")` を外す→1 本目が落ちた。`replaceState` を外す→1 本目が落ちた。`classList.remove` を外す→2 本目が落ちた。いずれも戻して通ることを確認。
- 実測（`archives/agents/TODO-213/measure_flash.py`。黄色の相 0ms で止め、キャンバスで (255,235,59) の画素の割合）:
  日付の欄 / 予定の行 = 通常 62.2% / 83.1%、休日 64.8% / 83.4%、ToDo 64.2% / 85.3%。
  どれも黄色が見える（残りは文字）。class_bg は `.my-sde` 自身にあり、子に背景が無いので影は隠れない。修正は不要。
- `mise run fmt` / `lint` / `typecheck` / `test`（test_browser 含む）通過、718 passed。
- 懸念: 点滅の終わりの相の見た目（色の跳び）は box-shadow 化で解消済みと見ているが、画素では測っていない。

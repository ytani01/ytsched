# TODO-108 implementer 報告

## 変更

- `base.html`、`main.html`、`sde.html`、`edit.html`: インラインイベントと設定用のインライン script を削除し、`data-*` 属性へ移した。
- `main-page.js`、`edit-page.js`: 各画面の親コンテナでイベントを委譲し、既存の `window.ytsched` 関数を呼ぶようにした。
- `state.js`、`swipe.js`: `data-url-prefix` を読み、マウスのクリック復帰は data-action 要素への mousedown 送出に変更した。
- `tests/test_web.py`、`tests/test_browser.py`: data 属性の出力、テンプレートの inline event handler 不在、日付欄から編集画面・戻る操作を確認するテストを追加・更新した。

## 確認

- `mise run fmtjs` を実行した（対象外の整形差分は戻した）。
- `mise run lintjs`: 成功。
- `.venv/bin/pytest tests/test_web.py -q`: 126 passed。
- `.venv/bin/pytest tests/test_browser.py -k 'date_column_and_edit_menu_are_delegated or home_button_moves_the_view or swipe_from_button_does_not_move_a_week' -q`: 3 passed。

## 判断

- 全画面共通の URL prefix は HTML の `data-url-prefix` から初期化し、テンプレートの設定用 script も不要にした。
- ブラウザテスト全体は既存テスト群の途中で完了表示を返さなかったため、変更に関係する 3 件を個別に成功確認した。

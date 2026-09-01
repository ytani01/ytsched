# TODO-141 implementer 報告

## 変更

- `src/ytsched/trash.py` — 選択した `(sde_id, trashed_at)` を1回の書き直しで削除する `delete_many()` を追加し、壊れた行・非 object 行・未選択行とパーミッションを保持するようにした。`delete()` は互換用の薄いラッパとして残した。
- `src/ytsched/trash_handler.py` — `cmd=delete_many` の入力を検証し、0件・組数不一致・不正な日時を400、一致なしを404にした。削除後に表示できる項目が残るかでリダイレクト先を決める。
- `src/ytsched/webroot/templates/trash.html`、`static/js/trash-page.js`、`static/css/my.css` — 個別削除を選択チェックボックスへ替え、全選択・部分選択の indeterminate・件数入り確認・未選択時 disabled を追加した。
- `tests/test_trash.py`、`tests/test_web.py`、`tests/test_browser.py` — 複数削除、異常入力、HTML、確認キャンセル、全選択の操作を追加した。
- `docs/User.md`、`src/README.md` — ゴミ箱の一括削除とデータ処理の説明を更新した。

## 確認

- `uv run pytest tests/test_trash.py tests/test_web.py -q` — 157 passed
- `uv run pytest tests/test_browser.py -k trash_select -q` — 1 passed, 48 deselected
- `mise run lint` — ruff、Prettier、basedpyright、mypy、ESLint がすべて成功
- `git diff --check` — 問題なし

## 判断・残る点

- JavaScript が無効な場合は一括フォームへ組を追加しないため、サーバーは空選択として400にする。誤った対応関係の削除を避けるため。
- `TrashMax` により未表示の有効な項目が残る場合は、削除後もゴミ箱へ戻る。実データは使用していない。

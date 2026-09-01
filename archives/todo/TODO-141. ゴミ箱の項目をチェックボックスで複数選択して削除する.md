# TODO-141. ゴミ箱の項目をチェックボックスで複数選択して削除する

|        | main                | 担当                              |
| ------ | ------------------- | --------------------------------- |
| 見込み | GPT-5 / effort high | implementer + verifier + reviewer |
| 実施   | GPT-5 / effort high | implementer + verifier + reviewer |

分担の理由、依頼、報告は
[archives/agents/TODO-141/README.md](../agents/TODO-141/README.md) にある。
`tools/token-usage.py` は Claude Code の transcript を集計する仕組みで、
Codex で行ったこの項目は集計できないため、消費の行は省いた。

## きっかけ

ゴミ箱から複数の項目を完全に削除するとき、1 件ずつ削除と確認を繰り返さず、
チェックボックスで選んだ項目をまとめて削除できるようにしたかった。

## やったこと

- 各項目の個別削除アイコンをチェックボックスへ変更し、復活ボタンは残した。
  ヘッダーには表示中の項目をすべて選択するチェックボックスと、選択した
  項目を削除するゴミ箱アイコンを置いた
- 未選択時は削除ボタンを無効にした。部分選択時は全選択チェックボックスを
  indeterminate にし、削除前の確認ダイアログには選択件数を表示する
- JavaScript で選択した各項目の `sde_id` と `trashed_at` を組にしてフォームへ
  加える。JavaScript が動かず選択情報が無い場合、サーバーは 400 として
  何も削除しない
- `TrashHandler` に一括削除を追加した。0 件、組数不一致、空の値、不正な日時は
  400、一致する項目が無い場合は 404 にする。削除後に表示できる項目が残れば
  ゴミ箱へ戻り、空なら週間表示へ戻る
- `TrashFile.delete_many()` で、選択した `(sde_id, trashed_at)` だけを一度の
  書き直しで削除する。未選択、`TrashMax` により表示外の項目、JSON として
  読めない行、予定として読めない行、非 object 行を保持し、ファイルの
  パーミッションも引き継ぐ。同じ組の正常な行が重複していればすべて削除する
- 以前の個別削除と全消去の HTTP/UI を外した。全選択は現在表示されている項目
  だけを対象とし、未表示の古い項目は削除しない
- データ処理、HTTP、HTML、JavaScript のテストを追加し、`docs/User.md` と
  `src/README.md` を更新した

## テスト

- implementer: `uv run pytest tests/test_trash.py tests/test_web.py -q` —
  157 件通過
- implementer: `uv run pytest tests/test_browser.py -k trash_select -q` —
  追加したブラウザテストが通過
- implementer: `mise run lint`、`git diff --check` — 通過
- main: 壊れたオブジェクトを保持する回帰テストを追加後、
  `uv run pytest tests/test_trash.py -q` — 14 件通過
- main: `uv run pytest tests/test_browser.py -k 'trash_select' -q` — 2 件通過
- main: verifier で一度タイムアウトした TODO-141 範囲外の自動ページ送り
  2 件を再実行 — 2 件通過
- main: 最終状態で `mise run test` — formatter、Ruff、Prettier、ESLint、
  basedpyright、mypy、pytest 583 件がすべて通過
- verifier: TODO-141 のブラウザテスト 2 件、データ・HTTP テスト 157 件、
  `git diff --check` が通過。最初の全体テストでは自動ページ送り 2 件が
  タイムアウトしたが、main の個別再実行と全体再実行では通過した
- reviewer: 予定として読めない JSON オブジェクトも選択組と一致すれば消える
  問題を指摘。`SchedDataEnt.from_dict()` まで成功した行だけを削除するように
  修正し、回帰テスト追加後の再レビューで指摘解消、新たな指摘なし

# TODO-172 verifier 報告

## 確認したコマンドと結果

- `mise run lint` — 通った（ruff format/check, prettier, eslint すべて OK）
- `mise run typecheck` — 通った（basedpyright 0 errors, mypy Success）
- `mise run test` — 通った（664 passed in 198.28s）

```sh
uv run ytsched webapp --datadir <一時ディレクトリ> --port 10086 &
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:10086/ytsched/trash
```
→ `200`

- `trash.jsonl` に同一 UUID・版違いを含む 3 件を用意し、`/ytsched/trash` の HTML を取得。
  `{{ }}` / `{%` の生残りなし（grep 0 件）。
  `.my-trash-group-multi`（1）、`.my-trash-trashed-at`（3）、`.my-trash-select`（5）、
  `.my-trash-actions`（3）がいずれも展開結果に出現
- 画面キャプチャ:
  `/home/ytani/tmp/playwright-mcp/todo172-trash_closed_800.png`（PC 幅）
  `/home/ytani/tmp/playwright-mcp/todo172-trash_closed_412.png`（スマホ幅）
  → グレー帯でグループ化され、削除日時が予定の枠内 2 行目に入り、チェックボックスが大きくなっている見た目を確認
- 復活: `POST /ytsched/trash` に `cmd=restore` で 1 件送信 → HTTP 302。
  `2026/08/21.jsonl` に `sde_id` が `-1` → `-2`、タイトルに `(復活)` が付いた行が追加されていることを確認
- 一括削除（チェックボックス相当）: `cmd=delete_many` に `sde_id`/`trashed_at` を 2 組送信 → HTTP 302、
  ゴミ箱の件数が 3件→1件に減少
- 空の状態: 残り 1 件も `delete_many` で削除 → 件数 0件、「ゴミ箱は空です」表示、
  ヘッダーの `#trash-select-all` と削除ボタンに `disabled` 属性が付くことを確認
- ヘッダーの「表示中をすべて選択」（`#trash-select-all`）は `trash-page.js` の JS 側で
  各 `.my-trash-select` へチェック連動させる実装になっていることをソースで確認
  （ブラウザ JS 実行までは行わず、サーバ側の受け口である `delete_many` の動作で代替確認）

## サーバログ

例外・トレースバックなし。

## 見つかった不具合

なし。

## 判断が要る点

なし。

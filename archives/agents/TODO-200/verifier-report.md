# TODO-200 verifier 報告

## 環境

- `uv run ytsched webapp --datadir <scratchpad>/datadir --port 18765`
- Playwright（node, `chromium.launch()`）, viewport 390x844
- 使ったスクリプト: `verifier-check.js`（変更後）、`verifier-check-before.js`（変更前・STEP1のみ）

## 変更後（現状のワーキングツリー）の確認

`node verifier-check.js <datadir>/conf.json` を実行。

1. `#todo_days` に `mousedown` のみ → 読み直しは起きない。
   `nav_count_before=0, after_mousedown=0`, `url` は変化なし
   （`http://127.0.0.1:18765/` のまま）。 ○
2. `selectOption('7')`（1w）→ 送信され、読み直し後 `#todo_days` の値は `7`。
   `conf.json` の `ToDo_Days` も `"7"` になった。 ○
   ```
   "ToDo_Days": "7",
   ```
3. フィルタアイコン（`svg[data-form-id="form_filter"]`）に `mousedown` →
   送信される（`nav_happened=true`, `nav_count` が 1→2 に増加）。 ○

サーバログ（`server.log`）に traceback / exception は 0 件。

## 変更前（`git stash` で戻した状態）での不具合再現

`node verifier-check_before.js` を実行（STEP1 相当のみ）。

- `#todo_days` に `mousedown` → 読み直しが起きた
  （`nav_happened=true, nav_count=1`）。
  URL も `.../ytsched/?date=2026-09-27` に変わり、選び直す前に送信される
  不具合を再現できた。

確認後、`git stash pop` で変更を復元し、`git diff --stat` で
2ファイル（`main-page.js` +4/-2 相当、`main.html` +1/-1 相当）が
元どおりであることを確認した。

## 結論

依頼の3項目・比較用の再現確認、すべて期待どおりの値が得られた。
食い違いは無し。

## 判断が要る点

無し。

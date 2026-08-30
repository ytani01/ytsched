# TODO-117 verifier 報告

## 1. lint / typecheck / test

- `mise run lint`（ruff format/check・eslint・prettier）: ○
- `mise run typecheck`（basedpyright + mypy）: ○（0 errors / no issues）
- `uv run pytest tests`: ○ 518 passed (114.99s)

## 2. 追加テストが実装を検出するか

- `week.js` の `moveActiveDate()` の検索モード分岐
  （`if (ytsched.search_date_to)`）を `if (false && ytsched.search_date_to)`
  に潰し、関係する 10 件（footer/double_tap/keyboard/swipe/mouse_drag の
  search 系）を実行 → 検索モード関連 8 件が想定どおり FAIL（タイムアウト）、
  一覧モードの `test_double_tap_starts_auto_page_turn` と
  `test_swipe_from_button_does_not_move_a_week` の 2 件は影響なく PASS。
  元に戻して差分ゼロを確認。
- `swipe.js` の `swipeDragTo()` の検索モード分岐
  （115 行目 `!ytsched.search_date_to && !ytsched.hasAdjacentWeek()`）を
  `!ytsched.hasAdjacentWeek()` に戻し、`-k mouse_drag` の 2 件を実行 →
  `test_mouse_drag_moves_search_date_by_a_week` は想定どおり FAIL、
  `test_mouse_drag_within_move_threshold_still_works_as_a_click` は影響なく
  PASS。元に戻して差分ゼロを確認。
- 追加された 6 件（キーボード×2・タッチスワイプ×2・マウスドラッグ×2）は
  いずれも狙った分岐を実際に検出している。

## 3. 一覧画面（検索していない）の挙動

`uv run ytsched webapp --datadir <一時ディレクトリ>` を起動し
（`--datadir` は scratchpad 配下の一時ディレクトリ）、Playwright の手動
スクリプトで確認。

- キーボード → : `date=` が月曜のまま 1 週進んだ（例
  `2026-08-24` → `2026-08-31`）: ○
- キーボード ← : 1 週戻った: ○
- マウスの左右ドラッグ（250px 左払い）: 1 週進んだ: ○
- ドラッグと見なす距離に届かない動き（10px）: URL 変化なし
  （クリック扱いのまま）: ○
- `mise run test` に含まれる `test_forward_button_moves_a_week` /
  `test_back_button_moves_a_week` / `test_double_tap_starts_auto_page_turn` /
  `test_swipe_from_button_does_not_move_a_week` はすべて通過済み
  （フッター ＜ ＞・ダブルタップ自動送り・ボタン上の払いを拾わない挙動）。

アプリのログ（stdout/stderr）に例外・トレースバックなし。

## 4・5. 検索モードでの各操作

自動テスト（既存 4 件＋追加 6 件）で以下を確認済み（上記 2 の分岐確認と
併せて実装を壊すと落ちることも確認済み）。

- キーボード ← → で `date_to` が ±7 日動く: ○
- タッチのスワイプで ±7 日動く: ○
- マウスドラッグで ±7 日動く: ○（追従表示なし、離した瞬間に遷移。
  implementer 報告の「追加対応」で解消済み）
- しきい値未満のマウス操作は検索結果の予定
  （`[data-action="edit-sde"]`）へのクリックとして今までどおり動く: ○
  （`test_mouse_drag_within_move_threshold_still_works_as_a_click`）

## その他

- 全体テスト実行中に `test_tap_again_stops_auto_page_turn` が 1 回だけ
  タイムアウトで FAIL したが、単体では即 PASS。ソースは変更前の状態に
  正しく復元されていた（`git diff --stat` で確認）ため、実装起因では
  なくタイマー系テストのフラッキーな失敗と判断した。
- 作業終了後、`git status --short` で意図しない変更が残っていないことを
  確認した。

不具合は見つからなかった。implementer 報告にある「マウスドラッグが
`swipeFinish()` に届かない」問題は、追加対応で既に解消されている。

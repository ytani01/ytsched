# TODO-217 verifier 報告 3（流している途中のドラッグの直し）

スクリプト: `verify_home_slide_2.py`（`DRAGDX=<px>` を追加。4 週先からホームボタン→300ms 後に予定の上 x=300,y=400 から左へドラッグ）。差分は src のみ、私は触っていない。

1. ○ 160px ドラッグ: 編集画面へ遷移せず、放した後 URL `http://127.0.0.1:10099/?date=2026-10-12`、offset 1（今日の週から左向きに 1 週送られた）。
   translateX: 流しは 1463 まで進んだあとドラッグ開始で -60 に切り替わり（今日の週に済ませてから追従開始）、-80…-160→-247→-318→-369 と進んで終わる。ドラッグ中（3 ステップ目）の状態は offset 0、URL `?date=2026-10-05`、class `my-week-wrap my-week-wrap-dragging`。
2. ○（40px は代表にならない）40px では編集画面へ遷移したが、閾値 SWIPE_MIN_X=50 未満でドラッグが始まらないための普通のクリック（流さずに同じ 40px でも編集画面へ遷移）。そこで 60px（閾値超え・送らない量）で測った:
   編集画面へ行かず、tx は流し 1453→-60 に切り替わり -52→-31→-14→-3→0 と戻って止まる。放した後 offset 0、URL `?date=2026-10-05`、style=""。今日の週に戻って止まった。
3. ○ 前回の 1（代表 1 回、4 週先からホームボタン）: 針は単調に今週へ（True）、終了後 offset 0、URL `?date=2026-10-05`、`.my-gauge-r-no-transition` 0 件、class `my-week-wrap` のみ、near -1/1。
   console error 0 件。今日の週でのホームボタンは tx 0 のみ、ダブルタップは `?date=2026-10-05&sde_align=home` で offset 0。

- `mise run lint`: ○（ruff All checks passed、typecheck 0 errors・mypy 39 files no issues）
- `mise run test`: ○ 720 passed（1 回目の実行では末尾の件数行を取り損ね、再実行で確認）

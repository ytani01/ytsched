# TODO-217 verifier 報告 2（1 秒・ゲージ追従・取り消し）

スクリプト: `archives/agents/TODO-217/verify_home_slide_2.py`（`uv run python`。390x844、port 10099、一時 datadir）。
`DRAGY=<y>` `NOSLIDE=1` は 3 の確認用の環境変数。スクリーンショット `mid2_1_future.png` `mid2_2_past.png`（500ms 時点、目では未確認）。
差分は始める前から src 8 ファイル（gauge/nav/swipe/week/main-page/keyboard/my.css）。私は src を触っていない。

## 結果

1. ○ 4 週先からホームボタン: translateX は 0→820→1203→1368→1453→1502→1530→1546→1554→1559→1560(約 1000ms)→0（100ms 毎）。
   単調に増え、行き先 1560 に一致。針の left（getBoundingClientRect）は 222.4→210.1→201.4→196.4→…→189.0 と単調に今週へ、
   ラベルは +4w→+2w→+1w→±0（途中 +3w 等は 100ms 毎では拾えず）。全パネル(0〜4)表示。終了後 offset 0、style=""、
   class `my-week-wrap` のみ、`.my-gauge-r-no-transition` 0 件、URL `?date=2026-10-05`、near は -1/1。
   過去側（4 週前から Home キー）: tx 0→-913→…→-1560、針 155.6→…→189.0 単調、ラベル -4w→-2w→-1w→±0、終了後も同じく正常。
2. ○ 300ms 後に history.back(): 1.2 秒後 offset 3、URL `?date=2026-10-26`（今日に上書きされない）。
   300ms 後にゲージ 30% クリック: `?date=2026-03-02&sde_align=top`（選んだ日のまま）。
   300ms 後にゲージの +1w ラベル位置をクリック（DOM にある週）: offset 1、URL `?date=2026-10-12`（今日に上書きされない）。
3. × 条件つき。300ms 後に、予定の上（x=300,y=400）で左へ 160px ドラッグして放した: 流れは途切れず（tx 0→413→820→1056→…→1546 と滑らか、
   位置の飛びは無い）が、約 700ms 時点でページが `/ytsched/edit/?date=2026-10-18&sde_id=id13-1&todo_flag=false`（その下の予定の編集画面）へ
   遷移し、「流し終えたあと今日の週」にはならなかった。
   比較: 流さずに同じドラッグ（NOSLIDE=1）では編集画面に行かず、週が送られた（`?date=2026-11-09&sde_align=top`）。
   流している間はドラッグが無視され（`swipeDragTo` が false）、放したときにクリックとして扱われた可能性。原因は未確認、実害は未確認
   （実機の指で同じ操作が起きるかは未測定。マウスのみ）。予定の無い位置（y=700、ミニカレンダー上）では、流し終えて offset 0・URL `?date=2026-10-05`、飛びなし。
4. ○ ダブルタップ(200ms)＋文書の応答 1.5 秒遅延: 600ms 時点の URL は `/?date=2026-11-02`（まだ読み直し前）、
   待ったあと読み直されて（ページ内フラグ消失）offset 0、URL `?date=2026-10-05&sde_align=home`。
5. ○ 今日の週でホームボタン: tx は 0 のみ。◀▶（ArrowRight）の途中: `my-week-wrap-sliding`、transition 0.2s。
   月間表示でホームボタン: `?view=month&date=2026-10-05`、エラー無し。
8. ○ console error / pageerror 0 件。サーバログの "Traceback" は 1 件だが、`webapp()> end` の後ろ（terminate による停止時）のもの。リクエスト中の例外は未確認でなし。

## lint / test
- `mise run lint`: ○（ruff・typecheck 0 errors・mypy 39 files no issues・eslint エラー出力無し）
- `mise run test`: ○ 720 passed in 161.92s

## 補足
- 途中でスクリプトの不具合（ナビゲーション中の evaluate）で落ちた回があり、残ったサーバ（PID 119275/119278）は kill 済み。
- 8000 番のサーバには触っていない。

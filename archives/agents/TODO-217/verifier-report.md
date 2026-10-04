# TODO-217 verifier 報告

スクリプト: `archives/agents/TODO-217/verify_home_slide.py`（`uv run python` で実行。390x844、
一時 datadir に前後 60 日の予定、port 10099。実行後にサーバ停止済み）。
作業ツリーの差分は始める前と同じ（5 ファイル +96/-9。src は触っていない）。

## 結果（すべて 1 回ずつ）

1. ○ ホームボタン、4 週先から。translateX（50ms 毎）: 0 → 889 → 1308 → 1452 → 1515 → 1544 → 1556 → 1560(355ms) → 0(405ms)。
   行き先は +4*390=1560 に一致、増分が 889/419/144/63/29/12/4 と前半ほど大きい（減速）。
   流れている間は offset 0〜4 の全パネルが display != none。終了後: activeWeekOffset 0、
   style=""、class は `my-week-wrap` のみ（homing/sliding 残らず）、URL `?date=2026-10-05`（今週の月曜）、
   `my-week-near` は -1 と 1 だけ。スクリーンショット `mid_1_future.png`（180ms 後）は
   中間の週（予定 10/05〜10/11）が映っており空白でない。
2. ○ 過去側（4 週前）から Home キー: 0 → -1090 → -1370 → -1479 → -1527 → -1549 → -1558(319ms) → 0。
   全パネル（-4〜0）表示。終了後 offset 0、style=""、class `my-week-wrap`、URL `?date=2026-10-05`、near は -1/1。
   `mid_2_past.png` も撮ってある（目では 1 のみ確認）。
3. ○ 今日の週でホームボタン: 600ms の間の translateX は 0 のみ。offset 0 のまま。
4. ○ 100ms 後に history.back(): 450ms 後 offset 3、URL `?date=2026-10-26`（今日に上書きされない）。
   100ms 後に #footer_gauge_bar の 30% 位置をクリック: 450ms 後 URL `?date=2026-03-02&sde_align=top`
   （選んだ日のまま。今日に上書きされない。その日は DOM 外のため読み直しで offset 0 になるのは仕様どおりのはず）。
5. ○ ダブルタップ（200ms 間隔、4 週先から）: ページ内フラグが消えており読み直された。
   1.5 秒後の URL `?date=2026-10-05&sde_align=home`、offset 0（今週の週間表示）。
6. ○ 月間表示（`?view=month`）でホームボタン: URL が `?view=month&date=2026-10-05` に切り替わり、エラー無し。
7. ○ ◀▶（ArrowRight で 1 週送り）の途中: class `my-week-wrap-sliding`、transition-duration 0.2s、property transform。
8. ○ ブラウザの console error / pageerror: 0 件。サーバログに Traceback 無し。

## lint / test

- `mise run lint`: ○（ruff・basedpyright・mypy は 39 ファイル no issues、fmtjs 全て unchanged、eslint 出力エラー無し）
- `mise run test`: ○ 720 passed in 168.12s

## 補足

- 最初の 1 回目の実行は、スクリプトのセレクタ誤りで途中で落ち、サーバが残った。
  自分で kill 済み（PID 95603/95606）。2 回目の測定は、残ったサーバに当たった可能性があり、
  3 回目で全項目を取り直した（上の値は 3 回目。1・2 回目とほぼ同じ）。
- ポート 10088 の別のサーバ（scratchpad/data217）は私が起動したものではなく、触っていない。

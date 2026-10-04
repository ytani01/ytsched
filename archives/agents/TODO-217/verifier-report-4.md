# TODO-217 verifier 報告 4（ダブルタップの直し）

`verify_home_slide_2.py` の 4 を直して使用（4 週先からホームボタンのダブルタップ、間隔 200ms、文書の応答を 1.5 秒遅延）。
2 回目のタップの直後は、Playwright の evaluate が遷移で落ちるので、`pagehide`（応答が来て元ページを離れる直前）に状態を sessionStorage へ書かせて後で読んだ。

- ○ 読み直し後: offset 0、URL `?date=2026-10-05&sde_align=home`、style なし、class `my-week-wrap`、near は -1/1（今週の週間表示）。ページ内フラグは消えており読み直された。
- ○ 元のページの状態（2 回目のタップから 1556ms 後、pagehide の時点）: offset 4（流す前の週）、`.my-week-wrap` の style=""（transform 空）、class `my-week-wrap` のみ（homing/dragging/sliding 無し）、`.my-gauge-r-no-transition` 0 件、near は ["3"] のみ。
  流す前（4 週先に着いた時点）の near も ["3"] で同じ（週 5 が DOM に無いため。「隣の 2 週」にならないが、流す前と同じ状態）。
- ○ console error / pageerror 0 件。
- `mise run lint`: ○（ruff All checks passed、typecheck 0 errors、mypy 39 files no issues）
- `mise run test`: ○ 720 passed in 161.78s
- 補足: 前の実行では 2 回目の約 150ms 後の evaluate が「Execution context was destroyed」で落ちた（遷移が先に始まっていたため。実害は未確認）。サーバは停止済み。

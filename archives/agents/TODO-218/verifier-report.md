# TODO-218 verifier 報告

## 1. 定型の実行
- `mise run lint`: ○（エラー無し）
- `mise run typecheck`: ○ basedpyright 0 errors / mypy 39 source files no issues
- `mise run test`: ○ 722 passed (167.75s)

## 2. 実測（412x915、`?date=2027-04-26`）
手段: Playwright は node 側に無く、`.venv` の Python 版を使った（`verify.py`）。
データ・起動: 一時 `--datadir`、`--port 10999`。サーバログに例外なし。
- 2027/05 側の前の月の日: 04-29 = `…-day-out …-day-holiday` bg rgb(255,204,204) fg rgb(153,153,153) ○
  04-30 = `…-day-out` bg rgb(255,255,255) ○
- 2027/04 側の次の月の日: 05-01 = `…-day-out …-day-sat` bg rgb(255,238,238)、
  05-02 = `…-day-out …-day-holiday` bg rgb(255,204,204)（fg 153,153,153）○
- 月側と同色: 04/29 (04月側) bg rgb(255,204,204) = 05月側の前月の日と同じ ○。
  05/01 (05月側) bg rgb(255,238,238) = 04月側の次月の日と同じ ○
- ドット: 04-29 は両ミニカレンダーとも無し ○。04-16 は有り（04月側）○
- スクリーンショット `mini-cal.png`: 欠け・余計なものなし（04-16 に青ドット 1 つ、04-29 は桃色でドット無し）

## 備考
- `git diff --stat` は始める前と同じ（変更なし。追加は archives/agents/TODO-218/ の verify.py・png・報告のみ）。
- 最初のデータ作成が失敗してデータ無しの状態で 1 回測ったが、データを置き直してサーバを再起動し、上記は再測定の値。

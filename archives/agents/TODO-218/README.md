# TODO-218 の分担

- main: 実装（`mini_cal.html` の条件、`sched_load.py` のドットの判定）とテスト
- reviewer（Opus 5.5 / high）: ドットと曜日の色の分岐が変わるので、正しさを見る
- verifier（Sonnet 5.5 / medium）: reviewer のあとで、lint・型チェック・テストと、
  Playwright で前後の月の日の背景色とドットの有無を実測する（`verify.py`、`mini-cal.png`）

報告は `reviewer-report.md` / `verifier-report.md`。

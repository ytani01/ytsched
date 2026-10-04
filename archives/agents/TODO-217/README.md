# TODO-217 の分担

- main: 実装（`week.js` の `slideToWeekOfDate()` と `slideWeekWrap()` の引数追加、
  `main-page.js` / `keyboard.js` の呼び出し、`my.css` の `.my-week-wrap-homing`）
- reviewer（Opus 5.5 / high）: 分岐が変わる（ホームの単押し・Home キーが、流してから
  `scrollToDate()` を呼ぶようになる）ので、正しさを見る
- verifier（Sonnet 5.5 / medium）: reviewer のあとで、Playwright で流れる様子と
  最後の位置を実測する

報告は `reviewer-report.md` / `verifier-report.md`。

途中で利用者の依頼（流す時間を 1 秒に、ゲージの針を追従させる）が加わり、
reviewer の指摘で取り消しの経路を直したので、同じ担当に続けて頼んだ。
reviewer は 3 回（`reviewer-report-2.md` / `-3.md`）、verifier は 4 回
（`verifier-report-2.md` 〜 `-4.md`、スクリプトは `verify_home_slide_2.py`）。

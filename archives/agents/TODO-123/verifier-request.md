# TODO-123 動作確認依頼

`TODO.md` の TODO-123、実装担当の
`archives/agents/TODO-123/implementer-report.md`、および差分を確認する。
コードやテストは変更しない。

次を実行して確認する。

1. `uv run pytest tests/test_browser.py -k 'auto_page_turn_in_search_mode' -v`
   で、前後の自動送りと同じボタンによる停止が通る。
2. 検索画面を一時データディレクトリで開き、ダブルタップ後に URL の `date` が
   7 日ずつ複数回動き、画面を再読み込みしても続くことを確認する。
3. 自動送り中にフッター以外を押すと停止することを確認する。
4. 検索画面の自動送りで `.my-week-wrap-sliding` が付かず、週枠の
   アニメーションがないことを確認する。
5. `npx eslint src/ytsched/webroot/static/js/main-page.js` を実行する。

既知の対象外: 検索画面のキーボードとスワイプは TODO-117 の範囲であり、
今回の確認対象に含めない。

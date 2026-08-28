# TODO-093 verifier への依頼

`TODO.md` の TODO-093 と、`archives/agents/TODO-093/implementer-brief.md`
`archives/agents/TODO-093/implementer-report.md` を読んでから始めること。

表示中の週の月曜日を `ytState.activeMonday` に 1 本化し、`#date_from` の
hidden input を `#week_wrap` の `data-monday` 属性へ移した変更。

## 確認してほしいこと（これだけ。思いついた確認を足さない）

1. `mise run lintjs` と `mise run fmtjs` が緑か（`.js` を整形で書き換え
   ないか）。
2. `mise run lint`（ruff / eslint / basedpyright / mypy）が緑か。
3. `mise run test` が緑か。件数を報告。
4. `uv run pytest tests/test_browser.py` を **3 回** 走らせて、毎回緑か。
   implementer が `test_tap_again_stops_auto_page_turn` の 1 回だけの
   失敗（自動ページ送り停止のレース）を報告している。これが TODO-093 の
   変更由来か、既存の flaky かを見たい。落ちたら、その回の出力を貼る。
5. 一時 datadir でアプリを起動し（`uv run ytsched webapp --datadir
   <一時ディレクトリ>`、`run_in_background`）、次を curl で確認:
   - `GET /ytsched/?date=2020-01-08`（水曜）の HTML に
     `id="week_wrap"` の要素があり `data-monday="2020-01-06"`（その週の
     月曜）が付いていること。
   - 同じ HTML に `id="date_from"` が**無い**こと。
   - `{{ }}` や `{%` が生で残っていないこと。
   終わったら `pgrep -f ytsched` で PID を確かめて kill。

## 決まり

- コードは直さない。見つけたら「ファイル・行・症状」を報告するだけ。
- git commit / TODO.md 編集はしない。
- 報告は `archives/agents/TODO-093/verifier-report.md` に。返事は 5 行以内。

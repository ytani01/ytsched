# verifier 報告 TODO-222

1. ○ `mise run lint` 終了 0（ruff・eslint とも指摘なし。出力は tail のみ確認）/ `typecheck`: basedpyright 0 errors, mypy "no issues found in 39 source files" / `test`: 721 passed in 331.08s
2. ○ CLI（datadir=scratchpad/d、`uv run python` で A&B <x> の予定・時刻無し「終日」・期限 09-05 の ToDo を投入）
   - `uv run ytsched notify --datadir DIR --date 2026-09-02 --days 2`
     ```
     2026-09-02 (水)
       10:00-11:00 A&B <x>
       終日

     2026-09-03 (木)
       予定なし

     期限が近い ToDo
       09-05 請求書
     ```
     素のテキスト、`` ` `` も `&amp;` も無し。
   - 同 `--url https://example.net/ytsched`
     ```
     <https://example.net/ytsched?date=2026-09-02|2026-09-02 (水)>
       `10:00-11:00 A&amp;B &lt;x&gt;`
       `終日`

     <https://example.net/ytsched?date=2026-09-03|2026-09-03 (木)>
       予定なし

     期限が近い ToDo
       09-05 請求書
     ```
     期待どおり。
3. ○ notify.py 92 行の `slack_escape(line[2:])` を `line[2:]` に変更 → `tests/test_notify.py::test_url_links_header_and_quotes_lines` が落ちた（1 failed, 11 passed）。複製から書き戻し、`git diff` を前後で保存して cmp → 同一。
4. ○ slack-send（PATH 先頭に何もしない curl、`-w` ダミー、`-v`）
   - `-r` 無し: `"text": "[T]\n```\nhello\n```"`
   - `-r` 付き: `"text": "[T]\nhello\n"`（コードブロック無し）

食い違い・不具合なし。
補足: 起動時の git status は TODO.md・docs・src・tests の変更と archives/agents/TODO-222/ のみで、依頼外の変更は無し。

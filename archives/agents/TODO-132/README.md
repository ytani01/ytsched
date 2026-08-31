# TODO-132 の分担

| 担当 | 範囲 | 報告 |
|---|---|---|
| implementer | CSS・`sched_load.py`・`main.html`・テストの 4 ファイル | [implementer-report.md](implementer-report.md) |
| verifier | fmt / typecheck / lint / test、テストの妥当性、アプリを起動しての目視 | [verifier-report.md](verifier-report.md) |

TODO-130・131 と違い、CSS だけでなくデータモデル（`MonthCalDay`）と
テンプレートとテストにまたがるので、実装を implementer に分けた。
確認は別に verifier を立て、HTML の `class` 属性とスクリーンショットの
両方で見た目を確かめさせた。

`has_important` の意味は変えず、ToDo 用に `has_todo_important` を
足しただけなので、reviewer は入れていない。

verifier から「日付ファイルに ToDo 型の行が混ざった経路で
`has_todo_important` を見るテストが無い」という指摘が出たので、
implementer に 1 件足させた（`test_todo_in_day_file_important_is_shown_as_important`）。

`.my-mini-cal-sq` に implementer が書いた `box-sizing: border-box` は、
`*` へ既に効いていて冗長だったので main が削った（TODO-131 で確認済み）。

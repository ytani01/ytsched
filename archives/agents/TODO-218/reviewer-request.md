# TODO-218 reviewer への依頼

目的: TODO.md の TODO-218 の変更（`git diff`、未コミット）の質を見る。

- ミニカレンダーの前後の月の日にも土日祝の色を付ける（`mini_cal.html` の `d.in_month` の条件を外した）
- 休日の予定を、ミニカレンダーのドット（`has_sched` / `has_important`）の対象から外す（`sched_load.py`）
- テスト: `tests/test_web.py`、`tests/test_main_handler.py`

見てほしいこと:
- 分岐の意味が変わって困る呼び出し元が無いか（`rg -n "has_sched|has_important|in_month|my-mini-cal-day-(out|sat|holiday)" src tests`）
- CSS（`my.css` の `.my-mini-cal-day-out` と曜日のクラス）との組み合わせで、前後の月の日の見た目に矛盾が無いか
- 追加したテストが、変更を戻すと落ちるか（読んで判断。走らせてもよい）
- 古くなったコメント・文書が無いか（`src/README.md`、`docs/`）

見なくてよいもの: 色そのものの良し悪し、画面の実測（verifier がやる）。
コードは直さない。境界線上の判断は報告だけ。

報告は `archives/agents/TODO-218/reviewer-report.md` に、指摘だけを書く（問題なしの点は 1 行）。
返事は「終わったか・報告ファイルのパス・判断が要る点」だけ。

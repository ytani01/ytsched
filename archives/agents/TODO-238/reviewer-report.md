# reviewer 報告 TODO-238

`tests/README.md` の追加 3 件（test_trash / test_fix_id / test_notify）を、各テストのテスト名・docstring と、クラス名・コマンド名（`TrashFile`、`SchedUpdater`、`IdFixer`、`fix-id`、`build_notify_text`）に照らした。

誤りも言い過ぎも無い。

## 検討（実害は未確認、抜けの指摘のみ）
- test_notify: `memo`（先頭に足す）、`detail`（予定の下に字下げ）、`include_todo=False`、7 日より先の ToDo を除くこと、期限切れ ToDo を含めること、種別・場所の付け方（`[種別] タイトル @場所`）にテストがあるが、説明には載っていない。「重要な抜け」とまでは言えない。
- test_trash: 同じ予定の ID が複数回ゴミ箱に入ったときのバージョンの扱い（`max_version` が最大のバージョンを返すこと、UUID 部分だけでの絞り込みがバージョン違いも拾うこと）と、行を消してファイルを書き直したあともパーミッションが変わらないことのテストが、説明に無い。同上。

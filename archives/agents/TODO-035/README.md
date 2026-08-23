# TODO-035 の分担

- 実装: `implementer` — 依頼書 `implementer-request.md`、報告
  `implementer-report.md`
- 確認: `verifier` — 依頼書 `verifier-request.md`、報告
  `verifier-report.md`
- 実行: `runner` — 報告 `runner-report.md`
- 文書: `wording` — 報告 `wording-report.md`

## この分担にした理由

**implementer を立てたのは、`tools/token-usage.py` を新規に 1 本書き、
`mise.toml` にもタスクを足す規模だったから。**

**verifier を立てたのは、このツールの仕事が「数字を出す」ことだったから。**
出た数字が正しいかは、実装したコードを読むだけでは確かめきれない。実際、
`tools/token-usage.py` とは別に自分で書いた検算スクリプトで担当別・
モデル別・合計の突き合わせを行い、一致を確認したうえで、**実装者の
報告を鵜呑みにせず実バグを 1 件見つけた**（`find_start()` が、決着も
`docs(todo):` で書いていた古い規約の項目（TODO-013・TODO-022）で
始点を取り違える）。

**runner を追加で立てたのは、修正後の lint とテストを走らせるため。**
判断の要らない実行なので runner で足りると考えたが、実際に main の
見落とし（`find_start()` は直したが `show_list()`（`--list`）側の同じ
不具合を直し忘れていたこと）を拾った。

`.md` が複数入るコミット（`TODO.md`・このディレクトリの各報告ファイル・
`archives/todo/TODO-035. ….md`）なので `wording` を立てた
（TODO-025・TODO-026）。

## reviewer

`reviewer` は入れていない。verifier が独自の検算スクリプトで数値の
正しさまで確かめており、集計ロジック以外に込み入った分岐は無いため。

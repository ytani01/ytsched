# TODO-028 の分担

`TODO.md` の見込みどおり、implementer + verifier + reviewer。

- **implementer**: `implementer-request.md` の依頼どおり 5 件を実装。
  報告は `implementer-report.md`
- **verifier**: 実装後に動作確認。`mise run fmt/typecheck/lint/test` と
  アプリの起動確認、テストが実際に効くかの再現。報告は
  `verifier-report.md`
- **reviewer**: 実装後にコードレビュー。正しさの欠陥は無しと判断、
  3 点の設計上の指摘。報告は `reviewer-report.md`
- **wording**: `.md` を含むコミットのため、造語の候補を確認。報告は
  `wording-report.md`。「歯があるか」を「実際に効くか」に直した

verifier・reviewer は依頼内容を口頭（Agent への prompt）で渡しただけで、
依頼書ファイルは作っていない（implementer だけ着手前に依頼書を
作っていたため）。

reviewer の指摘のうち、`src/README.md` の食い違いは TODO-028 のこの
コミットで直した。残り 2 点（`date2path()` の `expanduser()` の分散、
`get_conf_arg()` の保存方針）は TODO-029 まで据え置くと決めた
（`archives/todo/TODO-028. リファクタリングで見つかった残り 5 件を直す.md`
参照）。

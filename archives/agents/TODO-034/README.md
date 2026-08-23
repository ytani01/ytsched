# TODO-034 の分担

- 実装: main（Opus 5 / effort medium）
- 確認: `verifier` — 依頼書 `verifier-request.md`、報告 `verifier-report.md`
- 文書: `wording` — 報告 `wording-report.md`

## この分担にした理由

変えるのは 3 ファイル（テンプレート 1 行の削除、`expanduser()` の
置き場所、テスト 2 件）で、実装を分ける規模ではない。一方、
コードが変わる項目なので確認は必ず別の担当に分ける（`~/.claude/CLAUDE.md`）。
`sde.html` は自動テストが直接触っていない部分なので、実際にアプリを
起動して一覧 → 編集の経路を通してもらう必要があり、`verifier` の
出番がはっきりしていた。

`.md` が入るコミットなので `wording` を立てた（TODO-025・TODO-026）。

## wording の指摘への判断（main）

挙がった 5 語のうち、`verifier-report.md` の「外形」と「実機」を直した。
「分岐の外形」は何を指すか一読で取れず、「実機」はブラウザを使わない
`curl` での確認を指していて実態と合わないため、どちらも書き直した。
「出番」「宛先」「途中の失敗」は普通の日本語なのでそのまま残した。
`wording-report.md` の中の引用は、指摘の記録なので直していない。

## reviewer

`reviewer` は入れていない。挙動を変えない片付けで、分岐も条件も
足していないため（TODO-017 の基準）。

# TODO-143 の分担

| 担当 | 範囲 |
| --- | --- |
| implementer | `TrashFile.count()`、`MainHandler.get()`、`main.html`、テスト |
| main | 仕様管理、差分確認、完了記録、コミット |
| verifier | テスト・lint・型チェックと、アプリを起動しての表示確認 |

小さい項目だが、`trash.py`・`main_handler.py`・`main.html`・テストに
またがるので implementer を分けた。表示の追加だけで分岐の変更が無いため
reviewer は立てず、確認は verifier に任せた。実際に画面へ数字が出るかは
起動して見ないと分からないので、verifier には curl での確認を頼んだ。

依頼と報告:

- [implementer-request.md](implementer-request.md)
- [implementer-report.md](implementer-report.md)
- [verifier-request.md](verifier-request.md)
- [verifier-report.md](verifier-report.md)

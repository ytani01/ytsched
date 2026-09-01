# TODO-142 の分担

| 担当 | 範囲 |
| --- | --- |
| implementer | JavaScript とブラウザテストの変更、基本確認 |
| main | 仕様管理、差分確認、指摘の反映、完了記録、コミット |
| verifier | ブラウザ操作と全体テストの独立検証 |
| reviewer | 選択状態と既存一括削除への回帰のコードレビュー |

画面の選択状態を変える挙動変更なので、実装、動作検証、コードレビューを
分ける。変更範囲は小さいため、implementer は JavaScript と対応する
ブラウザテストだけを担当する。

依頼と報告:

- [implementer-request.md](implementer-request.md)
- [implementer-report.md](implementer-report.md)
- [verifier-request.md](verifier-request.md)
- [verifier-report.md](verifier-report.md)
- [reviewer-request.md](reviewer-request.md)
- [reviewer-report.md](reviewer-report.md)

# TODO-141 の分担

| 担当 | 範囲 |
| --- | --- |
| implementer | データ処理、HTTP、テンプレート、CSS、JavaScript、テスト、文書の実装と基本確認 |
| main | 仕様管理、実装差分と画面の確認、指摘の反映、完了記録、コミット |
| verifier | 全テストと、一時データを使った選択・確認ダイアログ・一括削除の実測 |
| reviewer | データ保護、入力検証、画面操作、TODO-141 の範囲、テストのレビュー |

データ処理からブラウザ操作まで複数の層にまたがるため、実装を implementer
へ分ける。選択していない行や表示外の行を消さないことは実データ保護に
関わるので、verifier の実測と reviewer のコード確認を別々に行う。

依頼と報告:

- [implementer-request.md](implementer-request.md)
- [implementer-report.md](implementer-report.md)
- [verifier-request.md](verifier-request.md)
- [verifier-report.md](verifier-report.md)
- [reviewer-request.md](reviewer-request.md)
- [reviewer-report.md](reviewer-report.md)

# TODO-111 の分担

- main: テンプレート、JavaScript、ブラウザテストの実装
- verifier: 対象ブラウザテストと全テストの実行による確認
- reviewer: 差分の正しさ、TODO-111 の範囲、既存画面への影響の確認
- wording: 完了コミットに含まれる Markdown の語彙確認

日付入力欄の ID と週切り替え時の処理を変えるため、実装者とは別に動作確認を
行う。ブラウザ側の挙動とテストを同時に変えるので、テスト合格だけで判断せず、
差分のレビューも分ける。

各担当の報告:

- [verifier-report.md](verifier-report.md)
- [reviewer-report.md](reviewer-report.md)
- [wording-report.md](wording-report.md)

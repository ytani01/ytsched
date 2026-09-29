# TODO-206 の分担

| 担当 | モデル | 担当したこと |
|------|--------|--------------|
| implementer | Sonnet 5.5 / medium | 実装（`webapp.py`、テンプレート、`nav.js`、`handler.py` の 403、テスト、`src/README.md`） |
| reviewer | Opus 5.5 / high | POST の経路の漏れ、`nav.js` の cookie 読み取り、403 の画面、テストの強さ |
| verifier | Sonnet 5.5 / medium | lint・型チェック・テスト、壊すと落ちるか（4 か所）、curl での実起動 |

セキュリティの設定を入れ、複数のテンプレートと JS にまたがるので、実装と確認を
分け、挙動が変わる項目として reviewer も入れた。reviewer を先、verifier を後に回した。
reviewer の指摘（テストの追加、403 の文言）は main が直した。

- [implementer-request.md](implementer-request.md) / [implementer-report.md](implementer-report.md)
- [reviewer-request.md](reviewer-request.md) / [reviewer-report.md](reviewer-report.md)
- [verifier-request.md](verifier-request.md) / [verifier-report.md](verifier-report.md)

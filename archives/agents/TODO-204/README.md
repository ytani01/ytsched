# TODO-204 の分担

| 担当 | モデル | 担当したこと |
|------|--------|--------------|
| main | Opus 5.5 / high | 実装（`is_conflict()`、409 の画面、テスト、`src/README.md`） |
| reviewer | Opus 5.5 / high | 判定の条件、`write_error()` の作り、テストの差し替えの妥当さ。直したあとの再レビュー |
| verifier | Sonnet 5.5 / medium | lint・型チェック・テスト、壊すと落ちるか、ブラウザでの再現 |

分岐の条件が変わる項目なので、verifier とは別に reviewer を入れた。
reviewer の指摘で実装が変わることがあるので、reviewer を先、verifier を後に回した。
変更は 5 ファイル程度で main が一人で書ける規模なので、implementer は立てていない。

- [reviewer-report.md](reviewer-report.md)（末尾に再レビュー）
- [verifier-report.md](verifier-report.md)

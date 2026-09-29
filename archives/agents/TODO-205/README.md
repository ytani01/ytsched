# TODO-205 の分担

- main: 実装（1 行の分岐とテスト 1 つ）
- reviewer（Opus 5.5 / high）: 挙動が変わる分岐なので入れた。報告は [reviewer-report.md](reviewer-report.md)
- verifier（Sonnet 5.5 / medium）: テスト・lint・実アプリでの確認と、修正を戻すと落ちるかの実測。報告は [verifier-report.md](verifier-report.md)

reviewer を先、verifier を後に回した。reviewer の 1 回目はセッションの使用上限（429）で止まり、同じ依頼で起動し直した。

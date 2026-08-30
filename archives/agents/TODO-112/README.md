# TODO-112 の分担

main がブラウザーテストと、全テストを通すために古くなっていた HTML の
期待値を修正した。verifier は対象テストの繰り返し実行と全体の確認、reviewer
は待機条件とテスト範囲の確認を担当した。

自動ページ送りの開始・継続・停止をテストで確認するため、実装者とは別に
動作確認を行う。時間に依存する待機条件を変えるので、テストの内容も別に
確認する。

立案時の報告:

- [wording-plan-report.md](wording-plan-report.md)

実装時の報告:

- [verifier-report.md](verifier-report.md)
- [reviewer-report.md](reviewer-report.md)

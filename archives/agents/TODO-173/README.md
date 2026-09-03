# TODO-173 の分担

| 担当 | 誰が | 何を |
|------|------|------|
| 実装 | main | `week.js` / `month.js` の変更、リグレッションテストの追加 |
| 確認 | verifier | lint・型チェック・テスト、ブラウザでの操作確認 |

## この分担にした理由

見込みでは implementer + verifier としていたが、着手時に main のみへ
変えた。原因を突き止めるのに `week.js` / `month.js` / `nav.js` /
`main-page.js` / `keyboard.js` の呼び出し関係を読む必要があり、その
文脈が main に残っている。変更そのものは引数 1 つの追加と受け渡しで、
implementer へ渡すと同じ範囲を読み直させることになる。

**確認は分けた。** ゲージ・`activeMonday`・URL の基準日を変える
変更で、週間表示・検索モード・ブロック送りといった `setActiveWeek()`
を通る他の経路に影響が出ていないかを、別の目で見る必要がある。

## ファイル

- [verifier への依頼](verifier-request.md)
- [verifier の報告](verifier-report.md)

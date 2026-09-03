# TODO-179 の分担

|          | 担当 | 何を任せたか |
|----------|------|--------------|
| 実装     | main | `gauge.js` の `dispGauge()` と、回帰テスト 1 件 |
| 確認     | verifier | lint・全テスト・playwright での実測 |

直すのは `gauge.js` の数行なので、implementer は立てずに main が書いた。
挙動（見た目の動き）が変わるので、確認は verifier に分けた。

- [依頼](verifier-request.md)
- [verifier の報告](verifier-report.md)

TODO 側は
[archives/todo/TODO-179. スライダーから指を離すと、針が一瞬 0 に戻ってから飛ぶ.md](../../todo/TODO-179.%20スライダーから指を離すと、針が一瞬%200%20に戻ってから飛ぶ.md)。

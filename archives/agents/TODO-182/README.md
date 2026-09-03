# TODO-182 の分担

|          | 担当 | 何を任せたか |
|----------|------|--------------|
| 実装     | main | `my.css` の 3 点（帯 50px・`--my-gauge-shift: 0px`・コメント書き直し）と、回帰テスト 1 件 |
| 確認     | verifier | lint・全テスト・playwright での実測（2 回） |

直すのは `my.css` の数行なので、implementer は立てずに main が書いた。
見た目の並びが変わるので、確認は verifier に分けた。reviewer は入れて
いない（分岐は増えず、変わる経路も playwright で全部たどれる）。

verifier は 2 回動かした。

1. 1 回目: 最初 `--my-gauge-shift: 0`（単位なし）で実装したところ、
   `calc(19px + var(--my-gauge-shift))` が無効化されて目盛りの `top` が
   0 に潰れる不具合を発見。あわせて縦位置の回帰テストが無いことを指摘
2. main が `0px` へ直し、回帰テストを 1 件追加。2 回目で、修正の確認と、
   新テストが修正前（単位なしの `0`）で実際に落ちることを確認

- [依頼（追記あり）](verifier-request.md)
- [verifier の報告（2 回分）](verifier-report.md)

TODO 側は
[archives/todo/TODO-182. ゲージを上詰めに戻して、高さを 50px に広げる.md](../../todo/TODO-182.%20ゲージを上詰めに戻して、高さを%2050px%20に広げる.md)。

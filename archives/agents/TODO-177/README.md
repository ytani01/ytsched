# TODO-177 の分担

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort medium | implementer + verifier |
| 実施 | Opus 5 / effort medium | implementer + verifier |

## なぜこの分担にしたか

テンプレート・CSS・JS・テストの 4 つにまたがるので、実装も分けた
（1 ファイルの手直しではない）。確認は決まりどおり別の担当にした。
上下 2 か所に増えることで `id` の重複やリスナーの付け漏れが起きうるので、
ブラウザで実際に押して確かめられる verifier の出番がある。

## 報告

- [implementer-report.md](implementer-report.md) — 変更点と手元での確認
- [verifier-report.md](verifier-report.md) — テスト・lint の結果、
  playwright での実測、残る懸念

## main の判断

verifier が挙げた「上のボタンから `update` などを押す自動テストが無い」
という懸念について、下の帯を押す
`test_update_button_in_bottom_bar_also_submits` を 1 件足した。
既存の 2 件が `.first`（＝上の帯）を押しているので、これで上下とも
リスナーの付け漏れに気づける。`fix` / `add` / `del` は、`update` と
同じ経路（`data-action="submit-cmd"`）なので個別には足していない。

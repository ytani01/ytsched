# TODO-165 の分担

| 担当 | 何を任せたか |
|------|--------------|
| main（Opus 5 / effort high） | 設計と実装、テストの書き換え |
| verifier | 全件テスト・lint・型チェック、ホームボタンのテストの繰り返し実行、起動確認 |
| reviewer（Opus） | sessionStorage の干渉、`doGet` → `doPost` の影響、テストが退行を捕まえる形か |

## この分担にした理由

TODO-164 の実装をやり直す項目で、**前回は reviewer を入れたのに見逃した**
（1 回目のタップを 350 ミリ秒遅らせると、それより遅い 2 回目が読み直しに
飲まれる、という筋を誰も追わなかった）。今回は判定の仕組みそのものを
入れ替えるので、reviewer に Opus を充て、干渉と退行の筋道を名指しで
見てもらった。

verifier には、タイミングに依存するテストを足したぶん、
`-k home_button` を 3 回続けて走らせて skip が出ないかを見させた。

- [verifier の報告](verifier-report.md)
- [reviewer の報告](reviewer-report.md)

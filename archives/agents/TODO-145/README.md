# TODO-145 の分担

| 担当 | 範囲 |
|------|------|
| main | テンプレート・CSS・テストの変更 |
| [verifier](verifier-report.md) | pytest / lint / typecheck / 起動して HTML の実測 |

テンプレートと CSS とテストで数行ずつの変更なので、実装は main で行った。
確認は、実際にアプリを起動して HTML を取れば確かめられるので verifier に分けた。

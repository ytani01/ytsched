# TODO-147 の分担

| 担当 | 範囲 |
|------|------|
| main | テンプレート・CSS・テストの変更、見た目の確認 |
| [verifier](verifier-report.md) | pytest / lint / typecheck、playwright で実際の画面を確認 |

テンプレートと CSS で十数行の変更なので、実装は main で行った。
確認は、アプリを起動して月をまたぐ週・またがない週・検索モードを実際に
見る手順があるので verifier に分けた。

verifier は 2 回に分けて動かした。1 回目が実装（テンプレート・CSS）、
2 回目が後から足したテスト。2 回目は変更が `tests/test_web.py` だけ
なので、全テストの再実行はさせていない。

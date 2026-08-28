# TODO-104 の分担

| 担当 | 何を | なぜ |
|------|------|------|
| main | 仕様の決定（`conf.json` に持たせる、スイッチの位置と見た目）、依頼書、コミット | 決めることは main で済む |
| implementer | `main_handler.py` / `main.html` / `my.css` / テストの実装 | コードとテストと文書がまとまって要るので分ける |
| verifier | lint・型チェック・テスト・一時 datadir での起動確認 | 実装した本人に「動くはず」で済ませない |
| reviewer | 変更の質（分岐の増え方、既定値の扱い、検索モードとの噛み合わせ） | 表示の分岐が増えるため（TODO-103 でも指摘が出た） |
| wording | このコミットに入る `.md` の語 | 報告ファイルを含めて最後に 1 回 |

- 依頼書: [implementer-order.md](implementer-order.md)
- 報告: `implementer-report.md` / `verifier-report.md` / `reviewer-report.md` / `wording-report.md`

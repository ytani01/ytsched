# TODO-183 の分担

| 担当 | 受け持ち | 依頼 | 報告 |
|------|----------|------|------|
| main | 現状の調査と設計（変更する 4 ファイルと、日付の受け渡しの決め方） | — | — |
| implementer | 実装とテストの追加 | [implementer-request.md](implementer-request.md) | [implementer-report.md](implementer-report.md) |
| verifier | fmt / lint / typecheck / pytest の実行、実機（playwright）での確認 | [verifier-request.md](verifier-request.md) | [verifier-report.md](verifier-report.md) |

## この分担にした理由

テンプレート 2 つ・JavaScript 1 つ・ハンドラ 1 つ・テスト 2 つと、
**複数のファイルにまたがる**ので、実装まで分けた
（`~/.claude/CLAUDE.md` の目安どおり）。

確認は、日付が URL を渡り歩くかどうかが要点で、**ブラウザで動かさないと
分からない**（`ytState.activeMonday` が月間表示・検索表示でも入っているか、
フッターのアイコンが実際に押せるか）。TODO-017 の基準の「試せる手順が
あるなら分ける」に当たるので、verifier を立てた。

reviewer は入れていない。既存の分岐を変えるのではなく、日付を持ち回る
経路を足すだけで、挙動の変わる経路は verifier が実機で全部たどれるため。

## 設計を main が決めた理由

「フッターのリンクをどう `data-action` へ移すか」「無指定・不正な日付を
どう扱うか（`None` にして URL に付けない）」は、既存のテストの通り方まで
含めて決める必要があった。実装前に main が読んで決め、依頼書に具体的な
コード片まで書いて渡している。

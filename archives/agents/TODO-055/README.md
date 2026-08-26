# TODO-055 の分担

|  | 担当 | なぜそうしたか |
|---|---|---|
| 実装 | main | 触るのは `main.html` と `my.css`、`main_handler.py` の関数 1 つで、まとまった実装ではない。実装の担当は分けなかった |
| 確認 | verifier | 見た目と操作の変更で、**テストだけでは確かめられない**。ブラウザで押してみるまで分からない |
| レビュー | reviewer | 日付の欄を押したときの動きそのものを変えた。挙動や分岐が変わる項目には入れる（TODO-017） |
| 文書 | wording | `.md` が入るコミットなので立てる（TODO-025・TODO-026） |

依頼書と報告:

- [request-verifier.md](request-verifier.md) / [verifier-report.md](verifier-report.md)
- [request-reviewer.md](request-reviewer.md) / [reviewer-report.md](reviewer-report.md)
- [request-wording.md](request-wording.md) / [wording-report.md](wording-report.md)

reviewer の「ゲージの `centerY`」の指摘を見送った理由は、
[`archives/todo/TODO-055. 週表示に合わせて、ヘッダと日付欄を直す.md`](../../todo/TODO-055.%20週表示に合わせて、ヘッダと日付欄を直す.md)
に書いた。

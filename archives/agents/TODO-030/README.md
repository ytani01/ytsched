# TODO-030 の分担

見込み: main = Opus 5 / effort high、担当 = writer + verifier + wording

## なぜこの分担にしたか

- **writer に実装を分けた。** 新規 2 本（`src/README.md`・`docs/Developer.md`）
  に加えて `CLAUDE.md`・`README.md` の書き換えが入り、複数ファイルにまたがる。
  「実装の担当まで分けるかどうかを規模で決める」の目安に当たる
- **verifier を入れた。** 文書だけの項目だが、`README.md` と
  `docs/Developer.md` には実際に叩けるコマンドが載る。「書いたとおりに試せる
  手順があるなら再現は必ず分ける」（TODO-017）に当たる。あわせて、相互リンクの
  リンク切れと、`CLAUDE.md` から消した記述の移り先があるかも見てもらう
- **wording を入れた。** `.md` が 5 本入るコミットになる（TODO-025・TODO-026）
- **reviewer は入れない。** コードの挙動が変わらず、分岐も条件式も動かない

## 報告

- [writer](writer-report.md)
- [verifier](verifier-report.md)
- [wording](wording-report.md)

# TODO-031 の分担

見込み: main = Opus 5 / effort medium、担当 = writer + verifier + wording

## 誰に何を担当させたか

| 担当 | 範囲 | 報告 |
| --- | --- | --- |
| main | 入れる図の選定（利用者と相談）、報告を見ての採否の判断、コミット | — |
| `writer` | 図の Mermaid ソースを書いて `src/README.md` と `docs/data-format.md` へ埋め込む | [writer-report.md](writer-report.md) |
| `verifier` | 図が実際に描画されるか、図の内容がコードと合っているかの確認 | [verifier-report.md](verifier-report.md) |
| `wording` | コミットに入る `.md` から前例の無い語を挙げる | [wording-report.md](wording-report.md) |

## その分担にした理由

- **文書だけを変える項目なので `implementer` は立てない。** コードには
  一切触れない
- **`writer` と確認の担当を分けた。** コードを変える項目と同じ理由で、
  書いた本人は「合っているはず」で済ませてしまう。図はとくにそうで、
  クラス名や継承関係を 1 つ間違えても文章のようには目立たない
- **`verifier` を立てたのは、確かめられる手順があるから。** Mermaid は
  構文を間違えると GitHub の画面でエラーの箱になる。書式を目で見るだけ
  でなく、実際にパースを通せる（`CLAUDE.md` の「書式の確認だけなら main、
  試せる手順があるなら分ける」に当たる）
- **`wording` は `.md` が入るコミットなので必ず立てる**（TODO-025・
  TODO-026）
- **`reviewer` は立てない。** コードの挙動も分岐も変わらない

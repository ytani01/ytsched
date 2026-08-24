# TODO-042 の分担

|      | main | 担当 |
|------|------|------|
| 見込み | Sonnet 5 / effort medium | main のみ + verifier + wording |

## なぜこの分担にしたか

- **実装は main が行った。** 変えたのは `my.css` の 1 か所
  （`.my-gage-text` に `--fa-width: auto;`）だけで、原因も直し方も
  項目を立てる段階で分かっていた。implementer を立てても、依頼書を書く
  手間のほうが大きい
- **確認は verifier に分けた。** コードやファイルを変える項目では、
  規模によらず確認を別の担当にする決まりがある。今回はとくに、直った
  ことを画面で見ないと分からない種類の変更で、実装した本人は「CSS の
  指定どおりに効いているはず」で済ませてしまう
- **`.md` が入るので wording を立てた。** 項目を立てるコミットで 1 回、
  済ませるコミットでもう 1 回

## 報告

- [wording の報告](wording-report.md) — 項目を立てるコミット
- [verifier への依頼](verifier-request.md)
- [verifier の報告](verifier-report.md)

TODO 項目そのものは
[archives/todo/TODO-042. 左端のゲージの針の位置がずれているのを直す.md](../../todo/TODO-042.%20左端のゲージの針の位置がずれているのを直す.md)。

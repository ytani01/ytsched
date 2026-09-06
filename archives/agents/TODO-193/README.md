# TODO-193 の分担

## 誰に何を担当させたか

| 担当 | 何を |
|------|------|
| main | `.claude/hooks/fmt-one.sh` の実装、`.claude/settings.json` への登録、簡単な動作確認 |
| verifier（Sonnet 5） | 対象外のファイルで走らないこと、想定外の入力で落ちないこと、フックが有効な状態での連続編集 |

- [verifier の報告](verifier-report.md)

## その分担にした理由

シェルスクリプトで、挙動がある。文書だけの項目ではないので、確認は main から
分けた（TODO-192 と同じ理由）。実装は 1 ファイルなので implementer は立てず、
main が書いた。

reviewer は立てていない。新規のフックで、既存の分岐や条件式を変える項目では
ないため。

## やり取りの回数

verifier は 1 回で終わった。不具合の指摘は無し。

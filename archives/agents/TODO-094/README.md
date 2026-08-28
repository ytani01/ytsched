# TODO-094 の分担

## 誰にどこを

- **implementer は使わず、main が実装した。** 3 件とも 1〜数行の
  機械的な変更（改名・引数削除・フラグ名）で、複数ファイルにまたがる
  設計判断は無い。常設の基準（実装を分けるのは「複数ファイル・実装と
  テストと文書がまとまって要る」項目）に届かない規模。
- **verifier**（Sonnet 5 / 定義ファイル参照）。改名の追随漏れ、二重
  照合を外したことによる挙動変化、`--help` の表示を確認。依頼書は
  [verifier-request.md](verifier-request.md)、報告は
  [verifier-report.md](verifier-report.md)。
- **wording**（Sonnet 5 / 定義ファイル参照）。コミットに `.md`
  （`archives/todo/TODO-094. 細かいもの.md`、この README、各報告）が
  入るため、前例の無い語を挙げさせた。報告は
  [wording-report.md](wording-report.md)。

## 見込みとの違い

見込みの担当は verifier だけだった。着手時、コミットに `.md` が入る
ことから wording を足した（`.md` が入るコミットでは wording を立てる、
という運用どおり）。

# TODO-107 の分担

計画時は main が現行コードと ESLint の指摘を調べ、verifier が JavaScript の
依存関係、TODO-108 との境界、検証方法を確認した。wording は計画時の Markdown
を確認した。

実装時は、JavaScript の公開範囲を複数ファイル・テンプレート・ブラウザテストで
揃えるため、実装を implementer、実際の動作確認を verifier、変更内容の確認を
reviewer に分けた。実装者だけでは、公開名の取り残しやブラウザ上の例外を見逃す
おそれがあるため。implementer が中途で停止した後の実装は main が引き継いだ。

計画確認時の報告:

- [verifier-plan-report.md](verifier-plan-report.md)
- [wording-plan-report.md](wording-plan-report.md)

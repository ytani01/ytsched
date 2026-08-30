# TODO-106 の分担

`MainHandler` から引数解析と表示データの組み立てを分けるため、実装を
implementer、実際の動作確認を verifier、責務境界と既存挙動の確認を
reviewer に分けた。実装者以外が、設定の保存・入力エラー・週表示に
退行がないことを確認するためである。

- [implementer-report.md](implementer-report.md)
- [verifier-report.md](verifier-report.md)
- [reviewer-report.md](reviewer-report.md)

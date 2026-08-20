# TODO-016 の分担

見込み: main = Opus 5 / effort medium、担当 = implementer + verifier

## なぜこの分担にしたか

`main_handler.py` と `edit_handler.py` の 2 ファイルにまたがり、
テストの追加も要る。実装と確認を分ける決まりに従い、
実装を `implementer`、確認を `verifier` に割り当てた。
レビューを足すほど込み入った変更ではないと判断した。

## 報告

- [implementer](implementer-report.md)
- [verifier](verifier-report.md)

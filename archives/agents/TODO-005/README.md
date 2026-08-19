# TODO-005 の分担

見込み: main = Opus 5 / effort medium、担当 = implementer + verifier + reviewer

## なぜこの分担にしたか

直す箇所が 4 ファイル（`ytsched.py` / `handler.py` / `main_handler.py` /
`webapp.py`）とテストにまたがり、削除・データの保存・例外処理・挙動の
変更が混ざる。実装を `implementer` に分けた。

データが失われる不具合（`save()` がファイルを消す、`load()` が
`IndexError`）を含むので、確認は 2 系統に分けた。`verifier` に
「テストが通るか・アプリが起動するか」を、`reviewer` に
「直し方が正しいか・直したつもりで直っていない箇所が無いか」を見せる。

## 報告

- [implementer](implementer-report.md)
- [verifier](verifier-report.md)
- [reviewer](reviewer-report.md)

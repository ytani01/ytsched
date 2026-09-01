# TODO-148 の分担

## 分担にした理由

テンプレート 3 つ（`sde.html`・`main.html`・`trash.html`）、CSS、テストに
またがるので、実装を implementer に分けた。`sde.html` は週間・月間・検索の
すべてで使われていて、受け取る変数を増やす影響が広い。`main.html` 側の設定
漏れは実行時まで出ないので reviewer を入れた。表示の確認（テスト・lint・
ブラウザテスト）は verifier が行う。

## 報告

- [implementer](implementer-report.md)
- [verifier](verifier-report.md)
- [reviewer](reviewer-report.md)

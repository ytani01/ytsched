# TODO-116 の分担

implementer が実装とテストの追加、verifier が確認を担当した。

JavaScript (`main-page.js`)、テンプレート (`main.html`)、ブラウザーテスト
(`tests/test_browser.py`) にまたがるので、実装を分けた。挙動そのものを
変えるが、検索モードの分岐を 1 つ足すだけで、設計の判断は項目を立てる
段階で済んでいたため reviewer は入れていない。

verifier には、テストが通ることだけでなく **実装の分岐を壊したときに
実際に落ちるか** を確かめさせた。追加したのが「押したら日付が動く」と
いう類いのテストで、書き方によっては何も見ていなくても通ってしまうため。

報告:

- [implementer-report.md](implementer-report.md)
- [verifier-report.md](verifier-report.md)

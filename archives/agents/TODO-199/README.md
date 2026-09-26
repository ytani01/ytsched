# TODO-199 の分担

項目: [TODO-199. ホームボタンで今日が画面の下にはみ出す](../../todo/TODO-199.%20ホームボタンで今日が画面の下にはみ出す.md)

| 担当 | やったこと | 報告 |
|------|-----------|------|
| main | 実装・テストの追加 | — |
| reviewer | 差分のレビュー | [reviewer-report.md](reviewer-report.md) |
| verifier | lint・型チェック・テスト、PC とスマホの画面サイズでの実測（2 回） | [verifier-report.md](verifier-report.md) |

## この分担にした理由

- 変更は JS の 2 ファイルとテストで小さいので、実装は main が持った
- スクロール位置の分岐が変わるので reviewer を入れた
- 利用者から「画面サイズが変わっても、PC でもスマホでも大丈夫か」と
  聞かれたので、verifier に 3 つの画面サイズで測らせた
- reviewer を先、verifier を後に回した

計測スクリプトは [verifier-todo199_check.py](verifier-todo199_check.py)。

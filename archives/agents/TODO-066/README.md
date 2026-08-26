# TODO-066 の分担

| 担当 | 何を見たか | 報告 |
|------|-----------|------|
| main | 実装（テンプレート・CSS・JavaScript・テスト・文書） | — |
| verifier | テスト・lint・型チェックの実行と、実際の画面の確認 | [verifier-report.md](verifier-report.md) |
| wording | コミットに入る `.md` の、前例の無い語 | [wording-report.md](wording-report.md) |

## この分担にした理由

- **実装は main で足りる。** 触るのは週バーの周りだけで、テンプレート・
  CSS・JavaScript が 1 か所ずつ。設計を分けて考えるところが無い
- **確認は分けた。** 見た目の変更は「テストが通ること」では確かめられず、
  実際に画面を見るしかない（TODO-042・TODO-043・TODO-045 と同じ）。
  実装した本人は「動くはず」で済ませてしまう
- **reviewer は入れていない。** 分岐や挙動の判断を変えていない
  （`calc_week_diff()` も `days2xPercent()` もそのまま）。位置と文字の
  出し先を移しただけ

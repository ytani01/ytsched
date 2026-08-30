# TODO-127 の分担

変更が `sched_update.py` の 1 分岐に収まる小さな規模だったため、実装は
main が行い、確認だけ verifier に分けた。

- **main** — `sched_update.py` の実装、`test_web.py` のテスト追加、
  lint・型チェック・pytest の実行
- **verifier** — [verifier-report.md](verifier-report.md)。lint・型
  チェック・pytest の再実行、ロジックと追加テストの確認。半角 `#` +
  全角数字がマッチしてしまう不具合を見つけた（`main` が修正し、修正後の
  確認は `main` 自身の lint・型チェック・pytest 実行で済ませた。
  修正内容の規模が小さく、verifier を再度立てるほどではないと判断した）

# TODO-187 の分担

ゲージ（スライダー）を、ヘッダーに加えてフッターの直上にも出した項目。
テンプレート・CSS・JavaScript 3 ファイル・テストにまたがる。

- **implementer**（[依頼](implementer-brief.md) /
  [報告](implementer-report.md)）— 複数のファイルにまたがり、
  `gauge.js` を「ゲージが複数ある前提」へ直す設計が要るので分けた。
  定義のモデルは sonnet だが Opus 5 に上書きした。
  **2 回目の依頼（reviewer の指摘への対応）は Opus のセッション上限で
  落ちたので、その分は main が直接直した**（報告の末尾に節を足してある）
- **reviewer**（[依頼](reviewer-brief.md) / [報告](reviewer-report.md)）—
  挙動が変わる項目なので入れた。定義のモデルは sonnet だが Opus 5 に
  上書きした。4 点の指摘のうち 3 点を採った
- **verifier**（[依頼](verifier-brief.md) / [報告](verifier-report.md) /
  [報告 2](verifier-report2.md)）— テスト・lint・実機での動作確認。
  reviewer の指摘に対応したあと、もう一度動かした

項目そのものは
[archives/todo/TODO-187](../../todo/TODO-187.%20ゲージ（スライダー）を、フッターの直上にも出す.md)。

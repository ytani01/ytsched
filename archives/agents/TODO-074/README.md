# TODO-074 の分担

| 担当 | やらせたこと |
|------|------|
| wording | 項目を立てるコミットに入る `TODO.md` の文言 |
| implementer | `my.js` / `main.html` / `my.css` / `tests/test_browser.py` の実装 |
| verifier | lint・テスト・ブラウザでの動作確認 |

- 変更が JavaScript・テンプレート・CSS・テストの 4 ファイルにまたがり、
  既存のスワイプ処理との兼ね合いを読む必要があったので、**implementer を
  分けた**
- 動かしてみないと分からないこと（クリック位置と移動先が合っているか、
  既存のスワイプが壊れていないか）が中心なので、**verifier を分けた**。
  実際、押している間に帯が黄色一色になって目盛りが読めなくなる件は
  verifier の指摘で、これを受けて色を変えた
- reviewer は立てなかった。既存の関数の逆算を足すだけで、分岐や既存の
  挙動を変える変更ではないため

## ファイル

- [implementer への依頼](implementer-task.md) / [報告](implementer-report.md)
- [verifier への依頼](verifier-task.md) / [報告](verifier-report.md)
- [wording の報告](wording-report.md)

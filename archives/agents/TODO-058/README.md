# TODO-058 の分担

|  | 担当 | なぜそうしたか |
|---|---|---|
| 実装 | implementer | `main_handler.py`・`main.html`・`my.css`・`my.js`・テストの 5 種類にまたがる。**Python と JavaScript で同じ式を 2 か所に書く**必要もあり、まとまった実装になる |
| 確認 | verifier | 見た目と動きの変更で、**テストだけでは確かめられない**。針が動くこと・360px でラベルが重ならないことは、ブラウザで見るまで分からない |
| レビュー | reviewer | 縦ゲージを丸ごと置き換えた。挙動や分岐が変わる項目には入れる（TODO-017） |
| 文書 | （立てない） | **`wording` は立てないと利用者が決めた**（2026-08-26。TODO.md の TODO-058 に記載） |

設計（式・ラベル・DOM の置き場所・CSS の一式）は main が決めて
[request-implementer.md](request-implementer.md) に書き、implementer には
そのとおりに作らせた。数値（px・色）だけキャプチャを見て詰めてよいことにした。

依頼書と報告:

- [request-implementer.md](request-implementer.md) / [implementer-report.md](implementer-report.md)
- [request-verifier.md](request-verifier.md) / [verifier-report.md](verifier-report.md)
- [request-reviewer.md](request-reviewer.md) / [reviewer-report.md](reviewer-report.md)

## 報告について、main が判断したこと

- **implementer が `tests/test_web.py` の `TestWeekBar.week_bar()` の
  切り出し範囲を狭めた件**（依頼書の範囲外）は、そのまま採った。横ゲージの
  ラベルを `#week_bar` の中に置いた直接の結果で、DOM の置き場所のほうは
  仕様どおりのため
- **reviewer の報告 3 に「`.my-gage-r-no-transition` はクラス 1 つのまま」と
  あるのは、報告側の書き誤り。** 実際は `.my-gage-r.my-gage-r-no-transition`
  （クラス 2 つ）のまま残っていて、TODO-049 の指摘どおりの形。直すところは
  無かった

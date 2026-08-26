# TODO-056 の分担

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort medium | main のみ + verifier |
| 実施 | Opus 5 / effort high | main + verifier + wording |

## なぜこの分担にしたか

- **実装は main。** 変更したのは `tests/test_browser.py` 1 ファイルと、
  文書・`mise.toml` の付随的な書き換えだけ。複数のファイルにまたがる
  実装ではないので、implementer は立てなかった
- **verifier は必ず立てる。** この項目は「テストが退行を捕まえるか」が
  すべてで、**書いた本人が自分のテストを走らせて通ったことは、その
  裏付けにならない**。my.js をわざと壊して落ちるかを、独立に確かめさせた
- **reviewer は立てなかった。** アプリの挙動や分岐は変えておらず、
  読むべきコードはテスト 1 ファイル。「挙動や分岐が変わる項目には入れる」
  （TODO-017）に当たらない
- **wording は `.md` が入るので立てた**（TODO-025・TODO-026）

## 報告

- [request-verifier.md](request-verifier.md) / [verifier-report.md](verifier-report.md)
- [request-wording.md](request-wording.md) / [wording-report.md](wording-report.md)

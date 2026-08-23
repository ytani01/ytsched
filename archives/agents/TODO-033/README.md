# TODO-033 の分担

項目は
[TODO-033. URL_PREFIX の改名に追随できていない箇所を直す](../../todo/TODO-033.%20URL_PREFIX%20の改名に追随できていない箇所を直す.md)。

## 誰に何を担当させたか

| 担当 | 依頼書 | 報告 |
|---|---|---|
| wording | （main が口頭で依頼） | [wording-report.md](wording-report.md) |
| implementer | [implementer-request.md](implementer-request.md) | [implementer-report.md](implementer-report.md) |
| verifier | [verifier-request.md](verifier-request.md) | [verifier-report.md](verifier-report.md) |

## その分担にした理由

- **reviewer は入れていない。** 識別子の改名に追随するだけで、分岐も
  条件式も変わらない。`CLAUDE.md` の「整形、依存関係の更新、文書だけの
  項目には要らない」に当たる
- **implementer を立てるかは迷った。** 3 か所の機械的な置き換えなので、
  `CLAUDE.md` の「実装の担当まで分けるかどうかを、規模で決める」に
  照らせば main がやってもよかった。項目を立てるときに
  implementer + verifier と決めて利用者の承認を得ていたので、
  そのまま通した。**振り返ると、ここは main で足りた**
- **verifier は分けた。** 「テストが全件通る」ことが項目の目的そのもの
  なので、実装した本人の申告で済ませない
- **wording は、TODO.md をコミットする前に立てた。** `.md` が入る
  コミットなので。`全滅` `コレクション段階` の 2 語を指摘され、
  「テストを集める段階で失敗し、1 件も実行できない」に書き換えた。
  `改良案`（TODO-032、利用者が書いた節）はそのままにした

## この項目で分かったこと

- **verifier の報告は、担当した項目の外にも及ぶ。** この項目自体、
  TODO-027 の verifier が「範囲外だが動かない」と報告してきたことから
  始まった。依頼書の範囲だけを見て「不具合なし」と返させない書き方が
  効いている
- **main が依頼書に書いた事実が間違っていることがある。** CLI の
  オプション名を `--url-prefix` と書いたが、実物は `--urlprefix`
  だった。verifier が実物を読んで気づいた

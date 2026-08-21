# TODO-026 の分担

見込み: main = Opus 5 / effort high、担当 = implementer + verifier + reviewer

## なぜこの分担にしたか

- **implementer** — 定義ファイル 1 つ、hook スクリプト 1 つ、
  `settings.json` 1 つと複数のファイルにまたがる。`CLAUDE.md` の
  「実装の担当まで分けるかどうかを、規模で決める」に当てはまる
- **verifier** — hook は動くものなので、書式を見るだけでは足りない。
  「書いたとおりに発火するか」を実際に試す必要がある（TODO-017 の
  「試せる手順があるなら分ける」）
- **reviewer** — hook が誤って止める・黙って発火しない、はテストが
  通ることを見ても捕まらない。TODO-026 の「気をつけること」に明記が
  ある

`runner` は使わない。この項目には lint・型チェック・テストの対象になる
Python のコードが無い。

## 決めたこと（着手時）

- **定義は 6 個にする。** `runner` を `verifier` に畳むのは無理。
  TODO-022 で実測して「決まった手順を流すだけ＝runner、実際に叩いて
  確かめる＝verifier」と決着済みで、蒸し返す材料が無い
- **hook は止めない。** exit 0 + JSON の `systemMessage` /
  `additionalContext` だけを返し、`permissionDecision` は返さない
- **新しい担当の名前は `wording`。** 利用者が決めた
- **`wording` は sonnet / effort medium。** 仕事は「語を拾う →
  `git grep` で前例を見る → 前例の無い語を全部挙げる」で、一般に通用
  する語かの最終判断は main がする（TODO-025 で決めたこと）

## 報告

- [implementer-report.md](implementer-report.md)
- [verifier-report.md](verifier-report.md)
- [reviewer-report.md](reviewer-report.md)

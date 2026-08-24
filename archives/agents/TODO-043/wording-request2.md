# wording への依頼（TODO-043 を済ませるコミット）

前回（項目を立てるコミット）の報告は `wording-report.md` にある。
**今回はその続き**なので、報告は同じファイルの末尾に

```
---

## 済ませるコミット
```

という節を作って追記すること（新しいファイルを作らない）。

## 見てほしいファイル

このコミットに入る `.md` は次の 6 つ。**担当の報告ファイルも対象**。

- `archives/todo/TODO-043. ゲージの針と基準線を、アイコンフォントでなく図形で描く.md`（新規）
- `TODO.md`（節を archives へ移し、目次に足した差分）
- `archives/agents/TODO-043/README.md`（新規）
- `archives/agents/TODO-043/verifier-request.md`（新規）
- `archives/agents/TODO-043/verifier-report.md`（新規）
- `archives/agents/TODO-043/runner-report.md`（新規）

基準は `HEAD`（`5c7d18f`）。

## やること

このリポジトリに前例の無い語を挙げる。候補は十数語に絞り、それぞれに
見立て（一般に通用する専門用語か、造語に近いか、既にある語で置き換え
られるか）を添える。**文書は直さない。** 決めるのは main。

今回はフォント・SVG・画像処理の用語が多く出てくる
（`unitsPerEm`、`viewBox`、`polygon`、`bbox`、`アンチエイリアス`、
`グリフ`、`字面` など）。**前例なし ＝ 造語ではない**ので、そこは
見立てで分けてほしい。

`字面`・`グリフ`・`left side bearing` は TODO-042 で「そのまま使う」と
決めた語なので、挙げなくてよい。

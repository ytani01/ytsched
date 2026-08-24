# TODO-040 wording への依頼

TODO-040（bootstrap, fontawesome のバージョンアップ）のコミットに入る
`.md` から、**このリポジトリに前例の無い語**を挙げてほしい。

## 対象

このコミットに入る `.md` 全部。ステージ済みなので、こう拾える。

```sh
git diff --cached --name-only -z -- '*.md' | tr '\0' '\n'
```

いま入っているのは 8 つ（この依頼書自身を入れると 9 つ）。

- `README.md`
- `TODO.md`
- `archives/todo/TODO-040. bootstrap, fontawesomeのバージョンアップ.md`
- `archives/agents/TODO-040/README.md`
- `archives/agents/TODO-040/implementer-request.md`
- `archives/agents/TODO-040/implementer-report.md`
- `archives/agents/TODO-040/verifier-request.md`
- `archives/agents/TODO-040/verifier-report.md`
- `archives/agents/TODO-040/wording-request.md`（この依頼書）

**担当の報告ファイル 2 つ（`implementer-report.md` /
`verifier-report.md`）を外さないこと。**

## 前例があるかの調べ方

基準は `HEAD`（`b9579b5`）。

```sh
git grep -cF <語> HEAD -- '*.md'
```

`TODO.md` は `b9579b5` の時点で TODO-040 の節を含んでいる。その節に
初めて出てくる語は「前例あり」と数えられてしまうので、**`b9579b5` で
足した語かどうかが疑わしいときは `b9579b5^` でも見てほしい**。

## 見てほしいところ

この項目は、CSS フレームワークの版を上げる話。**版数・クラス名・
ファイル名（`text-start` `fw-bold` `woff2` `--bs-body-font-family` など）
は用語ではないので、挙げなくてよい。**

気にしてほしいのは、状態や現象を指す呼び名のほう。今回は特に、
画素単位の比較の結果を説明する言い回しが多い。

## 出してほしいもの

- **候補を十数語に絞る。** 全部挙げると読めない
- 各語に、どのファイルの何行目で使っているかと、**見立て**
  （造語だと思う／一般に通用する専門用語だがこのリポジトリでは初出、など）
- 言い換えの案があれば添える

報告は `archives/agents/TODO-040/wording-report.md` に。返事は 5 行以内。

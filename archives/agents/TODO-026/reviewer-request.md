# reviewer への依頼（TODO-026）

`~/work/ytsched/TODO.md` の TODO-026 と、
`archives/todo/TODO-025. 文書の確認を分ける仕組みを決める.md` の
「決めたこと」、`archives/agents/TODO-026/implementer-request.md`（仕様）、
`archives/agents/TODO-026/implementer-report.md`（実装の報告）を
**先に読むこと**。

`git status` と `git diff` で変更範囲を把握してから読む。

## 見てほしいこと

TODO-026 の「気をつけること」に、この項目で reviewer を入れる理由が
書いてある。**「hook が誤って止める・黙って発火しない」はテストが通る
ことを見ても捕まらない**、という点。

- **誤って止める経路が無いか。** `.claude/hooks/check-md-commit.sh` が
  0 以外の終了ステータスを返す経路、`permissionDecision` や
  `exit 2` を返す経路。`set -e` / `set -o pipefail` と、失敗しうる
  コマンド（`git`・`jq`）の組み合わせ。stdout に JSON 以外の文字が
  混ざる経路（`{` で始まらないと JSON として読まれず、`{` で始まって
  壊れていれば別の問題になる）
- **黙って発火しない経路が無いか。** `git commit` の書き方の違い
  （`-a`、`--amend`、`-m` を後ろに置く、`git -C … commit`、
  `&&` でつなぐ、改行を含む）。`.md` の拾い方（`--cached` だけで
  足りるか、大文字の `.MD`、パスに `.md` を含むディレクトリ名）。
  `matcher` と `if` の書き方で漏れる経路
- **仕様からの逸脱** — `implementer-request.md` と TODO-025 の
  「決めたこと」に対して、`.claude/agents/wording.md` の内容が
  ずれていないか。特に「既知語リストは持たない」「文書は直さない」
  「対象は報告ファイルを含む `.md` 全部」の 3 つ
- **`wording.md` の定義が、既存 5 個と役割の線引きで衝突していないか。**
  `reviewer`（コードの質）・`writer`（文書を書く）と重なっていないか
- **既にあるものの再実装** — シェルで自前に組んでいるが `git` や `jq`
  の機能で済むもの

## 見ないもの

- 好みの問題（変数名の趣味、コメントの多寡）
- 文書の日本語の文体
- `wording` が実際に「足場」を挙げるかどうか（`verifier` の担当）

## 決まりごと

- **コードも定義も直さない。** 指摘するだけ
- **書き込んでよいのは自分の報告ファイルだけ**
- 確信度の高い指摘を先に。低いものは節を分けて後ろに置き、
  確信度が低いと明記する
- **git commit / git tag はしない**
- **`TODO.md` は編集しない**
- 報告は `archives/agents/TODO-026/reviewer-report.md`。
  返事は 5 行以内

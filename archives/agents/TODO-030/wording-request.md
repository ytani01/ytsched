# 依頼: TODO-030 の文書の語の確認（wording）

このコミットには `.md` が 9 本入る。**このリポジトリに前例の無い語**を
挙げてほしい。文書は直さないこと。

対象（`git status --short` と `git diff --name-only` で確認できる）:

- 新規: `src/README.md`、`docs/Developer.md`、`tests/README.md`
- 変更: `CLAUDE.md`、`README.md`、`docs/data-format.md`、`TODO.md`
- 依頼・報告: `archives/agents/TODO-030/` の全 `.md`
  （`README.md`、`writer-request.md`、`writer-report.md`、
  `verifier-request.md`、この `wording-request.md`、`verifier-report.md`）

**担当の報告ファイルも対象に含める**（TODO-021 では報告ファイルに入っていた
造語が見逃された）。

## 見かた

前例の有無は、**変更前の状態**と突き合わせて調べる。
`git stash` は使わず、`git show HEAD:<path>` や、変更されていない
ファイル群（`archives/todo/` 配下、`src/`、`tests/`）への `grep` で見る。

**前例なし ＝ 造語ではない。** 一般に通用する専門用語でも、このリポジトリ
では初出になる。候補を**十数語に絞り**、それぞれに次を添える:

- どのファイルの何行目に出るか
- 前例があるか（あるならどこに）
- 見立て（一般的な専門用語か / 言い換えたほうがよさそうか /
  既にこのリポジトリで使われている別の語があるか）

**決めるのは管理者**なので、直さず挙げるだけでよい。

特に気をつけて見てほしいもの:

- 短く言おうとして作った独自の言い換え（過去に「足場」「全緑」「鳴動」
  「終了コード契約」のような例があった）
- 英語からの直訳になっている言い回し
- 同じものを指すのに、文書ごとに違う語を使っている箇所
  （6 文書に分けたので起きやすい）

## 報告

`archives/agents/TODO-030/wording-report.md` に書く。
返事は「終わったか・報告ファイルのパス・判断が要る点」の 5 行以内。

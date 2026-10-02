# TODO-214. 担当の定義を、ユーザー全体の定義と CLAUDE.md に合わせる

`TODO.md` での見出しは「担当の定義を、ユーザー全体の定義と
`~/.claude/CLAUDE.md` に合わせる」。ファイル名に `/` を使えないので縮めた。

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5.5 / effort medium | main のみ |
| 実施 | Opus 5.5 / effort medium | main のみ |

| 担当 | モデル | effort | input | output | cache_creation | cache_read | 割合 |
|------|--------|--------|-------|--------|----------------|------------|------|
| main | Opus 5.5 | medium | 20 | 4,026 | 9,002 | 938,410 | 100% |
| 合計 |  |  | 20 | 4,026 | 9,002 | 938,410 | 計 951,458 |

- `check-agent-reply.py` が別プロセスで起動した `claude -p`（reviewer・
  verifier の 2 回）は、この集計に入っていない

## きっかけ

ytsched の `.claude/agents/` は、`~/.claude/agents/` の同じ名前の定義を
全文で置き換える。そのため、ユーザー全体の定義に後から足された内容が
ytsched には届いていなかった。`~/.claude/CLAUDE.md` の「テストは『壊すと
落ちるか』を確かめさせる」に当たる手順も、verifier に無かった。

## やったこと

利用者と決めた範囲で、`.claude/agents/` の 3 つを直した。

- `reviewer.md`
  - frontmatter に `skills: [ponytail:ponytail-review]` を足し、「見るもの」に
    作り込みすぎとテストの観点を足した
  - 「事前レビュー（実装の前に呼ばれたとき）」の節を足した
  - 指摘に重大度（要修正／検討／好みの範囲）を付けるようにした。
    「確信度の高い指摘に絞る」と「見ないもの」は残し、「好みの範囲」には
    「見ないもの」を挙げないと書いた
- `verifier.md`
  - どの確認でも最初に `git status` と `git diff --stat` を見て、依頼に無い
    ファイルの変更を報告するようにした（定型の実行は除く）
  - 「壊すと落ちるかを見る」の節を足した。このときだけ作業ツリーを
    書き換えてよい。一時ディレクトリへ複製して書き戻し、`git stash` /
    `git checkout` / `git restore` は使わない（実装者のまだコミットして
    いない変更を巻き込むため）
- `implementer.md` と `reviewer.md` から「`~/work/tmr` と揃える」を削った
  （利用者の判断で、もう揃える先ではない）

残したもの: verifier の「原因の切り分けをしない」（ユーザー全体の定義の
「推定を書くのはよい」は `~/.claude/CLAUDE.md` と食い違う）と、wording の
役割（前例の無い語を挙げる）。

## 確かめたこと

- `~/.claude/bin/check-agent-reply.py --agent reviewer` と
  `--agent verifier` がどちらも「合格」（返事は 5 行と 3 行）
- reviewer の frontmatter が `skills:` を含めて YAML として崩れていないことを
  目で見た
- 定義は Claude Code の再起動まで、このセッションには効かない（再起動は利用者）

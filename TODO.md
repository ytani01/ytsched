# TODO

**残っている項目: TODO-201。** これまでに 200 件を決着させた。
新しく足すときは「完了済み」の上に節を作る。
**番号は `TODO-202` から**。

着手する項目は利用者が指定する。**並び順に優先度の意味は無い。**

---

## TODO-201. エージェント設定ファイルの古い記述を直す

|      | main | 担当 |
|------|------|------|
| 見込み | Sonnet 5 / effort medium | main（編集）+ verifier（Sonnet 5 / medium） |

- [ ] `.agents/skills/ytsched-workflow/SKILL.md:35-36` の完了手順を、
      `archives/todo/` へ 1 項目 1 ファイルで移す形に直す
      （今は「目次（`## 完了済み`）へ移動」と書いてあり、`TODO.md` と食い違う）
- [ ] `.claude/agents/writer.md:15` の「実際に `ls` する」を
      `git ls-files` か `find` に直す（Bash ツールの `ls` は何も出さない）
- [ ] `.claude/agents/implementer.md:18` と `.claude/agents/verifier.md:57` の
      `grep` を `rg -n` に直す（`~/.claude/CLAUDE.md` の「`grep` ではなく `rg`」）
- [ ] `CLAUDE.md:54-56` の `ytsched.py` の行番号を外し、クラス名だけにする
      （編集のたびにずれる）
- [ ] verifier に、書き換えたコマンド例（`rg -n`、`git ls-files`、`find`、
      `~/.claude/bin/todo-index.py`）を書いたとおりに叩かせて確かめる

`/claude-api prompt-audit`（2026-09-27）で見つかった 4 件。直す文面は
監査のときの diff をそのまま使う。

- 文書と定義ファイルだけの変更なので、レビューの担当は入れない。
  コマンド例は書いたとおりに試せるので、その再現は verifier に分ける
- `.agents/agents/*.md` は `.claude/agents/<role>.md` を読む形なので、
  Codex 側は直さなくてよい
- `.claude/agents/*.md` を直したら、Claude Code の再起動が要る（利用者が行う）
- 監査で Low とした `writer.md:20-28`（全体の「日本語の書き方」の書き写し）は
  この項目に入れない。今は中身が一致していて実害が無い

---

## 完了済み

決着した項目は `archives/todo/` にある（1 項目 1 ファイル）。
一覧は [archives/index.md](archives/index.md)（新しい順）。やらないと決めたものは
ファイル名に（対応しない）が付いていて、理由も書いてある。蒸し返す前に読むこと。

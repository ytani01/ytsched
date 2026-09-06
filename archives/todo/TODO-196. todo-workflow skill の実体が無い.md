# TODO-196. `todo-workflow` skill の実体が無い

|      | main | 担当 |
|------|------|------|
| 見込み | Opus 5 / effort high | main のみ |
| 実施 | Opus 5 / effort high | main のみ |

| 担当 | モデル | effort | output | cache_creation | 料金の割合 |
|------|--------|--------|--------|----------------|-----------|
| main | Opus 5 | high | 12,123 | 49,734 | 100% |
| 合計 |  |  | 12,123 | 49,734 | 概算 $1.2 |

- 直す先が `~/.claude`（`dotfiles-claude`）だけで、変えたのは skill 1 本と
  `.gitignore` 1 行。確かめる中身が「消えた行が漏れなく移っているか」しか
  無いので、担当は `main のみ`

## きっかけ

`~/.claude/CLAUDE.md` が 2 か所で「仕様は `todo-workflow` skill」と参照して
いるのに、`~/.claude/skills/` というディレクトリ自体が無かった。
このプロジェクトの `TODO.md` と `archives/todo/` の書式が拠り所を失っていた。

## やったこと

### skill が一度も作られていなかったことを確かめた

- `~/.claude/skills/` は無く、`plugins/` の下にも `todo-workflow` は無い。
  ytsched 側の `.claude/` にも `skills/` は無い
- `~/.claude` の `daf4954`（2026-09-07「docs: TODO の書式を todo-workflow
  skill へ移す」）は、`git show --stat` で見ると**変更対象が `CLAUDE.md`
  1 ファイルだけ**。169 行を削って 8 行に置き換えただけで、移す先を
  作っていなかった。`git log --all --diff-filter=A -- '*todo-workflow*'`
  でも追加の履歴が出ない

### 消えた 169 行を skill として書き直した

置き場所は利用者に確かめ、**skill として作り直す**ことにした
（`daf4954` の「`CLAUDE.md` には進め方の規則だけを残す」意図をそのまま活かす。
書式は必要なときだけ読み込まれるので、常時のトークンも増えない）。

`git show daf4954 -- CLAUDE.md` の削除行を取り出し、
`~/.claude/skills/todo-workflow/SKILL.md`（191 行）に移した。節の構成は:

- `TODO.md` の骨格
- `archives/todo/` のファイルの形（見込みと実施の表、見込みの行の書き方）
- 消費トークンの表と `token-usage.py` での集計
- 分担の振り返り
- サブエージェントの定義（`.claude/agents/*.md`）

`CLAUDE.md` 側の参照（2 か所）はそのままで、直していない。

### `.gitignore` に `skills/` の許可を足した

`~/.claude/.gitignore` はホワイトリスト方式（`*` で全部無視してから
`!` で許可する）なので、置いただけでは追跡されなかった。`agents/` と
同じ形で、**`skills/*/*.md` に限って**許可する 5 行を足した。

## 確かめたこと

削除された 169 行の 1 行ずつが、新しい `SKILL.md` か現行の `CLAUDE.md` の
どちらかに残っているかを機械的に照合した（`grep -qxF`）。
一致しなかったのは次の 2 行だけで、どちらも意図した差分:

- `` `TODO.md` の骨格: `` — skill では見出し `## `TODO.md` の骨格` にした
- `常設の定義（下記）で足りるなら` — `daf4954` が
  `常設の定義（`.claude/agents/*.md`。仕様は `todo-workflow` skill）で` に
  置き換えており、`CLAUDE.md` 側に残っている

`git add` 後の `git status` で、`skills/` から拾われたのが `SKILL.md`
1 本だけであることも確かめた。

## 残ること

**Claude Code は skill を起動時にしか読まない。** 認識されるかどうかは、
利用者が再起動してから分かる。

## 直した先

`~/.claude`（`dotfiles-claude`）の `a45ed0a`。
このリポジトリのファイルは変えていない（`TODO.md` と `archives/` を除く）。

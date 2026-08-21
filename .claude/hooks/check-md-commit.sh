#!/bin/bash
#
# PreToolUse(Bash) hook。`git commit` に `.md` が入っていれば、文書の確認の
# 担当（wording）を立てたかを促す。**止めない**（TODO-026）。
#
# 判断はしない。`.md` が入っているかどうかだけを見る。
# どんな場合も exit 0 で終わる（hook のせいでコミットを止めないため）。
#
# set -e は使わない。git や jq が失敗しても最後まで進んで exit 0 したい。

# 一覧に並べるファイル名の上限
MAX_LIST=20

# jq が無ければ何もしない（JSON を手で組み立てない）
command -v jq >/dev/null 2>&1 || exit 0

input=$(cat)
[ -n "$input" ] || exit 0

cmd=$(printf '%s' "$input" | jq -r '.tool_input.command // ""' 2>/dev/null)
[ -n "$cmd" ] || exit 0

# `git commit` か。同じコマンド区切りの中で git のあとに commit が来る形だけ
# を見る（`git log | grep commit` のような別コマンドを拾わないため）。
printf '%s' "$cmd" |
	grep -Eq '(^|[;&|(]|&&)[[:space:]]*git[^;&|]*[[:space:]]commit([[:space:]]|$)' ||
	exit 0

root="${CLAUDE_PROJECT_DIR:-$PWD}"
git -C "$root" rev-parse --is-inside-work-tree >/dev/null 2>&1 || exit 0

# ステージされた .md
# -z を付けるのは、日本語のファイル名が \346\226... に化けないため
# （archives/todo/ のファイル名は日本語）。NUL 区切りを改行に直して使う。
staged=$(git -C "$root" diff --cached --name-only -z -- '*.md' 2>/dev/null |
	tr '\0' '\n')

# 作業ツリー側も見るかどうか
#
#   (a) `-a` / `--all` が付いている  … ステージしていない変更も入る
#   (b) ステージが空（.md に限らず 1 つも無い）
#
# (b) を入れているのは `git commit -m "..." TODO.md` の形（pathspec）を
# 拾うため。pathspec はステージの有無に関わらずコミットされるので、
# --cached にも -a にも当たらない。pathspec を正規表現で切り出すのは
# -m の引数と見分けが付かず壊れやすいので、代わりに「ステージが空」を
# 手がかりにする。ステージが空で素の `git commit` を打つと git 自身が
# エラーで終わるため、ステージが空の `git commit` は -a か pathspec の
# ときしかない（余計に促す場面はほとんど増えない）。
look_worktree=""
if printf '%s' "$cmd" |
	grep -Eq '(^|[[:space:]])(--all|-[[:alnum:]]*a[[:alnum:]]*)([[:space:]]|$)'; then
	look_worktree="yes"
# ここは中身が空かどうかを見るだけなので -z を付けない。
# 付けると NUL がコマンド置換に入り、bash が警告を stderr へ出す。
elif [ -z "$(git -C "$root" diff --cached --name-only 2>/dev/null)" ]; then
	look_worktree="yes"
fi

unstaged=""
if [ -n "$look_worktree" ]; then
	unstaged=$(git -C "$root" diff --name-only -z HEAD -- '*.md' 2>/dev/null |
		tr '\0' '\n')
fi

files=$(printf '%s\n%s\n' "$staged" "$unstaged" | sed '/^[[:space:]]*$/d' | sort -u)
[ -n "$files" ] || exit 0

count=$(printf '%s\n' "$files" | wc -l | tr -d ' ')

# 一覧が長くなりすぎないように MAX_LIST 件で打ち切る
listed=$(printf '%s\n' "$files" | head -n "$MAX_LIST" | sed 's/^/  - /')
if [ "$count" -gt "$MAX_LIST" ]; then
	listed="${listed}
  - （ほか $((count - MAX_LIST)) 件）"
fi

sys_msg="このコミットには .md が ${count} 個入っている:
${listed}

文書の確認の担当（wording）を立てたか。まだなら、コミットの前に立てること
（コミットに入る .md から、このリポジトリに前例の無い語を挙げる担当）。"

ctx_msg="このコミットには次の .md が入っている:
${listed}

文書の確認の担当（wording）を立てたかを確かめること。立てていなければ、
コミットする前に wording を立てて、前例の無い語を挙げさせる（TODO-025・
TODO-026 で決めた手順）。既に立ててあるなら、このまま進めてよい。"

jq -n --arg sys "$sys_msg" --arg ctx "$ctx_msg" \
	'{systemMessage: $sys, additionalContext: $ctx}' 2>/dev/null

exit 0

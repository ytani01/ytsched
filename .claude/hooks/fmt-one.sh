#!/usr/bin/env bash
#
# PostToolUse(Edit|Write) の hook。いま編集した 1 ファイルだけを整形する
# （TODO-193）。
#
# mise run fmt は src / tests / tools 全体を舐めるので、編集のたびには重い。
# 触った 1 ファイルだけなら即座に終わり、mise run lint まで指摘を溜めずに
# 済む。
#
#   .py … uv run ruff format → uv run ruff check --fix
#   .js … npx prettier --write → npx eslint --fix
#
# 直したあとに残った指摘は stderr へ書き、exit 2 で返す（PostToolUse では
# exit 2 の stderr だけが Claude に渡る）。整形しかしていないときは何も
# 言わない。
#
# 対象を絞る理由:
#   - archives/ は決着した項目の記録。ruff の対象から外してある
#     （TODO-168）が、ファイルを名指しで渡すと ruff は exclude を見ない
#     （--force-exclude が要る）ので、こちら側でも外す
#   - .venv / node_modules / dist は生成物なので触らない
#   - プロジェクトの外のファイルは、このプロジェクトの設定で整形しない

set -uo pipefail

input=$(cat)
file=$(printf '%s' "$input" | jq -r '.tool_input.file_path // ""' 2>/dev/null) || exit 0
[ -n "$file" ] || exit 0
[ -f "$file" ] || exit 0

root=${CLAUDE_PROJECT_DIR:-$PWD}

# プロジェクトの外は触らない
case "$file" in
    "$root"/*) rel=${file#"$root"/} ;;
    *)         exit 0 ;;
esac

# 生成物と archives/ は外す
case "$rel" in
    archives/*|.venv/*|node_modules/*|dist/*|.git/*) exit 0 ;;
esac

out=""
status=0

case "$file" in
    *.py)
        uv run ruff format "$file" >/dev/null 2>&1
        out=$(uv run ruff check --fix "$file" 2>&1) || status=1
        ;;
    *.js)
        npx --no-install prettier --write "$file" >/dev/null 2>&1
        out=$(npx --no-install eslint --fix "$file" 2>&1) || status=1
        ;;
    *)
        exit 0
        ;;
esac

if [ $status -ne 0 ] && [ -n "$out" ]; then
    printf '%s を整形したあとに残った指摘:\n' "$rel" >&2
    printf '%s\n' "$out" >&2
    exit 2
fi

exit 0

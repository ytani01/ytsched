#!/bin/bash
# Adapt the Claude Code Markdown commit reminder to Codex's hook output shape.

root=$(git rev-parse --show-toplevel 2>/dev/null) || exit 0
output=$(bash "$root/.claude/hooks/check-md-commit.sh")
[ -n "$output" ] || exit 0

printf '%s' "$output" | jq '{
  systemMessage,
  hookSpecificOutput: {
    hookEventName: "PreToolUse",
    additionalContext: .additionalContext
  }
}' 2>/dev/null

exit 0

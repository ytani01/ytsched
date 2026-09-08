"""Codex の patch に含まれる各ファイルを Claude の整形フックへ渡す。"""

import json
import os
import subprocess
import sys
from pathlib import Path


def patch_paths(patch: str) -> list[str]:
    paths: list[str] = []
    for line in patch.split("\n"):
        if line.startswith(("*** Add File: ", "*** Update File: ")):
            paths.append(line.split(": ", 1)[1])
        elif line.startswith("*** Move to: ") and paths:
            paths[-1] = line.removeprefix("*** Move to: ")
    return paths


def main() -> int:
    event = json.load(sys.stdin)
    root = Path(__file__).resolve().parents[2]
    cwd = Path(event.get("cwd", str(root)))
    patch = event.get("tool_input", {}).get("command", "")
    status = 0
    for name in dict.fromkeys(patch_paths(patch)):
        path = (cwd / name).resolve()
        if not path.is_relative_to(root) or not path.is_file():
            continue
        # Claude のファイルと生成物は、シンボリックリンク経由でも触らない。
        if path.relative_to(root).parts[0] in {
            ".claude",
            "archives",
            ".venv",
            "node_modules",
            "dist",
            ".git",
        }:
            continue
        if path.suffix not in {".py", ".js"}:
            continue
        result = subprocess.run(
            ["bash", str(root / ".claude/hooks/fmt-one.sh")],
            input=json.dumps({"tool_input": {"file_path": str(path)}}),
            text=True,
            cwd=root,
            env={**os.environ, "CLAUDE_PROJECT_DIR": str(root)},
            check=False,
        )
        if result.returncode:
            status = 2
    return status


if __name__ == "__main__":
    sys.exit(main())

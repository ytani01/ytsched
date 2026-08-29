# Repository Guidelines

## Claude Code Configuration Parity

Before doing repository work, read both `~/.claude/CLAUDE.md` and this
repository's `CLAUDE.md` completely and follow them as project instructions.
They are the authoritative source for workflow, TODO management, Japanese
writing, shell safety, image handling, data protection, delegation, review,
verification, wording checks, token accounting, and two-stage commits. When
those files mention Claude-specific UI commands or paths, use the equivalent
Codex feature where one exists. Repository-specific instructions override
global instructions; direct user instructions override both.

Reusable role definitions are in `.agents/agents/`. Each role must also read
the matching `.claude/agents/<role>.md` before acting; the Claude definition is
the complete role specification. Codex workflows live in `.agents/skills/`.
For implementation tasks, use `ytsched-workflow`; use `wording-check` only
when the user explicitly requests it. Do not delegate unless the user, an
applicable skill, or repository instructions explicitly require it.

Codex loads repository hooks from `.codex/hooks.json`. After cloning or after a
hook change, review and trust the hook with `/hooks`.

## Project Structure & Module Organization

Application code lives in `src/ytsched/`. The Click CLI starts in
`__main__.py`; Tornado application assembly is in `webapp.py`; handlers are in
`handler.py`, `main_handler.py`, and `edit_handler.py`; persistence and domain
logic are separated into `ytsched.py`, `sched_load.py`, and `sched_update.py`.
Templates and browser assets live under `src/ytsched/webroot/`. Tests mirror
these modules in `tests/test_*.py`, with migration fixtures in
`tests/data/old_format/`. Developer notes belong in `docs/`; maintenance scripts
belong in `tools/`. See `src/README.md` and `tests/README.md` for detailed maps.

## Build, Test, and Development Commands

Run `uv sync`, then `mise install` and `npm install` to prepare Python and
JavaScript tooling.

- `mise run webapp -- --datadir /tmp/ytsched-data --port 10099` starts a safe
  local server without touching personal data.
- `mise run lint` formats and checks Python and JavaScript with Ruff, Prettier,
  basedpyright, mypy, and ESLint.
- `mise run test` runs linting followed by the complete pytest suite.
- `uv run pytest tests/test_handler.py -v` runs one focused test module.
- `mise run build` performs all checks and builds distributions with `uv`.

## Coding Style & Naming Conventions

Python uses four-space indentation, Ruff formatting, a 78-character line
length, type annotations, and `snake_case` names; classes use `PascalCase`.
Keep domain logic independent of Tornado where practical. Use the `mylog.py`
wrapper instead of standard `logging`. JavaScript is formatted by Prettier and
linted by ESLint; existing asset names use kebab-case (for example,
`main-page.js`).

## Testing Guidelines

Use pytest and name files `test_<module>.py` and functions `test_<behavior>`.
Put temporary application data under pytest's `tmp_path` or pass an explicit
`--datadir`; never test against `~/ytsched/data`. Browser behavior belongs in
`tests/test_browser.py` and must verify rendered content, not only URL changes.
Update golden-master expectations when a behavior change is intentional.

## Commit & Pull Request Guidelines

Follow the history's Conventional Commit-style subjects, such as
`feat(ui): ... (TODO-109)`, `fix(test): ...`, and `docs(todo): ...`. Keep each
commit focused and include the relevant TODO number when applicable. Pull
requests should explain the user-visible effect, list verification commands,
link the issue/TODO, and include before/after screenshots for UI changes. Note
data-format or migration implications explicitly.

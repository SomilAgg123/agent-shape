# Using agent-shape with different coding agents

Purpose: Point each coding agent at the single rule file.
Read when: Setting up a new agent runner.
Parent: [Context map](../README.md).
Retention: Current setup instructions.

| Runner | Setup |
| --- | --- |
| Codex | Reads `AGENTS.md` natively. |
| Cursor | Reads `AGENTS.md`; avoid duplicating rules in `.cursor/rules`. |
| Claude Code | Create a one-line `CLAUDE.md` containing `@AGENTS.md`, or configure it to read `AGENTS.md`. |
| Others | Configure the system prompt or project rules to load `AGENTS.md`. |

Review runs inside the agent chat using `.github/review-prompt.md` and `scripts/harness/pr_maintenance.py`.

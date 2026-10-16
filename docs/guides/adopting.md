# Adopting agent-shape in an existing repository

Purpose: Add the harness to a repo that already has code.
Read when: Installing agent-shape outside the GitHub template flow.
Parent: [Context map](../README.md).
Retention: Current instructions.

1. Copy `AGENTS.md`, `docs/`, `.github/` (template, review prompt/schema, `agent-shape.json`, workflows), `scripts/harness/`, `tests/harness/` and `requirements-ci.txt`.
2. Run `python scripts/harness/init.py --name <name> --description "<one line>" --test-command "<your tests>"`.
3. Move existing rule files (`CLAUDE.md`, `.cursorrules`) into `AGENTS.md` or steering docs; keep one owner per rule.
4. Seed `docs/plan.md` with your current queue under the configured heading.
5. In branch protection, require the `PR maintenance gate` check.

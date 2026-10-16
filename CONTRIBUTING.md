# Contributing

This repo uses its own harness. Read [AGENTS.md](AGENTS.md) and
[PR writing](docs/pr-writing.md) before opening a PR.

- Fill in every section of the PR template, including Knowledge updates
  ("No knowledge changes." when none) and the Maintenance fields.
- Use TDD for checker behavior: add a failing test in `tests/harness/` first and
  report Red / Green / Refactor evidence.
- Run `python -m pytest -q` before pushing.
- Keep the template generic: no product-specific names, data or credentials.

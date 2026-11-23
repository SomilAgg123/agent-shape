# Harness source

Purpose: Identify the extraction source and deliberate adaptations.
Read when: Refreshing the harness or explaining a difference from Customer Memory.
Authority: The source revision and the user's extraction choices.
Parent: [Context map](README.md).
Retention: Current provenance and adaptation boundaries.

This harness comes from `SomilAgg123/customermemory`, previously named `contextm`.
The source revision is `81a1f963bb896b63f68de6a9f6897a0f93c50ecb` on `main`, inspected on 23 November 2026.
The source repository requires access. Its application and customer data are outside this template.

## Source files

- `AGENTS.md` supplies scope, language, TDD, comment and context rules.
- `docs/README.md` supplies context ownership, retention and history review triggers.
- `docs/pr-writing.md` and `.github/pull_request_template.md` supply the PR format and review workflow.
- `.github/codex-review.md` and its schema supply context and language review requirements.
- `scripts/pr_maintenance.py` and `tests/test_pr_maintenance.py` supply the checker and its regression coverage.
- The PR and context workflows supply deterministic CI and revision evidence.
- Frontend and backend steering supply reusable interaction and API documentation rules.
- The Bend installer and version pin supply reproducible optional toolchain setup.

## Adaptations

Bend is optional by explicit user choice. Enabling it requires project laws,
proofs, generated-output checks and regression checks.
Application paths, review routes and the base branch are configurable.
The validation workflow runs harness checks until adopters add application checks.
Product scope, history, customer contracts, model settings and interface implementation remain project-owned.

The current Customer Memory harness defines the baseline.
The previous agent-shape checker, initializer, ticket fields and examples were replaced.
The template retains its existing MIT license.

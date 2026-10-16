# agent-shape

A repository template that gives coding agents a shape to work in: one rule
file, disciplined context docs, a strict PR contract, a CI gate, and an
agent-run review with a merge guard.

## What you get

- **`AGENTS.md`** — the single entry point: scope discipline, TDD, plain-language
  naming, stop-at-each-milestone, and a task → doc routing table.
- **Context system** (`docs/README.md`) — every context file has a Purpose /
  Read when / Authority / Parent / Retention header, one owner per fact, and
  "replace, don't append" retention. History stays out of default context.
- **PR contract** (`.github/pull_request_template.md`, `docs/pr-writing.md`) —
  Knowledge updates linking every changed context file, Red/Green/Refactor
  evidence, and a ticket from the queue in `docs/plan.md`.
- **PR checker** (`scripts/harness/pr_maintenance.py`) — enforces the contract
  in CI, prepares the agent review request, validates the review report
  against a JSON schema, and runs a merge guard that refuses stale reviews or CI evidence.
- **CI** — `pr.yml` runs validation + context check, then a gate job. Actions
  never call a model; the review happens in your agent's chat.
- **Add-ons** — formal proofs with Bend (`modules/proofs-bend`, off by default).
- **Example** — `examples/` shows a PR body that passes and one that is blocked.

## How the loop works

```
plan.md queue ──► agent builds (TDD) ──► PR with contract ──► CI: validate + context ──► gate
                                                                     │
                     merge ◄── merge-guard ◄── review report ◄── agent review in chat
```

## Get started

See [QUICKSTART.md](QUICKSTART.md). Adding to an existing repo:
[adopting guide](docs/guides/adopting.md). Configuration:
[customizing guide](docs/guides/customizing.md). Agent setup:
[runners guide](docs/guides/runners.md).

## Requirements

Python 3.10+ and git. The checker needs `jsonschema` and `markdown-it-py`
(`requirements-ci.txt`).

## License

[MIT](LICENSE).

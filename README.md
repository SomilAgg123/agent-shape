# agent-shape

A reusable coding-agent harness extracted from the current Customer Memory workflow.
It gives agents scoped instructions, maintained context, readable PRs and a review gate.

## What it does

- Loads `AGENTS.md` as the entry point, then reads context for the task.
- Keeps approved scope separate from proposals and stops at PR review checkpoints.
- Uses meaningful tests for new behavior and retains only useful context.
- Applies Simplified Technical English rules to changed prose and user communication.
- Reports validation, paid model spend and linked knowledge changes in each PR.
- Requires explicit context and language review before the local merge guard passes.
- Checks that the review and CI evidence match the current PR revision.

Actions runs deterministic checks. The agent reviews code and context in the current chat.
Bend proofs are optional and disabled by default.

## Start here

Use the [quickstart](QUICKSTART.md) to adopt this harness.
Read [configuration](docs/configuration.md) for project paths and [local validation](docs/local-validation.md) for checks.
The [source record](docs/source.md) identifies the upstream revision and extraction choices.

Python 3.10+ and Git are required. The CI workflow uses Python 3.12.

## License

[MIT](LICENSE).

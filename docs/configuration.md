# Project configuration

Purpose: Adapt review routing and validation to the project's structure.
Read when: Adopting the harness or changing repository paths.
Authority: `.github/agent-shape.schema.json` and the checker implementation.
Parent: [Context map](README.md).
Retention: Current configuration contract.

Edit `.github/agent-shape.json`. Unknown settings and invalid value types fail validation.

| Setting | Meaning |
| --- | --- |
| `base_branch` | The branch accepted by the merge guard. Update workflow branch filters when changing it. |
| `context_files` | Additional Markdown files that require linked Knowledge updates. |
| `context_prefixes` | Additional directories containing context files. Include the trailing slash. |
| `always_review` | Additional context files required for every review. |
| `review_routes` | Prefixes that select domain documents when matching files change. This list replaces the default routes. |
| `bend` | Optional proof validation. See [Bend setup](bend.md). |

Core context files and Markdown under `docs/` remain included.
Additional context settings extend that coverage.
The core review reads `AGENTS.md`, `docs/README.md` and `docs/pr-writing.md` when present.
It also reads changed context and any configured owners.
Missing configured owners block review preparation.

Keep the workflow name `PR maintenance` and its validation, context and gate job names.
The merge guard verifies these names and `.github/workflows/pr.yml`.
The [review schema](../.github/codex-review.schema.json) defines the report format.

Configure application tests and builds directly in `.github/workflows/validate.yml`.
Document their local equivalents in [local validation](local-validation.md).
The harness has no ticket queue parser or required ticket fields.
Approved scope belongs in [the plan](plan.md).

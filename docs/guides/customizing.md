# Customizing agent-shape

Purpose: Explain the configuration keys and optional add-ons.
Read when: Changing what the PR checker treats as context, tickets or required review docs.
Parent: [Context map](../README.md).
Retention: Current configuration contract.

All settings live in `.github/agent-shape.json`:

| Key | Meaning |
| --- | --- |
| `base_branch` | Branch the merge guard targets. |
| `board_path`, `board_heading` | File and heading holding the ticket queue. `PR-n` tickets match `### PR n` headings; other IDs match text. |
| `workflow_name`, `workflow_file`, `required_jobs` | CI run and jobs the merge guard requires. |
| `review_prompt`, `review_schema` | Agent review instructions and report schema. |
| `context_files`, `context_prefixes` | Markdown files that count as context and must be listed under Knowledge updates. |
| `docs_only_assets` | Non-Markdown paths that still count as documentation-only. |
| `always_review`, `review_routes` | Docs every review must read, plus docs added when changed paths match prefixes. |

Validation commands live in `.github/workflows/validate.yml` (marked `PROJECT CHECKS`).

Add-ons: `modules/proofs-bend` (formal proofs, off by default) via `init.py --enable-bend`.

# Local validation

Purpose: Run the harness checks and locate application validation.
Read when: Setting up development or checking a proposed change.
Authority: The test suite and [validation workflow](../.github/workflows/validate.yml).
Parent: [Context map](README.md).
Retention: Current commands and material validation limits.

## Harness checks

Use Python 3.10+ and Git. Install the development dependencies in a virtual environment.

```sh
python -m pip install -r requirements-dev.txt
python -m pytest tests -q
python scripts/check_bend.py
```

The tests cover PR evidence, context links, sentence limits, review coverage and merge guards.
They also cover configurable review paths and optional Bend execution.
The Bend wrapper tests use a simulated executable. They do not prove project laws or validate the downloaded toolchain.

Follow [PR writing](pr-writing.md#review-and-merge-through-codex) to prepare a review from a clean, captured PR revision.
Keep snapshots and review reports outside the repository.
The read-only review uses available evidence; run validation before that review stage.

## Application checks

The template contains no application. Add its setup, startup commands, tests and build checks here after adoption.
Link any interface contract and browser validation guide here.
Add matching commands to the validation workflow.
Keep credentials outside tracked files and isolate validation data from production data.
Distinguish simulated responses from real model evidence.
Record paid execution limits and results when paid model calls are authorized.

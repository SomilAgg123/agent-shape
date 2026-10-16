# Formal proofs add-on (Bend)

Purpose: Machine-check a small number of core invariants before every code PR.
Read when: You enable this add-on or change laws, proofs, or the pinned Bend version.
Status: Off by default. `scripts/harness/init.py --enable-bend` copies it to the repo root.

## What it adds
- `.bend-version`: pinned Bend version (CI step runs only when this file exists at the root).
- `scripts/install_bend.py --destination <new-dir>`: pinned installer (needs git + npm); exports `BEND_EXECUTABLE` in Actions.
- `scripts/check_bend.py`: verifies the version and runs `bend PROOF.bend`.
- `LAWS.bend.example` / `PROOF.bend.example`: rename to `LAWS.bend` / `PROOF.bend` and write real laws.

## Agent rule to add to AGENTS.md when enabled
Before opening or updating a code PR, run `bend guide`, `bend PROOF.bend`, and
`python scripts/check_bend.py`. Skipped proof checks are not completed validation.

The example files are syntax sketches and are not checked by this template's CI.

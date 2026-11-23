# Optional Bend validation

Purpose: Enable reproducible proof and integration checks for projects that use Bend.
Read when: Enabling Bend or changing laws, proofs or generated output.
Authority: The pinned installer, project proofs and explicit user scope.
Parent: [Context map](README.md).
Retention: Current setup, required checks and proof limits.

Bend is disabled in `.github/agent-shape.json` by default.
Disabled projects do not install Bend or require proof files.
The wrapper reports that state explicitly.

## Enable Bend

1. Add the project's `LAWS.bend` and `PROOF.bend` files.
2. Keep `.bend-version` matched to the source revision pinned in `scripts/install_bend.py`.
3. Set `bend.generated_check` to the command that verifies generated output.
4. Set `bend.regression_check` to the command that checks the integration boundary.
5. Set `bend.enabled` to `true`.
6. Run the installer and validation command below.

Commands are argument arrays, without a shell.
Use `python` as the first argument to run the current Python interpreter.
For example, a project can use `["python", "scripts/build_bend.py", "--check"]` when that script exists.
Both configured checks are required when Bend is enabled.

```sh
python scripts/install_bend.py --destination /tmp/project-bend
export AGENT_SHAPE_BEND=/tmp/project-bend/source/bin/bend
python scripts/check_bend.py
```

The destination must be new. Installation requires network access, Git, Node and npm.
The installer pins Bend source and Bun, and verifies their versions.
CI installs into its temporary directory only when Bend is enabled.

## Required validation

Every enabled code PR checks the pinned version, runs `bend guide` and proves `PROOF.bend`.
It then runs the generated-output and regression commands from the repository root.
Missing files, empty commands, incorrect versions and failed checks block validation.
Skipped checks are incomplete validation, even when Bend files are unchanged.

Keep claims within the proven boundary.
A pure function proof does not establish storage isolation, provider correctness or model quality.
Test those boundaries separately.
Preserve existing laws, proofs, generated output and supporting documentation unless the user explicitly authorizes changes.

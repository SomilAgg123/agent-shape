# Adopt agent-shape

Use this repository as a template, or copy its harness files into your project.
Keep the project's license and application files when adopting the harness.

1. Replace `{{PROJECT_NAME}}` and `{{PROJECT_DESCRIPTION}}` in `AGENTS.md`.
2. Fill in the current checkpoint and approved scope in `docs/plan.md`.
3. Record project direction in `docs/vision.md`, keeping proposals separate from approval.
4. Review the frontend, backend, language and comment rules with the project owner.
5. Configure project paths in `.github/agent-shape.json`.
6. Add application setup and validation commands to `docs/local-validation.md`.
7. Add those checks to `.github/workflows/validate.yml`, preserving the harness tests.
8. Configure your agent runner to load `AGENTS.md`.
9. Install dependencies and run the checks below.

```sh
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m pytest tests -q
python scripts/check_bend.py
```

The harness files are `AGENTS.md`, `.github/`, `docs/`, `scripts/`, the harness tests and Python configuration files.
When adopting into an existing project, reconcile destination paths before copying files.
Keep one active owner for each rule and repair its incoming links.
The [context policy](docs/README.md) defines document ownership and retention.

The test suite checks the harness. Add your application's checks before relying on CI for application validation.
Bend stays disabled until the project supplies its own laws, proofs and integration checks.
See [Bend setup](docs/bend.md).

Open the first PR with the repository template.
Follow [PR writing](docs/pr-writing.md) for validation evidence, review and merging.

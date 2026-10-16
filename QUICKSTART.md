# Quickstart

1. Create a repo from this template (or copy it) and clone it.
2. Initialize it:

   ```bash
   python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt
   .venv/bin/python scripts/harness/init.py --name my-app \
     --description "my-app does one useful thing." \
     --test-command "python -m pytest -q"   # add --enable-bend for proofs, --keep-example to keep the demo
   .venv/bin/python -m pytest tests/harness -q
   ```

3. Edit `docs/plan.md`: describe the current checkpoint and queue your first tickets under `## Queue`.
4. Replace the `PROJECT CHECKS` step in `.github/workflows/validate.yml` with your real lint/test/build commands.
5. In branch protection, require the `PR maintenance gate` check.
6. Ask your agent for the first ticket. It opens a PR using the template; CI checks the contract.
7. Before merging, have the agent follow [the review and merge guard](docs/pr-writing.md#review-and-merge-guard).

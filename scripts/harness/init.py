"""Fill agent-shape placeholders and toggle add-ons for a new project."""

import argparse
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent.parent.parent
PLACEHOLDER_FILES = ["AGENTS.md", ".github/agent-shape.json"]
DEFAULT_TEST = "python -m pytest -q"
BEND_FILES = {".bend-version": ".bend-version", "scripts/install_bend.py": "scripts/install_bend.py", "scripts/check_bend.py": "scripts/check_bend.py", "LAWS.bend.example": "LAWS.bend.example", "PROOF.bend.example": "PROOF.bend.example"}
BEND_RULE = """- Before opening or updating a code PR, run `bend guide`, `bend PROOF.bend` and
  `python scripts/check_bend.py` with the pinned `.bend-version`. Skipped proof
  checks are not completed validation; report setup failures as blockers.
"""


def initialize(root, name, description, test_command=DEFAULT_TEST, base_branch="main", enable_bend=False, keep_example=False):
    root = Path(root)
    for relative in PLACEHOLDER_FILES:
        path = root / relative
        path.write_text(path.read_text().replace("{{PROJECT_NAME}}", name).replace("{{PROJECT_DESCRIPTION}}", description))
    config_path = root / ".github/agent-shape.json"
    config = json.loads(config_path.read_text())
    config["base_branch"] = base_branch
    config_path.write_text(json.dumps(config, indent=2) + "\n")
    for workflow in ["pr.yml"]:
        path = root / ".github/workflows" / workflow
        path.write_text(path.read_text().replace("branches: [main]", f"branches: [{base_branch}]"))
    validate = root / ".github/workflows/validate.yml"
    validate.write_text(validate.read_text().replace(f"run: {DEFAULT_TEST}\n", f"run: {test_command}\n"))
    if enable_bend:
        module = root / "modules/proofs-bend"
        for source, target in BEND_FILES.items():
            destination = root / target
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(module / source, destination)
        agents = root / "AGENTS.md"
        text = agents.read_text()
        anchor = "- Stop at each PR milestone"
        agents.write_text(text.replace(anchor, BEND_RULE + anchor, 1))
    if not keep_example:
        shutil.rmtree(root / "examples", ignore_errors=True)
        test = root / "tests/harness/test_examples.py"
        if test.exists():
            test.unlink()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name", required=True)
    parser.add_argument("--description", required=True)
    parser.add_argument("--test-command", default=DEFAULT_TEST)
    parser.add_argument("--base-branch", default="main")
    parser.add_argument("--enable-bend", action="store_true")
    parser.add_argument("--keep-example", action="store_true")
    args = parser.parse_args()
    initialize(ROOT, args.name, args.description, args.test_command, args.base_branch, args.enable_bend, args.keep_example)
    print(f"Initialized agent-shape for {args.name}.")


if __name__ == "__main__":
    main()

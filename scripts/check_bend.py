import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

from jsonschema import Draft202012Validator

from install_bend import install


ROOT = Path(__file__).resolve().parent.parent


def check(root, executable=None, install_directory=None):
    settings = json.loads((root / ".github/agent-shape.json").read_text())
    schema = json.loads((ROOT / ".github/agent-shape.schema.json").read_text())
    errors = list(Draft202012Validator(schema).iter_errors(settings))
    if errors:
        raise ValueError("Invalid project configuration: " + errors[0].message)
    bend = settings.get("bend", {"enabled": False})
    if not bend["enabled"]:
        print("Bend is disabled for this project.")
        return
    for name in [".bend-version", "LAWS.bend", "PROOF.bend"]:
        if not (root / name).is_file():
            raise ValueError(f"Enabled Bend requires {name}.")
    for name in ["generated_check", "regression_check"]:
        if not bend[name] or not bend[name][0].strip():
            raise ValueError(f"Enabled Bend requires a {name} command.")
    expected = (root / ".bend-version").read_text().strip()
    if install_directory:
        if root != ROOT:
            raise ValueError("Install the pinned toolchain from the project root.")
        executable = str(install(install_directory.resolve()))
    executable = executable or os.environ.get("AGENT_SHAPE_BEND", "bend")
    actual = subprocess.check_output([executable, "version"], text=True).strip()
    if actual != f"bend {expected}":
        raise ValueError(f"Bend version must be {expected}; received {actual}.")
    for command in [[executable, "guide"], [executable, "PROOF.bend"], bend["generated_check"], bend["regression_check"]]:
        command = [sys.executable if part == "python" and index == 0 else part for index, part in enumerate(command)]
        subprocess.run(command, cwd=root, check=True)
    print(f"Bend {expected} validation passed.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--executable")
    parser.add_argument("--install-directory", type=Path)
    args = parser.parse_args()
    try:
        check(args.root.resolve(), args.executable, args.install_directory)
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"Bend validation blocked: {error}\n")


if __name__ == "__main__":
    main()

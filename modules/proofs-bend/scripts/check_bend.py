"""Check the pinned Bend version and the project's PROOF.bend."""

import os
from pathlib import Path
import subprocess

ROOT = Path.cwd()


def main():
    executable = os.environ.get("BEND_EXECUTABLE", "bend")
    expected = (ROOT / ".bend-version").read_text().strip()
    try:
        version = subprocess.run([executable, "version"], check=True, capture_output=True, text=True).stdout.strip()
        if version != f"bend {expected}":
            raise SystemExit(f"Use Bend {expected}; found {version}.")
        subprocess.run([executable, "PROOF.bend"], cwd=ROOT, check=True)
        print("Bend proofs checked.")
    except FileNotFoundError:
        raise SystemExit(f"Install Bend {expected}, or set BEND_EXECUTABLE to its executable path.")
    except subprocess.CalledProcessError:
        raise SystemExit("Bend proof check failed.")


if __name__ == "__main__":
    main()

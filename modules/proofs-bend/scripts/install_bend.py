import argparse
import os
from pathlib import Path
import shlex
import subprocess


SOURCE_SHA = "ef6278149f398132c006b4eaed73ee751fb8d897"
BEND_VERSION = "2.0.35"
BUN_VERSION = "1.4.2"
ROOT = Path.cwd()


def install(destination):
    expected = (ROOT / ".bend-version").read_text().strip()
    if expected != BEND_VERSION:
        raise ValueError(f"Pin the matching Bend source before installing version {expected}.")
    destination.mkdir(parents=True, exist_ok=False)
    source = destination / "source"
    subprocess.run(["git", "init", "-q", str(source)], check=True)
    subprocess.run(["git", "-C", str(source), "fetch", "--depth", "1", "https://github.com/bendlang/bend.git", SOURCE_SHA], check=True)
    subprocess.run(["git", "-C", str(source), "checkout", "--detach", "FETCH_HEAD"], check=True)
    subprocess.run(["npm", "install", "--prefix", str(destination / "bun"), f"bun@{BUN_VERSION}", "--no-audit", "--no-fund"], check=True)
    bun = destination / "bun/node_modules/.bin/bun"
    if subprocess.check_output([str(bun), "--version"], text=True).strip() != BUN_VERSION:
        raise ValueError("The installed Bun version does not match the pin.")
    executable = source / "bin/bend"
    executable.parent.mkdir()
    config = destination / "bunfig.toml"
    config.write_text("")
    executable.write_text("#!/bin/sh\nexec " + shlex.quote(str(bun)) + " --no-env-file --config=" + shlex.quote(str(config)) + " " + shlex.quote(str(source / "bend2/main.ts")) + ' "$@"\n')
    executable.chmod(0o755)
    if subprocess.check_output([str(executable), "version"], text=True).strip() != f"bend {expected}":
        raise ValueError("The installed Bend version does not match .bend-version.")
    return executable


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--destination", type=Path, required=True)
    args = parser.parse_args()
    try:
        executable = install(args.destination.resolve())
        if os.environ.get("GITHUB_ENV"):
            with open(os.environ["GITHUB_ENV"], "a") as output:
                output.write(f"BEND_EXECUTABLE={executable}\n")
        print(f"Installed Bend {BEND_VERSION}: {executable}")
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"Bend setup failed: {error}\n")


if __name__ == "__main__":
    main()

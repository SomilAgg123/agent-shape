import json
from pathlib import Path
import subprocess
import sys

import pytest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/check_bend.py"


def run_bend(root, *args):
    return subprocess.run([sys.executable, str(SCRIPT), "--root", str(root), *args], text=True, capture_output=True)


def configure(root, enabled=True):
    (root / ".github").mkdir()
    (root / ".github/agent-shape.json").write_text(json.dumps({"bend": {
        "enabled": enabled,
        "generated_check": [sys.executable, "-c", "print('generated output checked')"],
        "regression_check": [sys.executable, "-c", "print('regressions checked')"],
    }}))


def fake_bend(root, version="2.0.35", proof_status=0):
    binary = root / "bend"
    binary.write_text(f"#!{sys.executable}\nimport sys\nprint('bend {version}' if sys.argv[1] == 'version' else sys.argv[1])\nsys.exit({proof_status} if sys.argv[1] == 'PROOF.bend' else 0)\n")
    binary.chmod(0o755)
    (root / ".bend-version").write_text("2.0.35\n")
    (root / "LAWS.bend").write_text("law fixture\n")
    (root / "PROOF.bend").write_text("proof fixture\n")
    return str(binary)


def test_disabled_bend_needs_no_toolchain_or_project_proofs(tmp_path):
    configure(tmp_path, enabled=False)
    install = tmp_path / "toolchain"
    result = run_bend(tmp_path, "--install-directory", str(install))
    assert result.returncode == 0, result.stderr
    assert "disabled" in result.stdout
    assert not install.exists()


@pytest.mark.parametrize("missing", ["LAWS.bend", "PROOF.bend", "generated_check", "regression_check"])
def test_enabled_bend_requires_complete_project_checks(tmp_path, missing):
    configure(tmp_path)
    binary = fake_bend(tmp_path)
    if missing.endswith(".bend"):
        (tmp_path / missing).unlink()
    else:
        path = tmp_path / ".github/agent-shape.json"
        settings = json.loads(path.read_text())
        settings["bend"][missing] = []
        path.write_text(json.dumps(settings))
    result = run_bend(tmp_path, "--executable", binary)
    assert result.returncode == 1
    assert missing in result.stderr


def test_enabled_bend_runs_proofs_generation_and_regressions(tmp_path):
    configure(tmp_path)
    result = run_bend(tmp_path, "--executable", fake_bend(tmp_path))
    assert result.returncode == 0, result.stderr
    assert "guide" in result.stdout
    assert "PROOF.bend" in result.stdout
    assert "generated output checked" in result.stdout
    assert "regressions checked" in result.stdout


def test_bend_rejects_a_different_toolchain_version(tmp_path):
    configure(tmp_path)
    result = run_bend(tmp_path, "--executable", fake_bend(tmp_path, version="0.0.0"))
    assert result.returncode == 1
    assert "version" in result.stderr
    assert "generated output checked" not in result.stdout


def test_failed_proofs_block_later_bend_checks(tmp_path):
    configure(tmp_path)
    result = run_bend(tmp_path, "--executable", fake_bend(tmp_path, proof_status=1))
    assert result.returncode == 1
    assert "generated output checked" not in result.stdout


def test_mistyped_bend_flag_cannot_silently_disable_validation(tmp_path):
    configure(tmp_path, enabled="false")
    result = run_bend(tmp_path)
    assert result.returncode == 1
    assert "configuration" in result.stderr

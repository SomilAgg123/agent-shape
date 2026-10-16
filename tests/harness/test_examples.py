from pathlib import Path
import shutil
import subprocess
import sys

import pytest

from scripts.harness.pr_maintenance import MaintenanceError, check_pr

ROOT = Path(__file__).resolve().parent.parent.parent
EXAMPLE = ROOT / "examples"
CONFIG = {"board_path": "docs/plan.md", "board_heading": "Queue", "repository_full_name": "example/demo-todo", "pr_number": 2}


def git(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()


def commit(root):
    git(root, "add", ".")
    git(root, "commit", "-qm", "example")
    return git(root, "rev-parse", "HEAD")


@pytest.fixture
def demo(tmp_path):
    git(tmp_path, "init", "-q")
    git(tmp_path, "config", "user.email", "tests@example.invalid")
    git(tmp_path, "config", "user.name", "Tests")
    shutil.copytree(EXAMPLE / "demo-todo", tmp_path, dirs_exist_ok=True)
    source = (tmp_path / "src/todo.py").read_text()
    (tmp_path / "src/todo.py").write_text(source.split("\n\n\ndef complete")[0] + "\n")
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs/plan.md").write_text("# Plan\n\n## Queue\n\n- APP-2: Mark a task complete\n")
    (tmp_path / "AGENTS.md").write_text("# Working on demo-todo\n\nSee [plan](docs/plan.md).\n")
    base = commit(tmp_path)
    (tmp_path / "src/todo.py").write_text(source)
    (tmp_path / "docs/plan.md").write_text("# Plan\n\n## Queue\n\nNothing queued.\n")
    head = commit(tmp_path)
    return tmp_path, base, head


def test_demo_app_tests_pass():
    result = subprocess.run([sys.executable, "-m", "pytest", "-q", str(EXAMPLE / "demo-todo/tests")], capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr


def test_passing_example_body_is_accepted(demo):
    request = check_pr(*demo, (EXAMPLE / "pr-bodies/passing.md").read_text(), CONFIG)
    assert "docs/plan.md" in request["required_context_files"]
    assert request["code_changed"] is True


def test_failing_example_body_is_blocked(demo):
    with pytest.raises(MaintenanceError, match="Knowledge updates"):
        check_pr(*demo, (EXAMPLE / "pr-bodies/failing.md").read_text(), CONFIG)

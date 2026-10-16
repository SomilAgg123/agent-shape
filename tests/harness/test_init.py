from pathlib import Path
import json
import shutil

from scripts.harness.init import initialize

ROOT = Path(__file__).resolve().parent.parent.parent


def copy_template(tmp_path):
    for name in ["AGENTS.md", ".github", "modules", "examples", "tests"]:
        source = ROOT / name
        if source.is_dir():
            shutil.copytree(source, tmp_path / name, ignore=shutil.ignore_patterns("__pycache__"))
        else:
            shutil.copyfile(source, tmp_path / name)
    return tmp_path


def test_init_fills_placeholders_and_keeps_bend_off_by_default(tmp_path):
    root = copy_template(tmp_path)
    initialize(root, "acme", "Acme builds widgets.", "npm test", "trunk")
    agents = (root / "AGENTS.md").read_text()
    assert "{{" not in agents and "# Working on acme" in agents and "bend" not in agents.lower()
    assert json.loads((root / ".github/agent-shape.json").read_text())["base_branch"] == "trunk"
    assert "branches: [trunk]" in (root / ".github/workflows/pr.yml").read_text()
    assert "run: npm test" in (root / ".github/workflows/validate.yml").read_text()
    assert not (root / ".bend-version").exists()
    assert not (root / "examples").exists()


def test_init_can_enable_the_bend_add_on(tmp_path):
    root = copy_template(tmp_path)
    initialize(root, "acme", "Acme.", enable_bend=True, keep_example=True)
    assert (root / ".bend-version").exists() and (root / "scripts/check_bend.py").exists()
    assert "python scripts/check_bend.py" in (root / "AGENTS.md").read_text()
    assert (root / "examples").exists()


def test_template_has_no_unfilled_placeholders_outside_init_targets():
    for path in ROOT.rglob("*"):
        if path.is_file() and ".git" not in path.parts and path.suffix in {".md", ".yml", ".json", ".py"}:
            if str(path.relative_to(ROOT)) not in {"AGENTS.md", ".github/agent-shape.json"} and path.parent.name != "harness":
                assert "{{PROJECT_" not in path.read_text(), path

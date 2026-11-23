import copy
import json

import pytest

from scripts import pr_maintenance
from tests.test_pr_maintenance import body_with_board_update, commit, merge_inputs, repository


def test_custom_domains_route_review_to_existing_context_owners(repository):
    root, base, _, config = repository
    (root / ".github").mkdir()
    (root / ".github/agent-shape.json").write_text(json.dumps({
        "review_routes": [{"prefixes": ["service/"], "docs": ["docs/service.md"]}],
    }))
    (root / "service").mkdir()
    (root / "service/main.py").write_text("value = 1\n")
    (root / "docs/service.md").write_text("# Service\n\nKeep requests isolated.\n")
    base = commit(root)
    (root / "service/main.py").write_text("value = 2\n")
    head = commit(root)
    body = body_with_board_update().replace("- Updated [board](docs/board.md) to remove completed work.", "No knowledge changes.")
    request = pr_maintenance.check_pr(root, base, head, body, config)
    assert "docs/service.md" in request["required_context_files"]
    assert "docs/backend-steering.md" not in request["required_context_files"]


def test_custom_context_owners_require_knowledge_links(repository):
    root, base, _, config = repository
    (root / ".github").mkdir()
    (root / ".github/agent-shape.json").write_text(json.dumps({"context_prefixes": ["guidance/"]}))
    (root / "guidance").mkdir()
    (root / "guidance/runtime.md").write_text("# Runtime\n\nKeep requests isolated.\n")
    head = commit(root)
    with pytest.raises(pr_maintenance.MaintenanceError, match="guidance/runtime.md"):
        pr_maintenance.check_pr(root, base, head, body_with_board_update(), config)


def test_missing_configured_context_blocks_review(repository):
    root, base, _, config = repository
    (root / ".github").mkdir()
    (root / ".github/agent-shape.json").write_text(json.dumps({"always_review": ["missing.md"]}))
    head = commit(root)
    with pytest.raises(pr_maintenance.MaintenanceError, match="missing.md"):
        pr_maintenance.check_pr(root, base, head, body_with_board_update(), config)


def test_merge_guard_uses_the_captured_project_base_branch(merge_inputs):
    snapshot, request, report = copy.deepcopy(merge_inputs)
    request["base_branch"] = "develop"
    snapshot["pr"]["base"] = "develop"
    pr_maintenance.check_merge(snapshot, request, report)
    snapshot["pr"]["base"] = "main"
    with pytest.raises(pr_maintenance.MaintenanceError, match="develop"):
        pr_maintenance.check_merge(snapshot, request, report)

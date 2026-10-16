import copy
import io
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from scripts.harness import pr_maintenance
from scripts.harness.pr_maintenance import MaintenanceError, check_gate, check_merge, check_pr, check_review


BODY = """## Knowledge updates
No knowledge changes.

## Testing
Red: test_rejects_stale_ticket failed because the completed ticket remained queued.
Green: python -m pytest tests -q passed.
Refactor: No refactoring was needed.

## Maintenance
Ticket: APP-12
Ticket outcome: complete
Ticket reason: Completed the agreed ticket scope.
Context disposition: unchanged
TDD: applied
TDD reason: Added new maintenance behavior.
"""


def git(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()


def commit(root):
    git(root, "add", ".")
    git(root, "commit", "-qm", "fixture")
    return git(root, "rev-parse", "HEAD")


@pytest.fixture
def repository(tmp_path):
    git(tmp_path, "init", "-q")
    git(tmp_path, "config", "user.email", "tests@example.invalid")
    git(tmp_path, "config", "user.name", "Tests")
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs/board.md").write_text("# Work\n\n## To build\n\n- APP-12: Maintenance\n- APP-120: Other task\n\n## Done\n")
    (tmp_path / "docs/usage.md").write_text("# Usage\n\n## Save files\n\nCurrent behavior.\n")
    (tmp_path / "AGENTS.md").write_text("# Guidance\n\n[Usage](docs/usage.md#save-files)\n")
    (tmp_path / "main.py").write_text("value = 1\n")
    base = commit(tmp_path)
    (tmp_path / "docs/board.md").write_text("# Work\n\n## To build\n\n- APP-120: Other task\n\n## Done\n\n- APP-12: Maintenance\n")
    (tmp_path / "main.py").write_text("value = 2\n")
    head = commit(tmp_path)
    return tmp_path, base, head, {"board_path": "docs/board.md", "board_heading": "To build", "repository_full_name": "test/repo", "pr_number": 12}


def body_with_board_update():
    return BODY.replace("No knowledge changes.", "- Updated [board](docs/board.md) to remove completed work.").replace("Context disposition: unchanged", "Context disposition: updated")


def test_completed_ticket_is_removed_without_matching_another_ticket(repository):
    request = check_pr(*repository[:3], body_with_board_update(), repository[3])
    assert request["head_sha"] == repository[2]
    assert request["code_changed"] is True
    assert "docs/board.md" in request["required_context_files"]


def test_completed_ticket_cannot_remain_queued(repository):
    root, base, _, config = repository
    git(root, "checkout", base, "--", "docs/board.md")
    head = commit(root)
    with pytest.raises(MaintenanceError, match="still in"):
        check_pr(root, base, head, BODY, config)


def test_partial_ticket_cannot_disappear_from_queue(repository):
    with pytest.raises(MaintenanceError, match="Partial ticket"):
        check_pr(*repository[:3], body_with_board_update().replace("outcome: complete", "outcome: partial"), repository[3])


def test_plan_ticket_completion_removes_its_delivery_section(repository):
    root, _, _, config = repository
    (root / "docs/board.md").write_text("# Plan\n\n## Build\n\n### PR 1 — First change\n\nBuild this behavior.\n\n### PR 10 — Later change\n\nKeep this pending.\n")
    base = commit(root)
    (root / "docs/board.md").write_text("# Plan\n\n## Build\n\n### PR 10 — Later change\n\nKeep this pending.\n")
    head = commit(root)
    config["board_heading"] = "Build"
    body = body_with_board_update().replace("Ticket: APP-12", "Ticket: PR-1")
    assert check_pr(root, base, head, body, config)["head_sha"] == head
    git(root, "checkout", base, "--", "docs/board.md")
    head = commit(root)
    with pytest.raises(MaintenanceError, match="still in"):
        check_pr(root, base, head, body, config)


def test_ticket_checks_require_a_configured_board(repository):
    with pytest.raises(MaintenanceError, match="board_path"):
        check_pr(*repository[:3], body_with_board_update(), {"board_path": None, "board_heading": "To build"})


def test_untracked_work_requires_a_reason(repository):
    body = body_with_board_update().replace("Ticket: APP-12", "Ticket: none").replace("outcome: complete", "outcome: none").replace("Ticket reason: Completed the agreed ticket scope.", "Ticket reason:")
    with pytest.raises(MaintenanceError, match="Ticket reason"):
        check_pr(*repository[:3], body, repository[3])


def test_knowledge_report_cannot_claim_no_changes_when_context_changed(repository):
    with pytest.raises(MaintenanceError, match="Knowledge updates"):
        check_pr(*repository[:3], BODY, repository[3])


def test_knowledge_report_must_link_every_changed_context_owner(repository):
    root, base, _, config = repository
    (root / "docs/usage.md").write_text("# Usage\n\n## Save files\n\nChanged behavior.\n")
    head = commit(root)
    with pytest.raises(MaintenanceError, match="docs/usage.md"):
        check_pr(root, base, head, body_with_board_update(), config)


def test_knowledge_report_accepts_current_commit_links(repository):
    body = body_with_board_update().replace("(docs/board.md)", f"(https://github.com/test/repo/blob/{repository[2]}/docs/board.md)")
    assert check_pr(*repository[:3], body, repository[3])["head_sha"] == repository[2]


@pytest.mark.parametrize("repository_name,revision", [("other/repo", "current"), ("test/repo", "old")])
def test_knowledge_report_rejects_wrong_repository_or_old_version(repository, repository_name, revision):
    sha = repository[2] if revision == "current" else repository[1]
    body = body_with_board_update().replace("(docs/board.md)", f"(https://github.com/{repository_name}/blob/{sha}/docs/board.md)")
    with pytest.raises(MaintenanceError, match="Knowledge updates"):
        check_pr(*repository[:3], body, repository[3])


@pytest.mark.parametrize("target", ["missing.md", "usage.md#missing-heading"])
def test_changed_context_cannot_introduce_broken_links(repository, target):
    root, base, _, config = repository
    (root / "docs/board.md").write_text(f"# Work\n\n## To build\n\n[Reference]({target})\n")
    head = commit(root)
    with pytest.raises(MaintenanceError, match="Broken"):
        check_pr(root, base, head, body_with_board_update(), config)


def test_context_retirement_requires_repairing_inbound_links(repository):
    root, base, _, config = repository
    (root / "docs/usage.md").unlink()
    head = commit(root)
    body = body_with_board_update().replace("## Testing", f"- Removed [usage](https://github.com/test/repo/blob/{base}/docs/usage.md).\n\n## Testing")
    with pytest.raises(MaintenanceError, match="AGENTS.md"):
        check_pr(root, base, head, body, config)


def test_tdd_requires_actual_failing_and_passing_evidence(repository):
    with pytest.raises(MaintenanceError, match="Red"):
        check_pr(*repository[:3], body_with_board_update().replace("Red: test_rejects_stale_ticket failed because the completed ticket remained queued.", "Red:"), repository[3])


def test_documentation_only_work_does_not_require_tdd(repository):
    root, base, _, config = repository
    git(root, "checkout", base, "--", "main.py")
    head = commit(root)
    body = body_with_board_update().replace("TDD: applied", "TDD: not-applicable").replace("TDD reason: Added new maintenance behavior.", "TDD reason: Documentation only.")
    assert check_pr(root, base, head, body, config)["code_changed"] is False


@pytest.mark.parametrize("result", ["failure", "cancelled", "skipped"])
def test_merge_gate_rejects_incomplete_stages(result):
    pr = {"base": {"sha": "a" * 40}, "head": {"sha": "b" * 40}, "body": BODY}
    with pytest.raises(MaintenanceError, match="validation"):
        check_gate({"validation": result, "context": "success", "review": "success"}, pr, pr)


def test_failed_gate_reports_stage_failure_without_api_access(tmp_path):
    event = tmp_path / "event.json"
    event.write_text(json.dumps({"pull_request": {"base": {"sha": "a" * 40}, "head": {"sha": "b" * 40}, "body": BODY}}))
    environment = {key: value for key, value in os.environ.items() if key != "GH_TOKEN"}
    environment.update(GITHUB_EVENT_PATH=str(event), JOB_RESULTS=json.dumps({"validation": "failure", "context": "success", "review": "skipped"}))
    script = Path(__file__).resolve().parent.parent.parent / "scripts/harness/pr_maintenance.py"
    result = subprocess.run([sys.executable, str(script), "gate"], env=environment, capture_output=True, text=True)
    assert result.returncode == 1
    assert "validation did not succeed: failure" in result.stderr


@pytest.mark.parametrize("field", ["body", "head", "base"])
def test_merge_gate_rejects_stale_pr_evidence(field):
    pr = {"base": {"sha": "a" * 40}, "head": {"sha": "b" * 40}, "body": BODY}
    current = copy.deepcopy(pr)
    current[field] = "Changed description" if field == "body" else {"sha": "c" * 40}
    with pytest.raises(MaintenanceError, match="changed"):
        check_gate(dict.fromkeys(["validation", "context", "review"], "success"), pr, current)


def test_actions_gate_requires_only_deterministic_checks():
    pr = {"base": {"sha": "a" * 40}, "head": {"sha": "b" * 40}, "body": BODY}
    check_gate({"validation": "success", "context": "success"}, pr, pr)


def review_report(request, decision="ready"):
    return {"repository": request["repository"], "pr_number": request["pr_number"], "base_sha": request["base_sha"], "head_sha": request["head_sha"], "body_sha256": request["body_sha256"], "decision": decision, "summary": "Reviewed code and affected context.", "reviewed_context_files": request["required_context_files"], "findings": []}


@pytest.fixture
def merge_inputs(repository):
    request = check_pr(*repository[:3], body_with_board_update(), repository[3])
    request.update(repository="test/repo", pr_number=12)
    snapshot = {
        "repository": "test/repo",
        "pr": {"number": 12, "url": "https://github.com/test/repo/pull/12", "base": "main", "base_sha": request["base_sha"], "head_sha": request["head_sha"], "body": request["body"], "state": "open", "draft": False, "merged": False},
        "runs": [{"id": 91, "name": "PR maintenance", "run_number": 4, "status": "completed", "conclusion": "success"}],
        "jobs": [{"id": index, "run_id": 91, "name": name, "status": "completed", "conclusion": "success"} for index, name in enumerate(["validation / validation", "context / context", "PR maintenance gate"], 1)],
        "ci_evidence": {"repository": "test/repo", "pr_number": 12, "base_sha": request["base_sha"], "head_sha": request["head_sha"], "body_sha256": request["body_sha256"], "run_id": 91, "workflow_ref": "test/repo/.github/workflows/pr.yml@refs/pull/12/merge"},
    }
    return snapshot, request, review_report(request)


def test_merge_guard_returns_the_verified_commit_without_merging(merge_inputs):
    snapshot, request, report = merge_inputs
    result = check_merge(snapshot, request, report)
    assert result == {"repository": "test/repo", "pr_number": 12, "expected_head_sha": request["head_sha"], "ci_run_id": 91}


@pytest.mark.parametrize("field,value", [("draft", True), ("state", "closed"), ("merged", True)])
def test_merge_guard_blocks_prs_that_are_not_ready(merge_inputs, field, value):
    snapshot, request, report = merge_inputs
    snapshot["pr"][field] = value
    with pytest.raises(MaintenanceError, match="open.*ready"):
        check_merge(snapshot, request, report)


@pytest.mark.parametrize("field", ["head_sha", "base_sha", "body"])
def test_merge_guard_blocks_changes_after_agent_review(merge_inputs, field):
    snapshot, request, report = merge_inputs
    snapshot["pr"][field] = "Changed description" if field == "body" else "c" * 40
    with pytest.raises(MaintenanceError, match="revision"):
        check_merge(snapshot, request, report)


def test_merge_guard_rejects_review_of_a_different_pr(merge_inputs):
    snapshot, request, report = merge_inputs
    report["pr_number"] = 13
    with pytest.raises(MaintenanceError, match="pr_number"):
        check_merge(snapshot, request, report)


def test_merge_guard_requires_agent_to_finish_the_review(merge_inputs):
    snapshot, request, report = merge_inputs
    report["decision"] = "changes-required"
    with pytest.raises(MaintenanceError, match="review"):
        check_merge(snapshot, request, report)


def test_merge_guard_rejects_unresolved_findings_even_when_marked_ready(merge_inputs):
    snapshot, request, report = merge_inputs
    report["findings"] = [{"category": "code", "severity": "P1", "file": "main.py", "line": 1, "message": "Unresolved behavioral regression."}]
    with pytest.raises(MaintenanceError, match="findings"):
        check_merge(snapshot, request, report)


@pytest.mark.parametrize("status,conclusion", [("queued", None), ("in_progress", None), ("completed", "failure"), ("completed", "cancelled")])
def test_merge_guard_uses_the_latest_run_instead_of_an_older_success(merge_inputs, status, conclusion):
    snapshot, request, report = merge_inputs
    snapshot["runs"].append({"id": 92, "name": "PR maintenance", "run_number": 5, "status": status, "conclusion": conclusion})
    with pytest.raises(MaintenanceError, match="latest"):
        check_merge(snapshot, request, report)


@pytest.mark.parametrize("conclusion", ["failure", "cancelled", "skipped"])
def test_merge_guard_checks_each_required_job(merge_inputs, conclusion):
    snapshot, request, report = merge_inputs
    snapshot["jobs"][0]["conclusion"] = conclusion
    with pytest.raises(MaintenanceError, match="validation"):
        check_merge(snapshot, request, report)


def test_merge_guard_rejects_jobs_from_another_run(merge_inputs):
    snapshot, request, report = merge_inputs
    snapshot["jobs"][0]["run_id"] = 90
    with pytest.raises(MaintenanceError, match="run"):
        check_merge(snapshot, request, report)


def test_merge_guard_requires_current_ci_evidence(merge_inputs):
    snapshot, request, report = merge_inputs
    snapshot["ci_evidence"]["body_sha256"] = "c" * 64
    with pytest.raises(MaintenanceError, match="CI evidence"):
        check_merge(snapshot, request, report)


def test_merge_guard_requires_the_expected_workflow_source(merge_inputs):
    snapshot, request, report = merge_inputs
    snapshot["ci_evidence"]["workflow_ref"] = "test/repo/.github/workflows/other.yml@refs/pull/12/merge"
    with pytest.raises(MaintenanceError, match="workflow"):
        check_merge(snapshot, request, report)


@pytest.mark.parametrize("duplicate", [False, True])
def test_merge_guard_rejects_missing_or_ambiguous_job_evidence(merge_inputs, duplicate):
    snapshot, request, report = merge_inputs
    job = snapshot["jobs"].pop()
    if duplicate:
        snapshot["jobs"].extend([job, copy.deepcopy(job)])
    with pytest.raises(MaintenanceError, match="Required job"):
        check_merge(snapshot, request, report)


@pytest.mark.parametrize("field,value", [("run_id", 90), ("head_sha", "c" * 40), ("repository", "other/repo")])
def test_merge_guard_rejects_unrelated_ci_evidence(merge_inputs, field, value):
    snapshot, request, report = merge_inputs
    snapshot["ci_evidence"][field] = value
    with pytest.raises(MaintenanceError, match="CI evidence"):
        check_merge(snapshot, request, report)


def test_review_preparation_rejects_uncommitted_changes(repository, merge_inputs, monkeypatch):
    root = repository[0]
    monkeypatch.setattr(pr_maintenance, "ROOT", root)
    (root / "main.py").write_text("value = 3\n")
    with pytest.raises(MaintenanceError, match="clean checkout"):
        pr_maintenance.prepare_request(merge_inputs[0])


def test_review_preparation_requires_the_current_base_in_the_branch(repository, merge_inputs, monkeypatch):
    root, base, head, _ = repository
    snapshot, _, _ = merge_inputs
    monkeypatch.setattr(pr_maintenance, "ROOT", root)
    git(root, "checkout", "--detach", base)
    (root / "main.py").write_text("value = 4\n")
    snapshot["pr"]["base_sha"] = commit(root)
    git(root, "checkout", "--detach", head)
    with pytest.raises(MaintenanceError, match="current base"):
        pr_maintenance.prepare_request(snapshot)


def test_review_and_merge_commands_require_completion_before_producing_a_plan(repository, merge_inputs, monkeypatch, tmp_path_factory):
    root, _, _, config = repository
    snapshot, _, _ = merge_inputs
    (root / ".github").mkdir()
    (root / ".github/agent-shape.json").write_text(json.dumps(config))
    (root / ".github/review.schema.json").write_text((pr_maintenance.ROOT / ".github/review.schema.json").read_text())
    (root / ".github/review-prompt.md").write_text("# Review\n\nReview behavior and context.\n")
    snapshot["pr"]["head_sha"] = commit(root)
    snapshot["pr"]["body"] = body_with_board_update().replace("## Testing", "- Created [review](.github/review-prompt.md) criteria.\n\n## Testing")
    monkeypatch.setattr(pr_maintenance, "ROOT", root)
    records = tmp_path_factory.mktemp("review-records")
    snapshot_path, request_path, report_path, plan_path = [records / name for name in ["snapshot.json", "request.json", "report.json", "plan.json"]]
    snapshot_path.write_text(json.dumps(snapshot))
    monkeypatch.setattr(sys, "argv", ["maintenance", "prepare-review", "--snapshot", str(snapshot_path), "--output", str(request_path), "--report-template", str(report_path)])
    pr_maintenance.main()
    request = json.loads(request_path.read_text())
    report = json.loads(report_path.read_text())
    assert report["decision"] == "changes-required"
    monkeypatch.setattr(sys, "argv", ["maintenance", "merge-guard", "--snapshot", str(snapshot_path), "--report", str(report_path), "--output", str(plan_path)])
    with pytest.raises(SystemExit) as error:
        pr_maintenance.main()
    assert error.value.code == 1
    assert not plan_path.exists()
    report_path.write_text(json.dumps(review_report(request)))
    snapshot["ci_evidence"].update({key: request[key] for key in ["head_sha", "body_sha256"]})
    snapshot_path.write_text(json.dumps(snapshot))
    pr_maintenance.main()
    assert json.loads(plan_path.read_text())["expected_head_sha"] == request["head_sha"]


def test_actions_gate_publishes_evidence_for_the_verified_live_revision(merge_inputs, monkeypatch, tmp_path, capsys):
    snapshot, request, _ = merge_inputs
    live = {"base": {"ref": "main", "sha": request["base_sha"]}, "head": {"sha": request["head_sha"]}, "body": request["body"]}
    event_path = tmp_path / "event.json"
    event_path.write_text(json.dumps({"number": 12, "pull_request": live}))
    for key, value in {"GITHUB_EVENT_PATH": str(event_path), "JOB_RESULTS": '{"validation":"success","context":"success"}', "GITHUB_REPOSITORY": "test/repo", "GITHUB_RUN_ID": "91", "GITHUB_WORKFLOW_REF": snapshot["ci_evidence"]["workflow_ref"], "GH_TOKEN": "test-token"}.items():
        monkeypatch.setenv(key, value)
    monkeypatch.setattr(pr_maintenance, "urlopen", lambda *_args, **_kwargs: io.StringIO(json.dumps(live)))
    monkeypatch.setattr(sys, "argv", ["maintenance", "gate"])
    pr_maintenance.main()
    line = next(line for line in capsys.readouterr().out.splitlines() if line.startswith("PR_MAINTENANCE_EVIDENCE="))
    assert json.loads(line.split("=", 1)[1]) == snapshot["ci_evidence"]


def test_agent_report_requires_current_revision_and_context_coverage(repository):
    request = check_pr(*repository[:3], body_with_board_update(), repository[3])
    report = review_report(request)
    check_review(report, request)
    report["head_sha"] = "c" * 40
    with pytest.raises(MaintenanceError, match="head_sha"):
        check_review(report, request)
    report["head_sha"] = request["head_sha"]
    report["reviewed_context_files"] = []
    with pytest.raises(MaintenanceError, match="context"):
        check_review(report, request)


def test_agent_findings_are_preserved_for_human_review(repository):
    request = check_pr(*repository[:3], body_with_board_update(), repository[3])
    report = review_report(request, "changes-required")
    report["findings"] = [{"category": "context", "severity": "P1", "file": "docs/usage.md", "line": 5, "message": "The usage text conflicts with the changed behavior."}]
    check_review(report, request)
    assert report["findings"][0]["severity"] == "P1"


def test_agent_report_rejects_malformed_findings(repository):
    request = check_pr(*repository[:3], body_with_board_update(), repository[3])
    with pytest.raises(MaintenanceError, match="report"):
        check_review({"findings": "approved"}, request)

import copy
import io
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from scripts import pr_maintenance
from scripts.pr_maintenance import MaintenanceError, check_gate, check_merge, check_pr, check_review


BODY = """## Knowledge updates
No knowledge changes.

## Validation

| Check | Result and evidence |
| --- | --- |
| Python tests | Passed all tests. |
| Spend | $0 |
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
    (tmp_path / "docs/board.md").write_text("# Work\n\n## To build\n\n- TASK-12: Maintenance\n- TASK-120: Other task\n\n## Done\n")
    (tmp_path / "docs/usage.md").write_text("# Usage\n\n## Save files\n\nCurrent behavior.\n")
    (tmp_path / "AGENTS.md").write_text("# Guidance\n\n[Usage](docs/usage.md#save-files)\n")
    (tmp_path / "main.py").write_text("value = 1\n")
    base = commit(tmp_path)
    (tmp_path / "docs/board.md").write_text("# Work\n\n## To build\n\n- TASK-120: Other task\n\n## Done\n\n- TASK-12: Maintenance\n")
    (tmp_path / "main.py").write_text("value = 2\n")
    head = commit(tmp_path)
    return tmp_path, base, head, {"repository_full_name": "test/repo", "pr_number": 12}


def body_with_board_update():
    return BODY.replace("No knowledge changes.", "- Updated [board](docs/board.md) to remove completed work.")


@pytest.mark.parametrize("format", ["table", "bullets"])
def test_validation_accepts_grouped_results_without_maintenance_fields(repository, format):
    body = body_with_board_update()
    if format == "bullets":
        body = body.replace("| Check | Result and evidence |\n| --- | --- |\n", "")
        body = "\n".join("- " + ": ".join(line.strip("| ").split(" | ", 1)) if line.startswith("|") else line for line in body.splitlines())
    request = check_pr(*repository[:3], body, repository[3])
    assert request["head_sha"] == repository[2]
    assert request["code_changed"] is True
    assert "docs/board.md" in request["required_context_files"]


@pytest.mark.parametrize("missing", ["Validation", "Spend"])
def test_validation_requires_validation_and_spend(repository, missing):
    body = body_with_board_update()
    if missing == "Validation":
        body = body.split("## Validation")[0]
    else:
        body = "\n".join(line for line in body.splitlines() if not line.startswith(f"| {missing} |"))
    with pytest.raises(MaintenanceError, match=missing):
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
    body = body_with_board_update().replace("## Validation", f"- Removed [usage](https://github.com/test/repo/blob/{base}/docs/usage.md).\n\n## Validation")
    with pytest.raises(MaintenanceError, match="AGENTS.md"):
        check_pr(root, base, head, body, config)


def test_validation_rejects_blank_spend(repository):
    with pytest.raises(MaintenanceError, match="Spend"):
        check_pr(*repository[:3], body_with_board_update().replace("$0", ""), repository[3])


def test_documentation_only_work_accepts_test_results_and_spend(repository):
    root, base, _, config = repository
    git(root, "checkout", base, "--", "main.py")
    head = commit(root)
    body = body_with_board_update()
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
    script = Path(__file__).resolve().parent.parent / "scripts/pr_maintenance.py"
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
    return {"repository": request["repository"], "pr_number": request["pr_number"], "base_sha": request["base_sha"], "head_sha": request["head_sha"], "body_sha256": request["body_sha256"], "decision": decision, "summary": "Reviewed code and affected context.", "reviewed_context_files": request["required_context_files"], "context_review": [{"file": path, "verdict": "ready", "reason": "Removed completed work so the next task is selected from the remaining queue."} for path in request["changed_context_files"]], "language_review": {"verdict": "ready", "reason": "Explains the completed work and test results in familiar words."}, "findings": []}


@pytest.mark.parametrize("field", ["context_review", "language_review", "both"])
def test_review_rejects_blanket_approval_without_specific_checks(repository, field):
    request = check_pr(*repository[:3], body_with_board_update(), repository[3])
    report = review_report(request)
    for name in ["context_review", "language_review"] if field == "both" else [field]:
        del report[name]
    with pytest.raises(MaintenanceError, match="report"):
        check_review(report, request)


@pytest.mark.parametrize("change", ["omitted", "duplicate", "unrelated", "blank_reason"])
def test_review_requires_one_reason_for_each_changed_context_file(repository, change):
    request = check_pr(*repository[:3], body_with_board_update(), repository[3])
    report = review_report(request)
    if change == "omitted":
        report["context_review"] = []
    elif change == "duplicate":
        report["context_review"] *= 2
    elif change == "unrelated":
        report["context_review"][0]["file"] = "docs/usage.md"
    else:
        report["context_review"][0]["reason"] = "  \n"
    with pytest.raises(MaintenanceError):
        check_review(report, request)


@pytest.mark.parametrize("field", ["context_review", "language_review"])
def test_review_cannot_approve_flagged_context_or_language(merge_inputs, field):
    snapshot, request, report = merge_inputs
    item = report[field][0] if field == "context_review" else report[field]
    item.update(verdict="changes-required", reason="Remove the repeated milestone recap." if field == "context_review" else "Explain transient transfer recovery in familiar words.")
    with pytest.raises(MaintenanceError, match="ready"):
        check_review(report, request)
    report["decision"] = "changes-required"
    check_review(report, request)
    with pytest.raises(MaintenanceError, match="review"):
        check_merge(snapshot, request, report)


def test_context_review_covers_removed_files(repository):
    root, base, _, config = repository
    (root / "docs/usage.md").unlink()
    (root / "AGENTS.md").write_text("# Guidance\n")
    head = commit(root)
    body = body_with_board_update().replace("## Validation", f"- Updated [guidance](AGENTS.md).\n- Removed [usage](https://github.com/test/repo/blob/{base}/docs/usage.md).\n\n## Validation")
    request = check_pr(root, base, head, body, config)
    assert request["changed_context_files"] == ["AGENTS.md", "docs/board.md", "docs/usage.md"]
    report = review_report(request)
    check_review(report, request)
    report["context_review"] = [item for item in report["context_review"] if item["file"] != "docs/usage.md"]
    with pytest.raises(MaintenanceError, match="context"):
        check_review(report, request)


def test_unchanged_context_needs_no_invented_justification(repository):
    root, base, _, config = repository
    git(root, "checkout", base, "--", "docs/board.md")
    head = commit(root)
    body = BODY
    request = check_pr(root, base, head, body, config)
    assert request["changed_context_files"] == []
    report = review_report(request)
    assert report["context_review"] == []
    check_review(report, request)


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
def test_merge_guard_blocks_changes_after_codex_review(merge_inputs, field):
    snapshot, request, report = merge_inputs
    snapshot["pr"][field] = "Changed description" if field == "body" else "c" * 40
    with pytest.raises(MaintenanceError, match="revision"):
        check_merge(snapshot, request, report)


def test_merge_guard_rejects_review_of_a_different_pr(merge_inputs):
    snapshot, request, report = merge_inputs
    report["pr_number"] = 13
    with pytest.raises(MaintenanceError, match="pr_number"):
        check_merge(snapshot, request, report)


def test_merge_guard_requires_codex_to_finish_the_review(merge_inputs):
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
    (root / ".github/codex-review.schema.json").write_text((pr_maintenance.ROOT / ".github/codex-review.schema.json").read_text())
    (root / ".github/codex-review.md").write_text("# Review\n\nReview behavior and context.\n")
    snapshot["pr"]["head_sha"] = commit(root)
    snapshot["pr"]["body"] = body_with_board_update().replace("## Validation", "- Created [review](.github/codex-review.md) criteria.\n\n## Validation")
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


def test_codex_report_requires_current_revision_and_context_coverage(repository):
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


def test_codex_findings_are_preserved_for_human_review(repository):
    request = check_pr(*repository[:3], body_with_board_update(), repository[3])
    report = review_report(request, "changes-required")
    report["findings"] = [{"category": "context", "severity": "P1", "file": "docs/usage.md", "line": 5, "message": "The usage text conflicts with the changed behavior."}]
    check_review(report, request)
    assert report["findings"][0]["severity"] == "P1"


def test_codex_report_rejects_malformed_findings(repository):
    request = check_pr(*repository[:3], body_with_board_update(), repository[3])
    with pytest.raises(MaintenanceError, match="report"):
        check_review({"findings": "approved"}, request)


@pytest.mark.parametrize("text,limit", [(" ".join(["word"] * 26) + ".", 25), ("1. " + " ".join(["word"] * 21) + ".", 20)])
def test_writing_check_rejects_long_descriptions_and_numbered_steps(text, limit):
    with pytest.raises(MaintenanceError, match=f"ASD-STE100.*{limit}"):
        pr_maintenance.check_writing(text, "PR description")
    pr_maintenance.check_writing(text.replace("word ", "", 1), "PR description")


def test_writing_check_preserves_technical_evidence_and_counts_link_labels():
    evidence = " ".join(["argument"] * 30)
    pr_maintenance.check_writing(f"Run `{evidence}`.\n\n```sh\n{evidence}\n```\n\n> {evidence}\n\nRead [usage](https://example.com/a.b).", "guide.md")
    sentence = " ".join(["word"] * 25)
    pr_maintenance.check_writing(f'“{sentence}.” {sentence}.', "guide.md")
    with pytest.raises(MaintenanceError, match="ASD-STE100"):
        pr_maintenance.check_writing(f"Read [{evidence}](https://example.com).", "guide.md")


def test_pr_check_validates_body_and_only_changed_markdown_passages(repository):
    root, base, head, config = repository
    long_sentence = " ".join(["word"] * 26) + "."
    with pytest.raises(MaintenanceError, match="PR description.*ASD-STE100"):
        check_pr(root, base, head, body_with_board_update() + "\n" + long_sentence, config)
    usage = root / "docs/usage.md"
    usage.write_text(usage.read_text() + "\n" + " ".join(["word"] * 13) + "\n" + " ".join(["word"] * 13) + ".\n")
    base_with_old_prose = commit(root)
    usage.write_text(usage.read_text() + "\nNew behavior.\n")
    head = commit(root)
    body = BODY
    body = body.replace("No knowledge changes.", "Updated [usage](docs/usage.md) with the new behavior.")
    check_pr(root, base_with_old_prose, head, body, config)
    usage.write_text(usage.read_text().replace("word", "changed", 1))
    head = commit(root)
    with pytest.raises(MaintenanceError, match="docs/usage.md.*ASD-STE100"):
        check_pr(root, base_with_old_prose, head, body, config)

# Writing readable pull requests

Apply the [ASD-STE100 language rules](../AGENTS.md#language-and-naming) to PR
titles, descriptions and review replies. Write for a product or executive reader
who understands the goal but has not read the code. Describe completed work in past tense. Lead with
the capability delivered and why it mattered, not the implementation activity.
Use familiar words, active sentences, and concrete examples. Omit file inventories, endpoint
paths, implementation narration, and repeated milestone history unless they
help the reader make a decision. Knowledge updates explicitly links affected
context files; keep that section focused on meaningful knowledge changes.

## Title and size

Use `[S] Title`, `[M] Title`, `[L] Title`, or `[XL] Title`. The title after the
prefix is 5–10 words describing the high-level capability built.

- S: one narrow behavior, small fix, or documentation change.
- M: several connected behaviors within one component or workflow step.
- L: substantial changes across components, with a larger review surface.
- XL: too large for one milestone; split into smaller PRs before building.

Choose size by scope and review effort, not a line-count threshold. Prefer small, bounded PRs. Example: `[S] Compare saved versions before applying edits`.

Name the action or outcome in the title. For technical maintenance, name the
concrete problem fixed. These examples illustrate wording, not planned features:

| Technical wording | Plain title |
| --- | --- |
| Implement incremental draft persistence | [S] Save drafts automatically while users edit |
| Add transient upload failure recovery | [S] Retry failed uploads after temporary connection errors |
| Expose task input provenance | [S] Show which files a task used |

## Description

Use the repository template. Word ranges exclude headings; do not pad to meet
a minimum or compress sentences into jargon to fit. Target under 150 words for
the main description; allow Validation and Knowledge updates to grow
enough to cover new tests and meaningful context changes.

- Description: 10–20 words explaining the capability delivered, in past tense.
- What changed: 1–3 bullets, 10–20 words each. Start each with what was made
  possible or changed for the user, in past tense. For example, "Enabled
  comparison of saved versions before applying edits" rather than "Added
  comparison logic and fixtures."
- Knowledge updates (every PR): concise past-tense bullets, normally 10–20
  words each, with links to affected knowledge/context files. Lead with Updated,
  Created, Moved, or Removed and describe the knowledge changed. Each newly
  created file gets a bullet explaining its contents; group related updates
  when clear, and link removals to the prior version. If none, write "No
  knowledge changes." Do not invent a documentation change to fill the section.
- Validation: use only the template's check table and added-test table.
  Keep the existing check names; do not add rows, subsections, bullets, or paragraphs.
  Omit inapplicable checks, except Spend. Omit the added-test table when no tests were added.
  Put each result and relevant limit in its existing row.
  Include commands and pass/fail counts. Use `Spend` for the total paid model
  cost in USD. If no paid calls ran, write `$0` without extra explanation.
  If paid calls ran but their cost is unavailable, state that the cost is unknown.
  Include every new test by exact name with a 10–20 word explanation of its
  behavior. Keep this coverage visible within Validation.
  When Bend is enabled, report proof, generated-output and regression results for every code PR.
  Include the pinned version and unresolved blockers. Skipped checks are incomplete validation, even when Bend files were unchanged.
- Screenshots (UI PRs): embed desktop web screenshots of the changed UI in the
  PR description. Include relevant viewport screenshots for responsive changes. Omit this
  section for PRs without UI edits.
- Design steering (UI PRs): 10–20 words per proposed principle, with a link
  to `docs/frontend-steering.md` and approval status. If none, say "No new
  design steering proposed." Existing guidance consolidated for review should
  be labeled as such, not presented as new guidance.

Test explanations must describe the logical behavior covered: what happens,
under what condition, and what stays correct. Do not narrate mocks, SQL,
internal functions, or assertions. Include the meaning of parameterized cases
in plain language. Report final results, relevant coverage, and unresolved failures.
Do not include test-development history, TDD chronology, or whether tests failed
before implementation. Say when answers are simulated rather than real AI responses.

### Plain-language pass

Check the prose against the ASD-STE100 rules in AGENTS.md. Keep exact technical
identifiers and required template fields. The section word ranges do not
replace the sentence limits.

Before opening or updating a PR, edit the description once for a reader who
knows the product but has not read the code. State the problem, what changed,
and how it was checked in short, direct sentences. Replace technical shorthand
with the behavior it describes. Write "retried failed uploads" instead of
"implemented transient transfer recovery." Write "kept saved history unchanged"
instead of "preserved append-only invariants." Explain a necessary technical term on
first use. Keep exact test names and commands where needed, but describe their
results in familiar words. Remove repeated claims. Keep relevant limits and
failure conditions with their validation result.

## Actions maintenance

[PR maintenance](../.github/workflows/pr.yml) runs validation and context checks for every PR into the configured base branch.
Add project tests and build commands to the validation workflow. Bend checks run only when enabled.
Code/context review uses the current Codex chat; Actions makes no model calls.
CI checks links, validation evidence and ASD-STE100 sentence limits. It checks the PR
description and changed Markdown passages, including their unchanged continuation
lines. Numbered steps have a 20-word limit. Other sentences have a 25-word limit.
Code blocks and quoted evidence are excluded. Inline code counts as one term;
link labels count as prose. Existing passages outside the diff remain unchanged.
These checks do not certify full ASD-STE100 compliance. The required review checks
terms, voice, instructions and technical meaning, including titles and UI text.
Apply the
[review criteria](../.github/codex-review.md) before opening or updating a PR.
The Codex merge guard requires a reason for every changed context file and a
separate language verdict; missing checks or requested changes block approval.

### Required evidence

Complete the [template](../.github/pull_request_template.md):

- Knowledge updates must link every changed context owner at the current head
  (removed files at the base), or say exactly "No knowledge changes."
- Use the `Spend` row within Validation. Report the paid model cost;
  use `$0` when no paid calls ran.

Do not add a Maintenance section or ticket bookkeeping fields. The diff identifies
changed context files; Knowledge updates explains their changes.
Use only Python tests, UI tests, Browser checks, Build and interface, Bend, and Spend in the check table.
Do not add PR checks, UI comparison, New primitives, or other rows.
Omit Run details and What remains sections. TDD remains a development rule, not a PR reporting section.

### Review and merge through Codex

Keep snapshots and reports outside the repository. Use trusted, fresh GitHub tool
results; the guard checks consistency, not their origin or review quality.

1. Save `/tmp/pr-snapshot.json` with `repository` in owner/name form and `pr`
   containing the complete `get_pr_info` result. Fetch the refs and use a clean
   checkout of its head or merge commit. Its branch must include the current base.
   Prepare the request, [review prompt](../.github/codex-review.md), and report:

   ```bash
   python scripts/pr_maintenance.py prepare-review --snapshot /tmp/pr-snapshot.json --output /tmp/pr-request.json --prompt /tmp/pr-review-prompt.md --report-template /tmp/pr-review.json
   ```

2. Complete the review in this chat and validate the report:

   ```bash
   python scripts/pr_maintenance.py review --request /tmp/pr-request.json --report /tmp/pr-review.json
   ```

3. Refresh the PR snapshot. Add `runs` from `fetch_commit_workflow_runs` for its
   head and `jobs` from `fetch_workflow_run_jobs` for the latest `PR maintenance`
   run by `run_number`. Copy the JSON after `PR_MAINTENANCE_EVIDENCE=` in that
   run's gate logs into `ci_evidence`, then check:

   ```bash
   python scripts/pr_maintenance.py merge-guard --snapshot /tmp/pr-snapshot.json --report /tmp/pr-review.json --output /tmp/pr-merge-plan.json
   ```

4. Retain a compact `COMMENT` review through `add_review_to_pr`, anchored to the plan's `expected_head_sha`.
   Include base/head, description hash, CI run URL, reviewed context files, necessity verdict and guard result.
   Verify the saved fields with
   `list_pull_request_reviews` before merging; keep receipts out of repo context.

5. Refresh the snapshot and repeat the guard after recording the receipt.
   Merge only after user authorization and a successful guard.
   Pass the plan's repository, PR number and `expected_head_sha` to the merge tool.
   Base, head or description changes require new review/CI evidence and a new receipt.
   Refresh and repeat the guard after a failed merge.

This local guard does not configure repository branch protection.
Configure repository protection separately when server enforcement is needed.

For local tooling, install `requirements-dev.txt`.
Use the [Bend setup](bend.md) only when the project enables Bend.

## Reviewing design steering

Before opening or updating a UI PR, review the chat for explicit guidance that
should shape future screens. Exercise high discretion: a PR may yield none,
one, or occasionally several principles. Record only reusable direction;
exclude isolated layout fixes, agent-invented preferences, and duplicates.
Propose qualifying changes in `docs/frontend-steering.md` for user review and
approval. Log the proposed principles, file link, and pending approval visibly
under Design steering in the PR. Do not promote a proposal to approved guidance
until the user approves it. If nothing qualifies, state that briefly in the PR.

## Reviewing PR feedback

When the user leaves PR comments, fetch and review every comment. Discuss each
in chat with one concise bullet explaining current behavior, rationale, and
any proposed change. Make implementation changes after alignment. Update
workflow instructions immediately when explicitly requested; do not post GitHub
replies unless authorized.

## Documentation review

At each PR or relevant change, review the affected documents using the
[tracking and retention policy](README.md). Update current state in place and
remove superseded/contradictory text; no documentation edit is needed when the
state did not change. Keep PR-local discussion, test transcripts, and handoffs
out of active instructions. Apply the file contract and matching-history review
when creating/splitting/retiring context files.
Before a major product update, new product phase, or roadmap revision, load the history index and decision trace pages.
Compare them with current principles and scope.
A broad roadmap review reads all retained product decision traces; a focused
major update reads the affected topics in full. An index scan alone is not the
review. Retain selected traces/evidence under the policy; do not append a
progress entry per PR.

## PR transitions

Keep PR descriptions focused on their completed change and relevant validation
limits. Do not include next-PR instructions, required reading for another task,
or a next-chat prompt. Keep Knowledge updates in every PR and omit unused
optional sections; documentation-only PRs
report documentation checks without inventing TDD tests or failing results.

At each PR transition, provide the copy-paste handoff prompt in chat only.
Include the repository, base branch, PR status, agreed scope, next checkpoint,
task-relevant reading, validation limits, and TDD/review requirements.
Distinguish proposed scope from approved work; do not require every document.

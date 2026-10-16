# Writing readable pull requests

Apply the [language and naming rules](../AGENTS.md#language-and-naming) to titles
and descriptions. Write for a product or executive reader who understands the
goal but has not read the code. Describe completed work in past tense. Lead with
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

Choose size by scope and review effort, not a line-count threshold. Prefer S.
Example: `[S] Show which files were used for each answer`.

Name the action or outcome in the title. For technical maintenance, name the
concrete problem fixed. These examples illustrate wording, not planned features:

| Technical wording | Plain title |
| --- | --- |
| Implement incremental draft persistence | [S] Save drafts automatically while users edit |
| Add transient upload failure recovery | [S] Retry failed uploads after temporary connection errors |
| Expose query-context provenance | [S] Show which context files were used for each answer |

## Description

Use the repository template. Word ranges exclude headings; do not pad to meet
a minimum. Target under 150 words for the main description; allow the Testing
and Knowledge updates lists to grow enough to cover new tests and meaningful
context changes. Collapse commands and detailed run evidence.

- Description: 10–20 words explaining the capability delivered, in past tense.
- What changed: 1–3 bullets, 10–20 words each. Start each with what was made
  possible or changed for the user, in past tense. For example, "Enabled
  previews of saved changes before publishing" rather than "Added
  an evaluator and fixtures."
- Knowledge updates (every PR): concise past-tense bullets, normally 10–20
  words each, with links to affected knowledge/context files. Lead with Updated,
  Created, Moved, or Removed and describe the knowledge changed. Each newly
  created file gets a bullet explaining its contents; group related updates
  when clear, and link removals to the prior version. If none, write "No
  knowledge changes." Do not invent a documentation change to fill the section.
- Testing: list every new test by exact name, with a 10–20 word plain-language
  description of the logical behavior it verified. Keep this list visible.
  Add a 15–30 word result summary stating whether real AI was used.
  For code PRs, report every check required by [AGENTS.md](../AGENTS.md),
  including enabled add-ons; skipped checks are incomplete validation.
- Screenshots (UI PRs): embed desktop web screenshots of the changed UI in the
  PR description. Mobile screenshots are not needed at this stage. Omit this
  section for PRs without UI edits.
- Design steering (UI PRs): 10–20 words per proposed principle, with a link
  to `docs/frontend-steering.md` and approval status. If none, say "No new
  design steering proposed." Existing guidance consolidated for review should
  be labeled as such, not presented as new guidance.
- What remains: omit if unnecessary; otherwise 10–25 words about a relevant limit.
- Run details (collapsed): 20–40 words summarizing failing/passing results,
  including the final command. Avoid repeating the visible test descriptions.

Make the opening understandable without reading the code: state what happened
before and what the change made possible when that helps explain the problem.
For example: "Failed uploads previously required a manual restart. Temporary
connection failures are now retried automatically." Keep technical terms and
identifiers where they help review correctness, risk, or compatibility; briefly
explain unfamiliar terms. Preserve meaningful limits, such as which failures
are retried, rather than simplifying them into an unsupported claim.

Test explanations must describe the logical behavior covered: what happens,
under what condition, and what stays correct. Do not narrate mocks, SQL,
internal functions, or assertions. Include the meaning of parameterized cases
in plain language. Distinguish tests written before implementation from later
regression checks. Report actual failures honestly; if an integration test
already passes because it exercises existing behavior, say so. Do not manufacture
a failure. Say when answers are simulated rather than real AI responses.

## Actions maintenance

[PR maintenance](../.github/workflows/pr.yml) runs the project's validation
(plus enabled add-ons) and ticket/context checks for every
PR into the configured base branch. Code/context review happens in your coding
agent's chat; Actions makes no model calls.

### PR metadata

Complete the [template](../.github/pull_request_template.md):

- Use stable ticket IDs such as `PR-2` for numbered plan sections. The
  [configuration](../.github/agent-shape.json) defines the queue. Completed
  tickets must exist in the base queue; remove their queued section or list item
  in the same PR. Partial tickets retain their remaining scope. Use `none` with a
  reason for untracked work.
- Knowledge updates must link every changed context owner at the current head
  (removed files at the base), or say exactly "No knowledge changes." Match
  `Context disposition` to those changes.
- For `TDD: applied`, include actual `Red`, `Green`, and `Refactor` evidence.
  Use `not-applicable` with a reason for documentation or changes adding no behavior.

### Review and merge guard

Keep snapshots and reports outside the repository. Use trusted, fresh GitHub tool
results; the guard checks consistency, not their origin or review quality.

1. Save `/tmp/pr-snapshot.json` with `repository` in owner/name form and `pr`
   containing the complete `get_pr_info` result. Fetch the refs and use a clean
   checkout of its head or merge commit. Its branch must include the current base.
   Prepare the request, [review prompt](../.github/review-prompt.md), and report:

   ```bash
   python scripts/harness/pr_maintenance.py prepare-review --snapshot /tmp/pr-snapshot.json --output /tmp/pr-request.json --prompt /tmp/pr-review-prompt.md --report-template /tmp/pr-review.json
   ```

2. Complete the review in the agent chat and validate the report:

   ```bash
   python scripts/harness/pr_maintenance.py review --request /tmp/pr-request.json --report /tmp/pr-review.json
   ```

3. Refresh the PR snapshot. Add `runs` from `fetch_commit_workflow_runs` for its
   head and `jobs` from `fetch_workflow_run_jobs` for the latest `PR maintenance`
   run by `run_number`. Copy the JSON after `PR_MAINTENANCE_EVIDENCE=` in that
   run's gate logs into `ci_evidence`, then check:

   ```bash
   python scripts/harness/pr_maintenance.py merge-guard --snapshot /tmp/pr-snapshot.json --report /tmp/pr-review.json --output /tmp/pr-merge-plan.json
   ```

4. Retain a compact `COMMENT` review through `add_review_to_pr`, anchored to the
   plan's `expected_head_sha`: base/head, description hash, CI run URL, reviewed
   context files, necessity verdict, and guard result. Verify the saved fields with
   `list_pull_request_reviews` before merging; keep receipts out of repo context.

5. Refresh the snapshot and repeat the guard after recording the receipt. Merge
   only after user authorization and a successful guard, passing the plan's
   repository, PR number and `expected_head_sha` to the merge tool. Base, head or
   description changes require new review/CI evidence and a new receipt; refresh
   and repeat the guard after a failed merge.

GitHub's merge button and direct pushes can bypass this local workflow unless
branch protection requires the `PR maintenance gate` check.

For local tooling, install `requirements-dev.txt`. Tool names such as
`get_pr_info` or `add_review_to_pr` refer to whatever GitHub tools your agent
has (GitHub MCP, `gh api`); capture the same JSON fields.

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
when creating/splitting/retiring context files. Before a major product update,
new product phase, or roadmap revision, load the history index and decision
trace pages into context, then compare them with current principles/scope.
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

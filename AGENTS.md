# Working on {{PROJECT_NAME}}

{{PROJECT_DESCRIPTION}}
Approved delivery scope and review gates live in `docs/plan.md`.

## Always apply

- Keep work within the user's agreed PR scope. The user owns product/design
  decisions. Change software only when requested; proposed scope is not approved
  scope. Keep the project simple.
  Architecture work follows the planning and delivery review gates in
  `docs/plan.md`; do not start implementation or concurrent agents early.
- Build on existing architecture and reusable behavior before adding parallel
  implementations. When replacing a feature within the agreed scope, remove its
  superseded UI, routes, components and unused code instead of leaving deprecated
  flows alongside the replacement. Preserve stored data, evidence and supported
  integrations.
- Do not add explanatory comments outside Bend. Preserve existing Bend files
  and their comments, including setup/docs, laws, proofs, and generated output;
  flag policy conflicts to the user before editing them. Keep lint/type/build
  checks and functional directives; prefer equivalent configuration when viable.
  Use clear names/structure and retain essential rationale in its owning doc
  only when it meets the knowledge-retention rules.
- Use TDD for new software behavior: meaningful failing tests, implementation,
  then refactoring. For documentation-only changes, check links and consistency.
- Bend is optional and disabled by default. When enabled, run all pinned
  proof, generation and regression checks before opening or updating any code PR.
  Use `docs/bend.md` for setup. Missing tools or skipped checks are blockers.
  These checks apply even when Bend files are unchanged.
- Stop at each PR milestone for feedback before starting the next stage.
  Update API and harness documentation when their contracts change.
- Before merging through Codex, follow the
  [review and merge guard](docs/pr-writing.md#review-and-merge-through-codex).
- Keep next-PR plans and copy-paste handoff prompts in chat only, never in PR
  descriptions. Commit approved plans and lasting decisions, not speculative
  next-task prompts. PRs describe their own change.
- Be very stringent about Markdown and context-file edits: update them only
  when absolutely necessary because the underlying context, behavior, decision,
  or requirement actually differs. Do not make wording-only rewrites or routine
  refreshes when the meaning is unchanged.
- When an update is necessary, refresh affected docs to current state: replace
  superseded rules and remove obsolete, duplicate, or contradictory text. Track
  only facts that affect future work; no per-PR logs in agent instructions.
  Keep rationale in `docs/decisions.md` only when it is not owned elsewhere.
  Every PR includes Knowledge updates with concise linked file-change bullets,
  or "No knowledge changes." Follow `docs/pr-writing.md`.

## Language and naming

Use the project name and established technical identifiers consistently.

Use **ASD-STE100 Simplified Technical English** for repository prose and all
communication with the user. This includes feature names, UI copy, documentation,
PRs, progress updates, explanations, questions, review replies and final answers.
Write for a reader who knows the product's purpose but may not know the code.

- Use short, direct sentences. Limit procedural sentences to 20 words and
  descriptive sentences to 25 words. Give one instruction per sentence.
- Use active voice and name the actor when needed. Use the imperative for
  instructions. State a condition before the action that depends on it.
- Use simple verb forms. Describe current behavior in the present tense.
  Describe completed changes and test results in the past tense.
- Use familiar, concrete words. Use one term for each concept and one meaning
  for each term. Avoid idioms, vague claims and unnecessary technical language.
- Name features after the user's action or outcome. Prefer familiar verbs and
  nouns, such as "Save drafts automatically" or "Compare saved versions."
  Keep names short and specific; avoid vague labels such as "Smart Processing."
- Keep exact code/API identifiers, commands, paths, test names and quoted
  evidence. Explain unfamiliar technical terms when first used. Do not simplify
  wording in a way that changes a technical meaning or a required PR field.
- Keep each paragraph about one subject. Use numbered steps for procedures.
  Use bullets or tables when they make separate items easier to read.
- Lead user messages with the answer, result or current state. Then explain
  what changed, why it matters and how it was checked. Include relevant limits
  and failures. Distinguish proposed work from implemented behavior.
  For maintenance, state the problem without inventing a user benefit.
- Include technical details only when they help the user understand the result
  or make a decision. Keep progress updates and questions short and specific.
- Before sending or committing prose, check sentence length, terms and meaning.
  Apply these rules to new or changed text within scope. Existing names and
  unrelated text need explicit scope for a rename or wording-only cleanup.

## Load context for the task

Core principles above apply to every task. Frontend and backend steering are
the defaults for work in those domains; load both when a change crosses them.
Use this table for additional reading; follow applicable nested instructions.
Ordinary Markdown links are references, not imports. Do not read all docs or
follow every link recursively. Search by topic and read the relevant
section; expand only when a dependency, conflict, or missing fact requires it.

| Task | Read when needed |
| --- | --- |
| Product scope, milestone planning, or conflicting decisions | Current scope and gates in `docs/plan.md`; `docs/decisions.md` only for relevant rationale. Resolve conflicts from explicit user direction; do not guess. |
| Backend/API changes | `docs/backend-steering.md`. |
| Frontend/UI changes | `docs/frontend-steering.md`; the project interface contract and checks linked from `docs/local-validation.md`. |
| Local validation | [docs/local-validation.md](docs/local-validation.md) for setup and project checks. |
| Bend laws, proofs, or generated output | `docs/bend.md`; run `bend guide` before Bend work. Pass proof, generation and regression checks. |
| Opening/updating a PR or reviewing PR feedback | `docs/pr-writing.md` and `.github/pull_request_template.md`. |
| Setup, demos, performance evidence, history, or documentation maintenance | Find the specific document in `docs/README.md`; load only the matching rows. |

## Create and maintain context files

Before creating, splitting, moving, or retiring a context file, read the file
contract and history-review triggers in `docs/README.md`. Create a file when a
distinct reusable scope/audience benefits from separate reading, not per PR.
Give it a purpose, read trigger, authoritative source, owning parent, related
links, and retention mode. Register it in the map and link its parent; update
routes only when needed. Keep one active owner per fact or principle.

At each relevant PR, refresh affected owners and remove resolved/duplicate text.
Preserve core and approved domain principles unless explicitly superseded;
never drop them just because they are old. Keep selected rationale/decision
traces under `docs/history/`, with sources and status, outside default context.
Review matching history on file creation/retirement and decision changes.
Before a major product update, new phase, or roadmap revision, load the history index and retained decision traces.
Read all product topics for broad roadmap work. Read affected topics in full for a focused major update.
Do not repeat this
load for every implementation PR; promote only approved findings into owners.
Application context, fixtures, and generated reports are not repo instructions.

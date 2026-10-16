# Working on {{PROJECT_NAME}}

{{PROJECT_DESCRIPTION}}
Approved scope and the ticket queue live in `docs/plan.md`.

## Always apply

- Keep work within the user's agreed PR scope. The user owns product and design
  decisions. Change software only when requested; proposed scope is not approved
  scope. Keep the solution simple.
- Build on existing architecture before adding parallel implementations. When
  replacing a feature within scope, remove the superseded UI, routes and unused
  code instead of leaving deprecated flows beside the replacement. Preserve
  stored data and supported integrations.
- Use TDD for new behavior: meaningful failing tests, implementation, then
  refactoring. For documentation-only changes, check links and consistency.
- Keep lint, type, build and test checks. Do not weaken a check to make it pass.
- Stop at each PR milestone for feedback before starting the next stage.
  Update usage documentation when an integration changes.
- Before merging, follow the
  [review and merge guard](docs/pr-writing.md#review-and-merge-guard).
- Keep next-PR plans and handoff prompts in chat, never in PR descriptions.
  Commit approved plans and lasting decisions, not speculative prompts.
- Edit Markdown and context files only when the underlying behavior, decision or
  requirement actually differs. No wording-only rewrites or routine refreshes.
- When an update is necessary, rewrite affected docs to current state: replace
  superseded rules and remove obsolete, duplicate or contradictory text. No
  per-PR logs in agent instructions. Every PR includes Knowledge updates with
  linked file-change bullets, or "No knowledge changes." Follow `docs/pr-writing.md`.

## Language and naming

Use plain, concrete language for feature names, UI copy, docs, PRs and chat.
Write for a product-minded reader who may not know the implementation.

- Name features after the user's action or outcome ("Save drafts automatically").
- Reuse established project terms; keep exact code/API identifiers.
- Avoid invented terminology and strings of abstract nouns.
- Lead with what changes and why it matters, then the technical detail needed to
  judge correctness, risk or compatibility.

## Load context for the task

Core rules above apply to every task. Use this table for additional reading.
Links are references, not imports: search by topic and read the relevant section.

| Task | Read when needed |
| --- | --- |
| Scope, milestone planning, or conflicting decisions | `docs/plan.md`; `docs/decisions.md` only for relevant rationale. Resolve conflicts from explicit user direction; do not guess. |
| Backend/API changes | `docs/steering/backend.md`. |
| Frontend/UI changes | `docs/steering/frontend.md`. |
| Opening/updating a PR or reviewing PR feedback | `docs/pr-writing.md` and `.github/pull_request_template.md`. |
| Setup, guides, history, or documentation maintenance | Find the document in `docs/README.md`; load only matching rows. |

## Create and maintain context files

Before creating, splitting, moving or retiring a context file, read the file
contract and history-review triggers in `docs/README.md`. Create a file for a
distinct reusable scope or audience, never per PR. Keep one active owner per
fact. Keep selected decision traces under `docs/history/`, outside default
context. Application data, fixtures and generated reports are not repo instructions.

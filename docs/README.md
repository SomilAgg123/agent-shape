# Context ownership and retention

Use this map when selecting or maintaining repository documentation. Read it
on demand; it is not required context for every task or every turn.

## Default and task context

`AGENTS.md` is the sole repository agent entry point. Runners that support it
load applicable instructions at startup; those instructions may remain in
context across turns. The repo does not require rereading files every turn.
There are no blanket Markdown imports.
Other runners must be configured to use AGENTS.md explicitly if needed.

Core principles in AGENTS.md apply throughout repo work. Frontend/backend
steering is the default for its domain; a cross-domain change loads both.
Specialized context is selected by task. Read relevant sections, not every
document or every linked reference. None of the history or evidence below
is default context. External runner settings can add context. This policy does not measure runtime
loading or token consumption.

Application context, fixtures, and reports are not coding-agent rules.

## What to track and update with each PR

Explanatory comments are banned outside Bend. Existing Bend files/comments,
including installation artifacts and supporting setup/evidence docs, are
preserved at the user's request. Flag a conflict instead of editing those files.
Lint, type, build, and proof checks remain required; a functional tool directive
may use comment syntax. Prefer a configuration equivalent when viable without
weakening checks. API handler docstrings remain required for generated API documentation.

Active documents describe current state. At each PR or relevant change, review
the affected owners below and rewrite changed sections in place. Do not rewrite
unaffected files just to mark a PR transition. Review each edit for a necessary
change in meaning; skip wording-only rewrites when the existing text is correct.

Track only information that changes a future action or interpretation.
This includes approved constraints, relevant rationale, unresolved choices, working setup and necessary evidence.
Do not track routine progress, completed task checklists, review transcripts,
repeated test output, abandoned proposals, or a decision entry for every PR.
Every PR reports actual file changes under Knowledge updates using concise
linked bullets; new files state their purpose/contents. With no changes, say
"No knowledge changes." This report does not require a new knowledge record.
Next-PR plans and handoff prompts stay in chat; approved phase plans belong in
plan.md while they remain current.

When state changes:

1. Find its owner. Replace obsolete wording and remove contradictory or
   duplicated instructions rather than adding a newer entry beneath them.
2. Remove resolved questions/blockers and completed task instructions. Keep a
   short current outcome only when it still affects future work.
3. Preserve core and approved domain principles unless explicit direction supersedes them.
   Age or a one-off exception does not make a principle stale.
   Keep approval distinct from proposals. Remove resolved proposals from active
   guidance, preserving selected rationale in history when useful. Check source
   authority when unclear; do not invent approval.
4. Update affected links/map rows when moving or deleting a file. Confirm no
   current requirement or reproducible evidence was lost during pruning.

Git and PRs preserve exact old versions and complete review discussions.
Preserve only selected decision traces in [history](history/README.md) when
they explain a tradeoff, a rejected approach, or a constraint likely to be
revisited. Do not copy the full chronology or import that collection at startup.

## Creating, splitting, and retiring a context file

A new file is justified by a distinct reusable topic, audience, or reading
trigger: for example, frontend accessibility guidance used for relevant UI
changes. First search the map and matching history for an existing owner.
Extend that owner when its scope still fits. Split when independent topics have
independent read triggers or an owner mixes guidance with historical records;
line count alone is not a reason. Never create one context file per PR.

A new active context file uses this compact contract (omit empty sections):

```markdown
# Specific topic

Purpose: What future action this document supports.
Read when: The task, component, or question that requires it.
Authority: Code/spec or approved guidance source; separate pending proposals.
Parent: The domain/topic document that routes to this file.
Retention: Current state, rewritten when relevant changes occur.

## Current guidance
Only constraints and facts owned here, with brief rationale where necessary.

## Related context
Links labeled by when to follow them; references are not recursive imports.
```

The owning parent is a document, not an invented person or team. An active file
may contain both current facts and principles; link the relevant decision/PR
instead of copying its discussion. Put observed historical records in history
or an evidence owner with their own retention mode, not under Current guidance.

Register the purpose, trigger, and retention in the map below, and link the new
file from its owning parent. Add an AGENTS.md route only for a new broad domain
or an otherwise undiscoverable trigger; specialized pages usually route through
existing parents. Fix inbound links when splitting/moving/retiring files, and
check that every retained fact has one current owner. Retire unused/duplicate
pages after preserving any useful rationale and updating their incoming links.

## History review triggers

| Event | What the agent reads and updates |
| --- | --- |
| Ordinary PR / relevant change | Core and matching domain/task guidance; refresh affected owners only. No routine history scan or progress entry. |
| Create, split, or retire a context file | Search the map and history index for the matching topic; read matching records only, then update ownership and links. |
| Revisit a decision, resolve a conflict, or investigate a regression | Read the relevant current owner and linked source/decision trace. Historical text cannot override approved active guidance. |
| Begin a major product update, enter a new product phase, or revisit the roadmap | Load the history index and decision trace pages into context before proposing scope. Read all retained product topics for a broad roadmap revision; read affected topics in full for a focused major update. Compare prior choices/assumptions with current core/domain principles and scope; an index scan alone is insufficient. |
| Close a major milestone | Reconcile affected decisions and observations, prune duplicates, and propose changes to approved principles for review. Preserve useful sourced traces outside default context. |

These are event-based review rules, not scheduled automation or routine imports.
Loading historical traces for strategic planning does not make them required
reading in every subsequent implementation PR. This trigger concerns decision
traces; it does not require loading every raw report, transcript, or fixture.
A history review can produce no changes. Promote only explicitly approved,
still-relevant conclusions into the owning active file; leave supporting traces
outside normal context. Summarize only meaningful review findings in the PR/chat,
not another chronological log.

## Document owners

Update current owners in place when their meaning changes. Keep one owner per fact.
Preserve Bend artifacts unless the user explicitly authorizes their replacement.

| Document | Read trigger / owned state | Retention |
| --- | --- | --- |
| [Agent instructions](../AGENTS.md) | All repository work: rules and reading routes. | Stable rules, without progress logs. |
| [This map](README.md) | Selecting or maintaining context. | File contract, ownership and retention. |
| [Repository cover](../README.md) | Understanding the harness. | Current introduction. |
| [Quickstart](../QUICKSTART.md) | Adopting the harness in a project. | Working adoption steps. |
| [Configuration](configuration.md) | Changing review paths or the base branch. | Current configuration contract. |
| [Source](source.md) | Understanding the extraction boundary or refreshing the harness. | Source revision and deliberate adaptations. |
| [Plan](plan.md) | Agreeing scope or delivery gates. | Approved scope, current checkpoint and unresolved choices. |
| [Vision](vision.md) | Choosing a product phase. | Direction, with proposals distinguished from approval. |
| [Decisions](decisions.md) | Rationale without another owner. | Current decisions and relevant reasons. |
| [Frontend steering](frontend-steering.md) | UI work. | Approved interaction guidance. |
| [Backend steering](backend-steering.md) | Backend and API work. | Approved backend guidance. |
| [Local validation](local-validation.md) | Setup, tests and project checks. | Reproducible commands and their limits. |
| [Bend](bend.md) | Enabling or maintaining formal checks. | Optional setup, proof boundaries and required checks. |
| [PR writing](pr-writing.md) | Opening, updating or reviewing a PR. | Description, feedback and merge workflow. |
| [PR template](../.github/pull_request_template.md) | Preparing a PR description. | Required and optional fields. |
| [Review criteria](../.github/codex-review.md) | Reviewing code and context. | Judgment required beyond automated checks. |
| [History index](history/README.md) | File lifecycle changes, revisited decisions or major phases. | Selected traces with sources and status. |

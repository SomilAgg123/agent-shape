## Description

Tasks can now be marked complete without affecting other tasks.

## What changed

- Enabled marking a single task complete from the list.

## Knowledge updates

- Updated [plan](docs/plan.md) to remove the completed task-completion ticket.

## Testing

- `test_completing_marks_only_the_chosen_task`: Verified completing one task leaves the others open.

Red: test_completing_marks_only_the_chosen_task failed because complete did not exist.
Green: python -m pytest -q passed.
Refactor: No refactoring was needed.

## Maintenance

Ticket: APP-2
Ticket outcome: complete
Ticket reason: Delivered the agreed completion behavior.
Context disposition: updated
TDD: applied
TDD reason: Added new task behavior.

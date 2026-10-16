# Example: demo-todo

A tiny app showing one full PR loop. `tests/harness/test_examples.py` builds a
throwaway git repo where the base queues `APP-2` in `docs/plan.md` and the head
adds `complete()` and removes the ticket. Then:

- [`pr-bodies/passing.md`](pr-bodies/passing.md) passes the checker.
- [`pr-bodies/failing.md`](pr-bodies/failing.md) is blocked: the plan changed but
  Knowledge updates says "No knowledge changes.", and Red evidence is a placeholder.

`init.py` removes this folder unless `--keep-example` is passed.

# Plan

Purpose: Own approved scope, the ticket queue and review gates.
Read when: Planning scope or milestones, or declaring a PR ticket.
Authority: Explicit user direction. Proposals stay marked as proposed.
Parent: [Context map](README.md).
Retention: Current checkpoint and queue; remove completed sequences.

## Current checkpoint

Describe what exists today and what is approved next.

## Queue

The PR checker reads this heading (`board_heading` in `.github/agent-shape.json`).
Use stable IDs. Remove an item in the PR that completes it; keep it for partial work.

### PR 1 — First approved change

Describe the agreed outcome.

- APP-1: Example list-style ticket

## Gates

- Planning review: the user approves scope before implementation starts.
- Delivery review: stop at each PR milestone for feedback.

# Example Report Contract

## Purpose

Define the evidence and status semantics consumed by downstream reviewers.

## Rules

- Every finding cites a readable source path.
- Missing evidence remains an unresolved gap.
- Status is one of `PASS` or `BLOCKED`.
- Missing required evidence uses `MY_EXTENSION_EVIDENCE_MISSING`.

---
description: "Create a feature specification (preset override)"
scripts:
  sh: scripts/bash/create-new-feature.sh "{ARGS}"
  ps: scripts/powershell/create-new-feature.ps1 "{ARGS}"
---

## User Input

$ARGUMENTS

## Goal

Create one feature specification at the `SPEC_FILE` returned by `{SCRIPT}`.

## Normative Authority

- `templates/spec-template.md` defines the persistent document shape.
- The user input owns feature intent; do not add unstated scope.

## Operating Boundaries

- Run `{SCRIPT}` once to resolve `BRANCH_NAME` and `SPEC_FILE`.
- Read the selected specification template.
- Write only `SPEC_FILE`.
- Stop if the script fails or the feature description is empty.

## Procedure

1. Run `{SCRIPT} --json --short-name "<short-name>" "<description>"`.
2. Read `BRANCH_NAME` and `SPEC_FILE` from the JSON result.
3. Render `templates/spec-template.md` using only supported requirements.
4. Preserve ambiguity as an explicit clarification gap.
5. Validate the required sections and acceptance criteria.

## Validation

- `PASS`: `SPEC_FILE` exists and contains testable acceptance criteria.
- `BLOCKED`: input or path resolution is unavailable.
- Use blocker code `PRESET_SPEC_INPUT_MISSING` for missing feature intent.

## Report

Return mode, branch, changed path, validation status, blockers, and gaps.

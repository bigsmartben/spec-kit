---
description: "Create one review report from the supplied evidence"
---

## User Input

$ARGUMENTS

## Goal

Create exactly one evidence-backed review report at
`.specify/outputs/my-extension/report.md`.

## Normative Authority

- `contracts/example-report-contract.md` defines report semantics.
- `templates/example-report-template.md` defines the persistent shape.
- `config-template.yml` defines supported defaults.
- `validators/config_contract.py` owns config readiness and blocker codes.

## Operating Boundaries

- Read only the paths named in the user input.
- Write only `.specify/outputs/my-extension/report.md`.
- Do not modify source evidence, project configuration, or workflow files.
- If required evidence is missing, report a blocker instead of inventing it.

## Procedure

1. Classify each supplied path as readable evidence or an unresolved gap.
2. Read the contract and template.
3. Populate only claims supported by the readable evidence.
4. Preserve unresolved gaps in the report.
5. Validate the final path, required sections, and evidence references.

## Validation

- `PASS`: the report exists and every finding cites readable evidence.
- `BLOCKED`: required input is absent or unreadable.
- Use blocker code `MY_EXTENSION_EVIDENCE_MISSING` for missing evidence.

## Report

Return:

- mode
- changed paths
- validation status
- blocker codes
- unresolved gaps

---
description: "Override of the myext extension's myextcmd command"
---

## User Input

$ARGUMENTS

## Goal

Create one customized myext report with compliance evidence.

## Normative Authority

- `templates/myext-template.md` defines the report shape.
- The upstream evidence owns facts; this Preset only changes presentation.

## Operating Boundaries

- Read only paths supplied by the user.
- Write only the resolved myext report.
- Do not change the Extension source, configuration, or lifecycle state.

## Procedure

1. Resolve and read the supplied evidence.
2. Render the report from `templates/myext-template.md`.
3. Add compliance findings with source references.
4. Preserve missing evidence as a gap.
5. Validate required report sections.

## Validation

- `PASS`: every compliance finding cites readable evidence.
- `BLOCKED`: required evidence is missing.
- Use blocker code `PRESET_COMPLIANCE_EVIDENCE_MISSING`.

## Report

Return mode, changed paths, validation status, blocker codes, and gaps.

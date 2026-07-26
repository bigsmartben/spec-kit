---
description: Wrap core checklist generation with BDD, NFR, and UI/UX specification readiness gates.
strategy: wrap
---

## Checklist Purpose: "Unit Tests for English"

This wrapper must not redefine core-owned User Input, Pre-Execution Checks, extension hooks, base path resolution, or core file handling.

Checklists validate whether requirements are complete, clear, consistent, measurable, and ready for downstream planning. NOT for verification/testing: do not test implementation behavior, code execution, UI rendering, API responses, or whether the built system works.

CORE PRINCIPLE - Test the Requirements, Not the Implementation. Checklist questions must use requirement-quality forms such as "Are ... specified?", "Is ... quantified?", "Can ... be objectively verified?", or "Are ... requirements consistent?"

Use `$ARGUMENTS` as checklist intent. Generate dynamic clarifying questions with no pre-baked catalog only when the answer changes BDD, NFR, or UI/UX specification checklist content. Use Q1/Q2/Q3 for initial questions and Q4/Q5 only for justified follow-up gaps.

For `checklists/behavior-testability.md`, create the file when absent; otherwise append or update without deleting existing checklist content. Resolve `behavior-testability-checklist-template` through the normal template stack and treat it as the only stable authority for checklist headings, item wording, matrices, columns, and status enums. Do not reproduce those structures in this command.

## Readiness Gate Behavior

Populate the resolved checklist template directly from `spec.md`. The checklist is the plan-entry quality gate and must not depend on behavior drafts or implementation artifacts.

Evaluate:

- observable and independently testable user-story behavior;
- primary, alternate, exception, boundary, permission, validation, and state-conflict coverage when applicable;
- explicit Given starting conditions, When triggers, and Then outcomes;
- product-level non-functional requirement applicability and verifiability;
- UI/UX requirement applicability, observable acceptance criteria, required states, responsive behavior, accessibility, content, and visual hierarchy.

For UI/UX rows, keep requirement applicability (`Required | Not Applicable | Unknown`) separate from specification readiness (`Ready | Blocked`). Use the stable `UI-###` or `UX-###` requirement ID from `spec.md`. `Unknown` applicability and incomplete Required requirements must appear in Blocking Items when they prevent downstream planning.

Set `Gate Status: PASS` only when every applicable readiness item is checked and `Blocking Items: none`. Otherwise set `Gate Status: BLOCKED` and list each requirement-quality gap that prevents behavior projection or planning.

Unchecked readiness items that prevent downstream planning return to `/speckit.clarify` or `/speckit.specify`. Do not repair requirements inside the checklist command and do not proceed to `/speckit.plan`.

{CORE_TEMPLATE}

## Behavior Checklist Reporting

Before finishing, report the full checklist path, item count, update mode, focus areas, depth level, actor/timing, must-have items, BDD/NFR/UI/UX readiness status, Gate Status, and Blocking Items.

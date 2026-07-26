---
description: Wrap core clarification with spec-only ambiguity resolution.
strategy: wrap
---

## Spec-Only Clarification Policy

This wrapper must not redefine core-owned User Input, Pre-Execution Checks, extension hooks, base path resolution, or core file handling.

Use `spec.md` as the clarification source. Ask and record clarification only for requirement ambiguity that affects product behavior, constraints, non-functional requirement assumptions, UI/UX applicability, acceptance criteria, user roles, permissions, entity states, data semantics, exceptions, validation rules, or boundaries.

Do not read or update behavior draft artifacts. Product requirements stay in `spec.md`; update `spec.md` only after user-provided answers make the requirement clear.

## Wrapper Input Additions

Treat `$ARGUMENTS` as prioritization context for the current clarification run. Do not ask the user to restate requirements already present in `spec.md`.

## Wrapper Preflight Additions

Load the active `spec.md` through the core command. Official hooks still apply: `hooks.before_clarify` runs before Outline, `hooks.after_clarify` runs before Completion Report, and mandatory hooks emit `EXECUTE_COMMAND`. If `spec.md` is missing, follow the core command error path and do not create a new spec here.

## Wrapper Outline Additions

### UI/UX Requirement Clarification Strategy

Scan `spec.md` first for `[NEEDS CLARIFICATION]`, UI/UX Applicability `Unknown`, and incomplete `UI-###` or `UX-###` requirements.

Ask at most 5 high-impact questions whose answers materially affect requirements, implementation planning, or validation readiness. Present exactly one question at a time and do not reveal future queued questions.

Format recommendations as `**Recommended:** Option [X] - <brief rationale>` when a discrete 2-5 option choice is available. For short-answer gaps, use `Suggested` and constrain answers to `<=5 words`. Accept `yes`, `recommended`, or `suggested` as approval of the shown recommendation.

Prioritize questions in this order:

1. UI/UX applicability: Required, Not Applicable, or Unknown.
2. Target users, experience goals, and critical journeys.
3. Information architecture, navigation, and recovery paths.
4. Required default, loading, empty, error, disabled, success, hover, and focus states.
5. Interaction feedback, validation behavior, and error semantics.
6. Responsive reflow, scrolling, safe areas, viewport support, and long-content handling.
7. Keyboard, focus, semantics, contrast, announcements, and other accessibility behavior.
8. Required copy, visual hierarchy, iconography, imagery, and numeric or date formatting.
9. Objective UI/UX acceptance criteria.

After each accepted answer, write confirmed answers back into the relevant `spec.md` requirement, scenario, acceptance criterion, assumption, or UI/UX section. Update Applicability when the answer resolves an `Unknown` decision. Ensure `## Clarifications`, `### Session YYYY-MM-DD`, and one `- Q: ... -> A: ...` bullet exist for the session. Save `spec.md` after each accepted answer.

Do not generate checklist artifacts. `/speckit.checklist` remains responsible for checking requirement text quality and readiness.

## Validation after each write

Run validation after each write plus a final pass. Confirm the accepted answer appears once in `spec.md`, no more than 5 questions were asked, the targeted ambiguity is removed or replaced, no contradictory earlier statement remains, and heading structure is preserved.

Do not update checklist artifacts. Report checklist impact as unresolved readiness context for `/speckit.checklist`.

{CORE_TEMPLATE}

## Completion Report

Before finishing, report answered questions, `spec.md` sections updated, and any unresolved requirement ambiguity that still blocks checklist readiness.

## Done When

- [ ] No more than 5 high-impact questions were asked.
- [ ] Each accepted answer was written back to `spec.md`.
- [ ] Any answered UI/UX applicability decision was updated in `spec.md`.
- [ ] Validation after each write found no duplicate or contradictory clarification.
- [ ] Completion reported sections touched and remaining blockers.

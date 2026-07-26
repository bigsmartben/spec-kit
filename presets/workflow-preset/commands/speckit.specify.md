---
description: Wrap core specification with spec-only requirement ownership.
strategy: wrap
---

Follow cross-agent protocol profile: `speckit.specify.single_core`.

## Spec-Only Requirement Policy

This wrapper must not redefine core-owned User Input, Pre-Execution Checks, extension hooks, base path resolution, or core file handling.

Preset-added requirement output writes only `spec.md`. Product requirements stay in `spec.md`: user stories, acceptance criteria, functional requirements, non-functional requirements, UI/UX requirements, constraints, assumptions, and clarification markers required by the active template.

Keep requirement text implementation-agnostic and scoped to product behavior. Focus on WHAT users need and WHY; avoid HOW to implement it.

## Wrapper Input Additions

Treat explicit user-provided product text, notes, and confirmed decisions as the feature description. If the core feature description is empty, follow the core command error path.

## Wrapper Preflight Additions

Resolve the active `spec-template` through the normal preset/template stack. Use its UI/UX section as the only stable UI/UX output structure; do not reproduce the template's headings, table columns, status enums, or examples inside this command.

## Wrapper Outline Additions

Determine whether the feature has a user-facing surface or interaction journey:

- `Required`: populate every applicable UI/UX field defined by the active template.
- `Not Applicable`: record a concrete product-level rationale in `spec.md`.
- `Unknown`: record the unresolved product decision with `[NEEDS CLARIFICATION]`.

Write only confirmed product requirements. Assign stable `UX-###` IDs to journey, navigation, feedback, and usability requirements, and stable `UI-###` IDs to surface, state, responsive, accessibility, content, and observable visual requirements.

Requirements must describe observable user outcomes. Do not invent framework components, DOM structure, CSS selectors, component props, code organization, asset packaging, or other implementation decisions.

Limit `[NEEDS CLARIFICATION]` markers to the highest-impact unresolved product decisions. Record reasonable low-impact defaults in Assumptions.

## Specification Quality Validation

Validate that the completed requirement text is stakeholder-readable, testable, implementation-agnostic, and explicit about applicability, assumptions, UI states, responsive behavior, accessibility, content, acceptance criteria, and unresolved product decisions.

{CORE_TEMPLATE}

## Completion Report

Before finishing, report the `spec.md` sections created or updated, confirmed requirements, UI/UX applicability, and unresolved requirement ambiguities.

## Done When

- [ ] The active spec template supplied the stable UI/UX artifact shape.
- [ ] Functional, non-functional, and UI/UX requirement coverage is present or explicitly marked Not Applicable or Unknown.
- [ ] Applicable UI/UX requirements have stable `UI-###` or `UX-###` IDs and observable acceptance criteria.
- [ ] Product `[NEEDS CLARIFICATION]` markers are limited to high-impact unresolved decisions.
- [ ] Completion reported updated `spec.md` sections and remaining ambiguities.

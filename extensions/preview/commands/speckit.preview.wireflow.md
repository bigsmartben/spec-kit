---
description: Generate one fidelity-specific HTML design artifact from spec.md and uc.md inputs. First argument must be low, mid, or high.
---

## User Input

```text
$ARGUMENTS
```

## Fidelity Parameter

You **MUST** parse `$ARGUMENTS` before loading or writing preview output.

The first token is required and must be exactly one of `low|mid|high`:

- `low`: convert inputs into a low-fidelity design artifact with actor intent, core journey, major nodes, branch points, and delivery-relevant gaps.
- `mid`: convert inputs into a mid-fidelity design artifact with source-defined pages, fields, controls, layout relationships, state inventory, and delivery-relevant gaps.
- `high`: convert inputs into a high-fidelity design artifact with documented interactions, observable state transitions, validation feedback, permissions, responsive states, and delivery-relevant gaps.

If the first token is missing or is not exactly `low`, `mid`, or `high`, stop and do not write output. Report this usage:

```text
/speckit.preview.wireflow <low|mid|high> [design focus]
```

Treat all remaining tokens as optional design focus, audience, device, flow, interaction, or output constraint. If `$ARGUMENTS` requests a page, role, device, state, interaction, validation rule, permission, or business rule that is not supported by the loaded artifacts, do not invent it. Mark it as `输入未说明`, or use `推理补齐` only when a minimal traceable inference is required to preserve design artifact coherence.

## Goal

Generate or update `specs/<feature>/preview/wireflow.html`.

The only goal is to synthesize `spec.md`, `uc.md`, and supporting feature inputs into a high-quality self-contained HTML design artifact that matches the required fidelity parameter. Evidence, provenance, and coverage conclusions are quality controls for the design artifact; they are not separate deliverables.

## Command Responsibilities

- Resolve the active feature and load source artifacts.
- Validate the required fidelity parameter before writing output.
- Apply evidence policy, Input-to-Design Synthesis Pass, and fidelity-specific Design Artifact Policy.
- Load the output template from `.specify/extensions/preview/templates/preview/wireflow.html`; when running from this extension repository, use `templates/preview/wireflow.html`.
- Populate template slots with source-grounded design content only.
- Write only `specs/<feature>/preview/wireflow.html`. Create `specs/<feature>/preview/` if it is missing; do not create any other files or directories.

Do not redefine template sections, table columns, CSS shell, JavaScript hook names, or output structure in this command. The template is the source of truth for HTML shape and required tables.

## Boundaries

- Do not modify source code, tests, app assets, package manifests, build configuration, feature specs, plans, tasks, or memory files.
- Do not create Markdown, Figma files, images, screenshots, or production UI.
- Do not invent business rules, roles, fields, states, copy, data rules, or interactions. Mark unsupported items as `输入未说明`; mark only minimal traceable inferences as `推理补齐`.
- HTML output must be self-contained and network-free. Use embedded CSS only and inline JavaScript only for documented interactions, fidelity gating, disclosure controls, and state changes.
- If an interaction is not documented or minimally inferable from source evidence, record it as an open design question instead of making it clickable.
- Do not claim that HTML is production-ready.
- If the template file cannot be read, stop with an error explaining that the preview extension template is missing.

## Context Loading

1. Verify the current directory is a Spec Kit project by checking for `.specify/`.
2. Identify the active feature:
   - Prefer `SPECIFY_FEATURE` when set.
   - Otherwise use the current Git branch name when it exactly matches a directory under `specs/`.
   - Otherwise inspect `specs/` and use it only when there is exactly one unambiguous candidate directory.
   - Do not choose by most recent timestamp when multiple feature directories exist.
   - If the feature cannot be identified, stop and ask the user to set `SPECIFY_FEATURE` or run from the feature branch.
3. Read these files:
   - `specs/<feature>/spec.md` (required)
   - `specs/<feature>/uc.md` (required)
   - `specs/<feature>/plan.md` (supporting, when present)
   - `specs/<feature>/research.md` (supporting, when present)
   - `specs/<feature>/data-model.md` (supporting, when present)
   - `specs/<feature>/contracts/` (supporting, when present)
   - `specs/<feature>/quickstart.md` (supporting, when present)
   - `intake/**/structured-ir.yaml` (supporting for `mid`, when present)
   - `intake/**/ir-assertions.yaml` (supporting for `mid`, when present)
   - `intake/**/ir-evidence-packet.md` (supporting for `mid`, when present)
4. Read `.specify/memory/constitution.md` if present.
5. If `spec.md` is missing, stop with an error explaining that `/speckit.specify` must run first.
6. If `uc.md` is missing, stop with an error explaining that this preview command requires use-case input before design synthesis.
7. If `specs/<feature>/preview/wireflow.html` already exists, read it before writing. Preserve user-authored design notes, decisions, and unresolved design questions when they remain consistent with current source artifacts; label changed items as `UPDATED` and superseded items as `SUPERSEDED`.

## Source Priority

Use `spec.md` and `uc.md` as the primary design inputs.

Supporting files may refine design synthesis only in these ways:

- `plan.md`: architecture context, platform constraints, and implementation boundaries that affect design feasibility.
- `research.md`: source-backed product, user, accessibility, or technical decisions that affect design choices.
- `data-model.md`: entity names, fields, states, relationships, and lifecycle constraints.
- `contracts/`: request/response fields, error states, validation rules, and permission boundaries.
- `quickstart.md`: user-visible setup, workflow, or operational assumptions.
- `intake/**/structured-ir.yaml`, `intake/**/ir-assertions.yaml`, and `intake/**/ir-evidence-packet.md`: optional `mid` fidelity support when they can be mapped to `schemas/preview/mid-ir-adapter.schema.json`.
- `.specify/memory/constitution.md`: project principles that constrain design output.

When a supporting file conflicts with `spec.md` or `uc.md`, do not let it override the primary inputs. Record the conflict as a design question or delivery quality issue.

## Evidence Policy

Use these coverage labels exactly: `已覆盖`, `部分覆盖`, `未覆盖`, `输入未说明`, `推理补齐`.

Use evidence to keep the design artifact grounded in the loaded inputs. Evidence and coverage labels support design quality, gap visibility, and handoff confidence; they must not become the primary output.

Every requirement, use case, acceptance scenario, screen, node, field, interaction, state, branch, permission, validation rule, and system response included in the generated artifact must include a coverage label and provenance. Provenance must be either a source anchor or a `推理补齐` explanation.

Use `输入未说明` when no source supports a requested item. Use `推理补齐` only when a minimal inference connects two supported facts; include the reasoning bridge and keep it non-authoritative.

## Input-to-Design Synthesis Pass

Before composing the design artifact, translate the loaded inputs into design decisions for the selected fidelity. The pass exists to improve the completeness, usefulness, and handoff quality of the HTML design artifact. The optional design focus changes ordering, emphasis, and first-screen selection only; it must not hide source-backed flows, constraints, states, or gaps that affect design delivery quality.

### spec.md Design Inputs

Extract every source-backed item from `specs/<feature>/spec.md` when present:

- feature goal, scope, user roles, and constraints
- every user story, priority, persona, and independent test
- every acceptance scenario, Given/When/Then block, edge case, and exception path
- every functional requirement, data requirement, validation rule, permission, and user-visible system response
- every non-functional requirement, success criterion, platform/device constraint, accessibility constraint, localization constraint, and compliance note
- every source-defined entity, field, relationship, status, lifecycle state, and external dependency

Each extracted item must be considered during design composition. Group related items when they map to the same screen, state, interaction, or design decision, but do not silently drop unsupported, conflicting, or delivery-relevant items. Surface those items in `spec.md` design input mapping, the delivery quality conclusion, a design node/control/state, or a design question.

### uc.md Design Inputs

Extract every source-backed item from `specs/<feature>/uc.md` when present:

- every use case ID, use case name, actor, supporting actor, trigger, and goal
- every precondition, postcondition, main success flow step, alternate flow, exception flow, cancellation path, and retry path
- every business rule, permission rule, validation rule, data condition, error condition, and user-visible feedback requirement
- every included or extended use case relationship

Each extracted item must be considered during design composition. Group related items when they map to the same flow, branch, state, interaction, or design decision, but do not silently drop unsupported, conflicting, or delivery-relevant items. Surface those items in `uc.md` design input mapping, the delivery quality conclusion, a design node/control/state, or a design question.

## Design Artifact Policy

Apply this policy after the Input-to-Design Synthesis Pass:

- `low` MUST include: a core journey map, actor intent and trigger, abstract node list, major branch points, outcome summary, delivery-relevant gaps, and unresolved design questions. Do not add source-undefined page chrome, fields, visual styling, or interactions.
- `mid` MUST include: screen or node inventory, layout regions, visible controls, source-defined fields, representative empty/loading/success/error states, branch handling, delivery-relevant gaps, and unresolved design questions. Only include labels, fields, buttons, and states supported by source evidence or marked as `推理补齐`.
- `high` MUST include: primary interactive surface, documented control behavior, interaction matrix, state transition matrix, validation and permission feedback, responsive mobile and desktop notes, delivery-relevant gaps, and unresolved design questions. Simulate only documented interactions.

For all fidelity levels, preserve unsupported requested focus items as design questions instead of omitting them.

## Procedure

1. Parse the required fidelity parameter and optional design focus from `$ARGUMENTS`.
2. Summarize the feature goal, personas, use cases, primary scenarios, constraints, and source availability from loaded artifacts.
3. Run the Input-to-Design Synthesis Pass for `spec.md` and `uc.md`.
4. Extract source-grounded pages, tasks, fields, controls, roles, permissions, data conditions, states, decisions, and system responses according to the selected fidelity.
5. Fill the HTML template slots for metadata, fidelity, input sources, evidence summary, design surface, wireflow, node inventory, interaction matrix, state matrix, branch handling, `spec.md` design input mapping, `uc.md` design input mapping, delivery quality conclusion, preserved design records, and unresolved design questions.
6. Escape user-provided content and source excerpts before inserting them into HTML.
7. Write `specs/<feature>/preview/wireflow.html`, preserving existing design content as described above.
8. Report output path, fidelity, input sources, design synthesis summary for `spec.md` and `uc.md`, flows represented, interactions represented, inferred assumptions, unsupported items, and unresolved design questions.

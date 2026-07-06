# Spec Kit Preview Extension

Generate one fidelity-specific HTML design artifact from `spec.md` and `uc.md` inputs. The command requires a `low`, `mid`, or `high` fidelity parameter.

## Overview

This extension turns Spec Kit requirements and use-case inputs into a design artifact between specification and implementation. Its only goal is to help teams produce the right design artifact for the selected fidelity: product flows, page/state structure, layout assumptions, UI states, interaction details, handoff notes, and delivery-relevant design gaps before production code is planned or built.

The command acts as an execution orchestrator: it resolves the active feature, loads `spec.md`, `uc.md`, and supporting Spec Kit artifacts, applies input-to-design synthesis policy, and fills the fixed HTML template under `templates/preview/`. Evidence and coverage labels support output quality; they are not separate deliverables. The template is the source of truth for output sections, table schemas, HTML shell, and preserved design-note slots. Structural validation is driven by `schemas/preview/contract.json`, validated against `schemas/preview/contract.schema.json`.

Generated previews are intentionally standalone:

- one HTML file
- inline CSS
- JavaScript only for documented interactions and template controls
- no network dependencies
- no build step
- no production source changes

## Command

| Command | Description |
|---------|-------------|
| `speckit.preview.wireflow` | Generate `specs/<feature>/preview/wireflow.html`; first argument must be `low`, `mid`, or `high` |

## Usage

```text
/speckit.preview.wireflow low
/speckit.preview.wireflow mid admin dashboard empty and error states
/speckit.preview.wireflow high checkout confirmation flow, desktop first
```

The first argument is mandatory:

- `low`: low-fidelity design artifact with actor intent, core journey, major nodes, branch points, and delivery-relevant gaps.
- `mid`: mid-fidelity design artifact with source-defined pages, fields, controls, layout relationships, state inventory, and delivery-relevant gaps.
- `high`: high-fidelity design artifact with documented interactions, observable state transitions, validation feedback, permissions, responsive states, and delivery-relevant gaps.

Any text after the fidelity parameter is treated as optional design focus. Focus changes ordering and emphasis, but it must not hide `spec.md` or `uc.md` flows, constraints, states, or gaps that affect delivery quality.

## Fidelity Outputs

- `low` must include a core journey map, actor intent and trigger, abstract node list, major branch points, outcome summary, delivery-relevant gaps, and unresolved design questions.
- `mid` must include a screen or node inventory, layout regions, visible controls, source-defined fields, representative empty/loading/success/error states, branch handling, delivery-relevant gaps, and unresolved design questions.
- `high` must include a primary interactive surface, documented control behavior, interaction matrix, state transition matrix, validation and permission feedback, responsive mobile and desktop notes, delivery-relevant gaps, and unresolved design questions.

## Inputs

The command reads the active feature under `specs/<feature>/`:

- `spec.md` (required)
- `uc.md` (required)
- `plan.md` (optional)
- `research.md` (optional)
- `data-model.md` (optional)
- `contracts/` (optional)
- `quickstart.md` (optional)

For `mid` fidelity, the command can also use optional structured intake artifacts as supporting evidence:

- `intake/**/structured-ir.yaml`
- `intake/**/ir-assertions.yaml`
- `intake/**/ir-evidence-packet.md`

These files are not required. When they can be mapped to `schemas/preview/mid-ir-adapter.schema.json`, the design artifact can use the mapped pages, regions, fields, controls, states, relations, assertions, and provenance as source-grounded design inputs. When they are missing or cannot be mapped, design synthesis continues from `spec.md`, `uc.md`, and other supporting feature artifacts, and the limitation is recorded as a design question or delivery quality issue.

It also reads `.specify/memory/constitution.md` when present.

## Output

```text
specs/<feature>/preview/wireflow.html
```

The HTML file can be opened directly in a browser.

## Input-To-Design Synthesis

The command must run an Input-to-Design Synthesis Pass before composing the design artifact. This pass exists to improve the completeness, usefulness, and handoff quality of the delivered HTML design artifact:

- `spec.md` inputs: user stories, acceptance scenarios, functional requirements, edge cases, constraints, success criteria, entities, data conditions, permissions, validation rules, and user-visible system responses must be considered and represented in the delivered design through screens, states, interactions, quality conclusions, or design questions.
- `uc.md` inputs: use cases, actors, triggers, preconditions, main flows, alternate flows, exception flows, postconditions, business rules, data conditions, error conditions, and feedback requirements must be considered and represented in the delivered design through flows, states, interactions, quality conclusions, or design questions.
- If `uc.md` is missing, the command stops before writing output because use-case input is required for high-quality design synthesis.

Supporting files such as `plan.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`, structured intake artifacts, and `.specify/memory/constitution.md` may refine the design artifact, but they do not override `spec.md` or `uc.md`. Conflicts become design questions or delivery quality issues.

## Boundaries

This extension does not modify app source code, tests, build files, specs, plans, or tasks. The preview is not production implementation and should not replace `/speckit.plan`, `/speckit.tasks`, or `/speckit.implement`.

## Installation

Install from the v1.3.0 release ZIP:

```bash
specify extension add preview --from https://github.com/bigsmartben/spec-kit-preview/archive/refs/tags/v1.3.0.zip
```

For local development from this repository root:

```bash
specify extension add --dev .
```

## Files Written

When the command runs in a Spec Kit project, it writes only:

```text
specs/<feature>/preview/wireflow.html
```

Installing the extension copies this repository into:

```text
.specify/extensions/preview/
```

## Template Source

Command prompts load one output template:

```text
templates/preview/wireflow.html
```

The command layer owns invocation, fidelity parameter validation, context loading, evidence policy, input-to-design synthesis, and file-write boundaries. The template layer owns sections, required tables, HTML structure, and the preserved design records slot.

## Validation Contract

Repository validation uses a schema-backed JSON contract:

```text
schemas/preview/contract.schema.json
schemas/preview/contract.json
schemas/preview/mid-ir-adapter.schema.json
```

`tests/validate-extension.py` validates the contract shape with a standard-library JSON Schema subset, then uses the contract to verify manifest command mappings, declared schema files, command/template files, required slots, forbidden legacy phrases, and documentation alignment.

`schemas/preview/mid-ir-adapter.schema.json` is a preview-owned ingest boundary for optional mid-fidelity structured intake. It validates whether a mapped payload has enough source-backed pages, regions, fields, controls, states, relations, assertions, coverage labels, and provenance to support the `mid` design artifact. It is not the authoritative schema for upstream `spec-kit-intake` IR.

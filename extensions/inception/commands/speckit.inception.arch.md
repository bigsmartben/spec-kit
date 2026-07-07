---
description: Derive inception architecture artifacts from product UC and confirmed API POC evidence.
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding when it is not empty.

## Goal

Guide a conversational architecture inception workflow from the product UC to these artifacts:

```text
inception/arch/api-capability.md
inception/arch/api-poc.md
inception/arch/system-boundary.md
inception/arch/domain-model.md
inception/arch/arch.md
inception/arch/api-poc-runs/
```

This command answers:

- How do all architecture inception artifacts roll up into complete architecture pre-design: capabilities, boundaries, domain-model constraints, security, error handling, NFRs, architecture decisions, risks, and constraints for `plan.md`?
- Which system capabilities are required by the confirmed UC?
- Which technical options are viable for each high-value or high-risk capability?
- Which option is recommended, which option is retained as backup, and which options are rejected?
- Which capabilities need real POC validation?
- Where are the client, server, data, permission, and third-party boundaries?
- What domain concepts and invariants constrain later formal planning?
- What did real POC code prove, fail to prove, or constrain?

It does not create formal API contracts, implementation plans, tasks, production code, or test-suite changes.
It is not an implementation plan; it is architecture input for later formal planning.

## Formal Input

The only formal input is:

```text
inception/product/uc.md
```

If it is missing, stop and ask the user to run `/speckit.inception.product` or provide the UC.

You may read existing files under `inception/arch/` only as refresh baselines. These existing files do not outrank the current UC.

Forbidden sources as architecture evidence:

```text
inception/product/wireflow-medium.html
inception/product/wireflow-high.html
spec.md
plan.md
tasks.md
contracts/
OpenAPI files
database schemas
application source code
tests
```

If a forbidden source is used as evidence, stop with blocker `SOURCE_PRIORITY_VIOLATION`.

## Templates

Template structure is authoritative. Load these templates before writing output:

```text
.specify/extensions/inception/templates/arch/api-capability-template.md
.specify/extensions/inception/templates/arch/api-poc-template.md
.specify/extensions/inception/templates/arch/system-boundary-template.md
.specify/extensions/inception/templates/arch/domain-model-template.md
.specify/extensions/inception/templates/arch/arch-template.md
```

When running from the extension repository, use:

```text
templates/arch/api-capability-template.md
templates/arch/api-poc-template.md
templates/arch/system-boundary-template.md
templates/arch/domain-model-template.md
templates/arch/arch-template.md
```

Do not invent output sections, table columns, POC evidence fields, or quality gates outside the templates. If a template is missing, stop with blocker `TEMPLATE_BYPASS`.

## Conversation Workflow

Before writing architecture artifacts, confirm:

1. UC scope and product boundaries from `inception/product/uc.md`.
2. Capability inventory and each capability's UC source.
3. Risk level for each capability.
4. Candidate technical options for each high-value or high-risk capability.
5. Technical option fit, complexity, dependency risk, performance/security/cost impact, team familiarity, maintainability, and POC necessity.
6. Recommended option, backup option, rejected options, and tradeoff rationale for each high-value or high-risk capability.
7. Which capabilities require real POC code.
8. System boundaries and non-goals.
9. Domain-model facts to record in `domain-model.md`, including objects, state transitions, invariants, and open questions. For `arch.md`, reference only the domain-model constraints that affect architecture decisions.

If a needed architecture conclusion is not supported by UC or confirmed POC evidence, record it as an open question instead of writing it as fact.

## API POC Workflow

`api-poc.md` is not pseudocode. It records real code execution evidence.

Before running any POC code, you **MUST** confirm the preparation packet with the user:

```text
target capability
validation hypothesis
runtime environment
dependencies
credential/config needs
sample input
external service access
allowed side effects
stop conditions
```

If this confirmation is missing, stop with blocker `POC_CONFIRMATION_MISSING`.

After confirmation:

- Create POC assets only under `inception/arch/api-poc-runs/<capability-slug>/`.
- Keep POC code disposable and explicitly labeled as validation-only.
- Run the POC code when the confirmed environment allows it.
- Capture the exact command, environment summary, input, output, failure details, conclusion, and formal-iteration constraints in `api-poc.md`.

POC code must not modify:

```text
application source
production configuration
database migrations
formal API contract
OpenAPI files
SDKs
test suites
build configuration
deployment files
```

If `api-poc.md` lacks real run command/output/result evidence for a completed POC, stop with blocker `POC_RUN_EVIDENCE_MISSING`.

## Operating Boundaries

Write only:

```text
inception/arch/api-capability.md
inception/arch/api-poc.md
inception/arch/system-boundary.md
inception/arch/domain-model.md
inception/arch/arch.md
inception/arch/api-poc-runs/<capability-slug>/
```

Do not create or modify:

```text
spec.md
plan.md
tasks.md
api-contract
openapi.yaml
database schema
application source code outside `inception/arch/api-poc-runs/`
tests
build configuration
production assets
```

If any output path falls outside `inception/arch/`, stop with blocker `OUTPUT_PATH_MISMATCH`.

## Procedure

1. Load `inception/product/uc.md`.
2. Load architecture templates.
3. Run the conversation workflow and confirm architecture scope.
4. Extract system capabilities from `uc.md`.
5. Compare technical candidates for high-value or high-risk capabilities in `api-capability.md`.
6. Record recommended, backup, and rejected options with tradeoff rationale.
7. Confirm POC preparation packets for high-risk capabilities.
8. Run confirmed POC code under `api-poc-runs/<capability-slug>/` when approved and feasible.
9. Render `api-poc.md` from real POC evidence.
10. Render `system-boundary.md`, `domain-model.md`, and `arch.md`.
11. Re-check every rendered artifact against the quality gates.
12. Report written paths, POC run directories, exact run commands, blockers, risks, and open questions.

`arch.md` must not include a mock strategy section. Mock handling, fixtures, sandboxing, or test doubles belong to later formal planning/task artifacts or to separate boundary notes, not to the primary architecture inception artifact.
`arch.md` must not include a standalone state model section. State enumerations, transitions, domain rules, and business invariants belong in `domain-model.md`; `arch.md` may reference only the key domain-model constraints needed for architecture decisions.

## Quality Gates

- `OUTPUT_PATH_MISMATCH`: a write target is outside `inception/arch/`.
- `SOURCE_PRIORITY_VIOLATION`: a forbidden source was used as evidence.
- `POC_CONFIRMATION_MISSING`: POC code would run before the user confirms the preparation packet.
- `POC_RUN_EVIDENCE_MISSING`: `api-poc.md` lacks real command, output, or result evidence for a completed POC.
- `SCOPE_LEAK`: output includes formal spec, plan, task, API contract, OpenAPI, database schema, application implementation, or test-suite changes.
- `UNSUPPORTED_INFERENCE`: an unconfirmed item is written as fact.
- `TECH_SELECTION_MISSING`: a high-value or high-risk capability lacks candidate technical options, a recommended option, or tradeoff rationale.
- `EMPTY_PRIMARY_ARTIFACT`: `arch.md` lacks overview, UC context, capability architecture, boundaries, domain model, decisions, risks, or handoff constraints.
- `TEMPLATE_BYPASS`: templates were not loaded or the output structure bypasses them.

If any blocker is present, report the blocker code and do not claim the inception architecture artifacts are ready.

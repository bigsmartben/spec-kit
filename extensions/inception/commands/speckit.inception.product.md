---
description: Converge product intent into inception product UC and wireflow artifacts.
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding when it is not empty.

## Goal

Guide a conversational product inception workflow and write only these artifacts:

```text
inception/product/uc.md
inception/product/wireflow-medium.html
inception/product/wireflow-high.html
```

This command answers:

- Who is the user?
- What goal are they trying to complete?
- What is the product boundary for this inception round?
- How does the user journey flow at medium and high fidelity?

It does not create formal Spec Kit feature artifacts.

## Templates

Template structure is authoritative. Load these templates before writing output:

```text
.specify/extensions/inception/templates/product/uc-template.md
.specify/extensions/inception/templates/product/wireflow-medium-template.html
.specify/extensions/inception/templates/product/wireflow-high-template.html
```

When running from the extension repository, use:

```text
templates/product/uc-template.md
templates/product/wireflow-medium-template.html
templates/product/wireflow-high-template.html
```

Do not invent output sections, table columns, HTML structure, or quality gates outside the templates. If a template is missing, stop with blocker `TEMPLATE_BYPASS`.

## Conversation Workflow

Proceed through these confirmation points before writing:

1. Confirm the product idea, target users, and primary job-to-be-done.
2. Confirm business assumptions and success criteria.
3. Confirm core user scenarios, alternate paths, exception paths, and permission boundaries.
4. Confirm out-of-scope items for this inception round.
5. Confirm unresolved questions and mark them as `[NEEDS CLARIFICATION]`.

If any confirmation is missing and the artifact would otherwise turn an assumption into fact, stop with blocker `UNSUPPORTED_INFERENCE`.

## Context Loading

1. Verify the current directory is a Spec Kit project by checking for `.specify/`.
2. Read user-provided product input from `$ARGUMENTS`.
3. Read existing `inception/product/uc.md` only when refreshing prior product inception work.
4. Read existing `inception/product/wireflow-medium.html` and `inception/product/wireflow-high.html` only to preserve still-valid design notes and open questions.

Forbidden sources:

```text
spec.md
plan.md
tasks.md
inception/arch/
docs/technical/
contracts/
OpenAPI files
database schemas
source code
tests
```

If a forbidden source is used as evidence, stop with blocker `SOURCE_PRIORITY_VIOLATION`.

## Product Artifact Rules

- `uc.md` is the primary product fact artifact.
- `wireflow-medium.html` and `wireflow-high.html` are derived from `uc.md`.
- Wireflow artifacts must not add new product facts, new business rules, new permissions, or new validation rules that are absent from `uc.md`.
- Unsupported requested items must be recorded as open questions, not silently invented.
- Use stable evidence labels: `confirmed`, `needs-clarification`, `derived-from-uc`, `unsupported`.

`wireflow-high.html` must cover these UI states when relevant to the confirmed UC:

```text
loading
success
empty
error
disabled
permission denied
submitting
submitted
```

## Operating Boundaries

Write only the three product inception paths listed in Goal.

Do not create or modify:

```text
spec.md
arch.md
plan.md
tasks.md
api-contract
openapi.yaml
database schema
domain model
source code
tests
build configuration
production assets
```

If any output path falls outside `inception/product/`, stop with blocker `OUTPUT_PATH_MISMATCH`.

## Procedure

1. Load the product templates.
2. Run the conversation workflow and resolve missing confirmations.
3. Render `inception/product/uc.md` first.
4. Derive `inception/product/wireflow-medium.html` from `uc.md`.
5. Derive `inception/product/wireflow-high.html` from `uc.md`.
6. Re-check every rendered artifact against the quality gates.
7. Report written paths, confirmed product facts, derived wireflow coverage, unsupported requests, and open questions.

## Quality Gates

- `OUTPUT_PATH_MISMATCH`: a write target is outside `inception/product/`.
- `SOURCE_PRIORITY_VIOLATION`: a forbidden source was used as evidence.
- `SCOPE_LEAK`: output includes formal spec, plan, task, API contract, database schema, domain model, code implementation, or test-suite work.
- `UNSUPPORTED_INFERENCE`: an unconfirmed item is written as fact.
- `EMPTY_PRIMARY_ARTIFACT`: `uc.md` lacks roles, goals, main flow, success criteria, or out-of-scope sections.
- `TEMPLATE_BYPASS`: templates were not loaded or the output structure bypasses them.

If any blocker is present, report the blocker code and do not claim the inception product artifacts are ready.

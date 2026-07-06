---
description: Reverse-generate an architecture planning contract from observable repository evidence.
scripts:
  sh: .specify/extensions/arch/scripts/bash/setup-arch.sh --json
  ps: .specify/extensions/arch/scripts/powershell/setup-arch.ps1 -Json
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding when it is not empty. User input may scope repository inspection or state external constraints, but user input alone must not prove a reverse-generated architecture rule.

## Goal

Reverse-generate or refresh the only architecture artifact:

- Planning contract: `.specify/memory/architecture.md`

The planning contract is the downstream planning surface. Repository evidence may be inspected during the command, but it must be summarized only inside plan-facing contract sections and open architecture questions.

## Operating Boundaries

- Write only `ARCH_FILE`.
- Do not create, update, or require separate 4+1 view files.
- Do not create, update, or require `.specify/memory/architecture-repo-facts.md`.
- Do not modify source code, feature specs, plans, tasks, tests, root `docs/`, deployment manifests, package files, infrastructure files, or runbooks.
- Stay at architecture planning-contract level. Do not promote implementation details into planning rules.

## Evidence Sources

Inspect observable repository evidence such as README files, entry points, package manifests, routes, workers, tests, configuration, scripts, CI, deployment clues, and existing `.specify/memory/repository-first/` artifacts when present.

Every reverse-derived planning rule must be supported by observable repository evidence or a stated external constraint. Git history alone must not prove an architecture rule.

## Internal 4+1 Reasoning Lens

Use these lenses to classify evidence, but render only the planning contract:

- Scenario lens: user-visible behaviors, actors, entry points, main paths, and failure paths.
- Logical lens: capability boundaries, domain concepts, ownership, state responsibility, and invariants.
- Process lens: runtime links, handoffs, approvals, receipts, and failure closure.
- Development lens: module boundaries, dependency direction, package ownership, and code-organization constraints.
- Physical lens: deployment assumptions, external systems, runtime environment, fact sources, and operational constraints.

## Structured Contract

`ARCH_SCHEMA_FILE` is the authoritative working-model contract for the planning contract. Shape a JSON-compatible working model before rendering Markdown with `architecture-template.md`.

`ARCH_VALIDATOR_FILE` and `ARCH_VALIDATOR_PS_FILE` provide the executable planning readiness gate. After rendering candidate changes, run the validator and report `planning_gate`, `ready_gate`, blocker codes, affected artifacts, and affected sections.

Every reverse-derived rule row must include `Source / Basis` inside `.specify/memory/architecture.md`. Because this command writes only one artifact, repository evidence must be summarized in that column or in `Open Architecture Questions`, not in a secondary evidence file.

## Outline

1. Run `{SCRIPT}` from repo root and parse JSON for `ARCH_FILE`, `ARCH_SCHEMA_FILE`, `ARCH_VALIDATOR_FILE`, and `ARCH_VALIDATOR_PS_FILE`.
2. Load `ARCH_FILE`, `ARCH_SCHEMA_FILE`, and `architecture-template.md`.
3. Inspect repository evidence within the user's scope, or the full repository when no scope is provided.
4. Use the internal 4+1 reasoning lens to project eligible evidence into plan-facing architecture rules.
5. Render `ARCH_FILE` with the required planning contract sections.
6. Run the readiness validator. Report `planning_gate`, `ready_gate`, blockers, updated path, evidence gaps, and open architecture questions.

## Quality Gates

- BLOCKER `ARCH_SOURCE_MISSING` if a reverse-derived planning rule lacks observable repository evidence or a stated external constraint.
- BLOCKER `ARCH_GIT_HISTORY_ONLY` if Git history is used as the sole support for a planning rule.
- BLOCKER `ARCH_PLANNING_SCOPE_RULES_MISSING` if the contract has no supported Planning Scope Rules.
- BLOCKER `ARCH_CAPABILITY_BOUNDARIES_MISSING` if the contract has no supported Capability Boundaries.
- BLOCKER `ARCH_CONSTRAINTS_OR_DECISIONS_MISSING` if both Required Constraints and Architecture Decisions Already Made are empty.
- BLOCKER `ARCH_PLAN_REVIEW_CHECKLIST_MISSING` if the contract has no supported Plan Review Checklist.
- BLOCKER `ARCH_UNSUPPORTED_CONCLUSION` if concrete package trees, classes, functions, endpoints, database structures, framework wiring, deployment manifests, scripts, runbooks, plans, tasks, or test strategy are promoted into planning rules.
- BLOCKER `ARCH_OPEN_QUESTION_STATUS_INVALID` if an open architecture question does not use `BLOCKS_PLAN` or `CAN_PROCEED_WITH_GUARDRAIL`.
- Place unsupported conclusions in `Open Architecture Questions`, not in planning-rule tables.

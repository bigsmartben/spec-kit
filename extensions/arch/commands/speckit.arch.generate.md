---
description: Generate an architecture planning contract for downstream Spec Kit planning.
scripts:
  sh: .specify/extensions/arch/scripts/bash/setup-arch.sh --json
  ps: .specify/extensions/arch/scripts/powershell/setup-arch.ps1 -Json
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding when it is not empty.

## Goal

Generate or refresh the planning-facing architecture contract:

- Target artifact: `.specify/memory/architecture.md`
- Optional input: `.specify/memory/uc.md`
- Optional existing memory: current `.specify/memory/architecture.md`

This command uses 4+1 as an internal reasoning lens only. Do not create, update, or require separate 4+1 view files.

## Operating Boundaries

- Write only `ARCH_FILE`.
- Read `.specify/memory/uc.md` only as optional product/use-case background.
- Do not modify `.specify/memory/uc.md`, `.specify/memory/constitution.md`, feature specs, plans, tasks, source code, tests, root `docs/`, deployment manifests, package files, infrastructure files, or runbooks.
- Stay at architecture planning-contract level. Record implementation design pressure as plan guardrails, prohibited directions, extension points, or open architecture questions.

## Internal 4+1 Reasoning Lens

Use these lenses to prevent omissions, but render only the planning contract:

- Scenario lens: identify goals, actors, main paths, alternate paths, and failure paths that a downstream plan must preserve.
- Logical lens: identify capability boundaries, domain concepts, ownership, state responsibility, and invariants.
- Process lens: identify runtime collaboration, handoffs, approval points, receipts, and failure closure.
- Development lens: identify module boundaries, dependency direction, package ownership, and code-organization constraints.
- Physical lens: identify deployment assumptions, external systems, runtime environment, fact sources, and operational constraints.

## Structured Contract

`ARCH_SCHEMA_FILE` is the authoritative working-model contract for the planning contract. Shape a JSON-compatible working model before rendering Markdown with `architecture-template.md`.

`ARCH_VALIDATOR_FILE` and `ARCH_VALIDATOR_PS_FILE` provide the executable planning readiness gate. After rendering candidate changes, run the validator and report `planning_gate`, `ready_gate`, blocker codes, affected artifacts, and affected sections.

Every plan-facing rule row must include `Source / Basis`. Use user input, `.specify/memory/uc.md`, existing architecture memory, or an explicitly stated architecture assumption as the basis. If the basis is missing, record the gap in `Open Architecture Questions` instead of turning it into a rule.

## Outline

1. Run `{SCRIPT}` from repo root and parse JSON for `ARCH_FILE`, `ARCH_SCHEMA_FILE`, `ARCH_VALIDATOR_FILE`, and `ARCH_VALIDATOR_PS_FILE`.
2. Load `ARCH_FILE`, `ARCH_SCHEMA_FILE`, `architecture-template.md`, and `.specify/memory/uc.md` if present.
3. Use the internal 4+1 reasoning lens to identify plan-facing architecture rules.
4. Render `ARCH_FILE` with the required planning contract sections.
5. Run the readiness validator. Report `planning_gate`, `ready_gate`, blockers, updated paths, and open architecture questions.

## Quality Gates

- BLOCKER `ARCH_PLANNING_SCOPE_RULES_MISSING` if the contract has no supported Planning Scope Rules.
- BLOCKER `ARCH_CAPABILITY_BOUNDARIES_MISSING` if the contract has no supported Capability Boundaries.
- BLOCKER `ARCH_CONSTRAINTS_OR_DECISIONS_MISSING` if both Required Constraints and Architecture Decisions Already Made are empty.
- BLOCKER `ARCH_PLAN_REVIEW_CHECKLIST_MISSING` if the contract has no supported Plan Review Checklist.
- BLOCKER `ARCH_SOURCE_MISSING` if a rule-bearing row has no supported `Source / Basis`.
- BLOCKER `ARCH_UNSUPPORTED_CONCLUSION` if the contract contains implementation tasks, source file edits, class designs, API schemas, database schemas, deployment manifests, runbooks, test strategy, or downstream-owned requirement IDs.
- BLOCKER `ARCH_OPEN_QUESTION_STATUS_INVALID` if an open architecture question does not use `BLOCKS_PLAN` or `CAN_PROCEED_WITH_GUARDRAIL`.
- Record missing architecture evidence in `Open Architecture Questions` instead of inventing planning rules.

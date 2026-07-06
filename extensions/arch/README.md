# Spec Kit Architecture Planning Contract Extension

Guide downstream Spec Kit plans with explicit architecture constraints.

Spec Kit turns feature specs into plans, tasks, and implementation work. Those plans need stable architecture context: which boundaries cannot be crossed, which capabilities own which responsibilities, which decisions have already been made, and which architecture gaps must block or shape planning.

This extension records that context in `.specify/memory/architecture.md` as a planning contract. The contract is intentionally plan-facing: it tells `/plan` what it must preserve, what it must not invent, where extension is allowed, and when architecture review is required.

Each rule-bearing row carries `Source / Basis` so the single artifact remains traceable without a secondary evidence file.

## When You Need This

Use this extension when you want downstream planning to respect project-level architecture:

- You are starting or reshaping a Spec Kit project and want plan guardrails before detailed planning.
- You have an existing repository and need planning constraints derived from observable repository evidence.
- You want stable boundaries, constraints, prohibited directions, and open architecture questions captured in one place.
- You need architecture guidance without producing implementation plans, task lists, API schemas, database schemas, deployment manifests, or runbooks.

## Install

The extension is listed in the Spec Kit community catalog for discovery:

```bash
specify extension search arch
specify extension info arch
```

Install the published release directly from GitHub:

```bash
specify extension add arch --from https://github.com/bigsmartben/spec-kit-arch/archive/refs/tags/v2.0.0.zip
```

Install from a local development checkout:

```bash
specify extension add --dev /home/administrator/github/spec-kit-arch
```

After installation, the extension is copied under:

```text
.specify/extensions/arch/
```

## Commands

The extension id is `arch`, and each command uses `.arch` as the command namespace. The extension provides two default commands:

```text
/speckit.arch.generate
/speckit.arch.reverse
```

| Command | Use when | Evidence source | Writes |
| --- | --- | --- | --- |
| `/speckit.arch.generate` | You know the intended product direction and want architecture planning guardrails | User input, current architecture memory, optional `.specify/memory/uc.md` | `.specify/memory/architecture.md` |
| `/speckit.arch.reverse` | You are onboarding or documenting an existing repository | Observable repository evidence inspected during the command | `.specify/memory/architecture.md` |

## Planning Contract

The primary artifact is:

```text
.specify/memory/architecture.md
```

It uses this structure:

- Architecture Intent
- Planning Scope Rules
- Capability Boundaries
- Required Constraints
- Architecture Decisions Already Made
- Allowed Extension Points
- Prohibited Plan Directions
- Open Architecture Questions
- Plan Review Checklist

Rule-bearing sections include `Source / Basis`. Open architecture questions also include a planning status: `BLOCKS_PLAN` or `CAN_PROCEED_WITH_GUARDRAIL`.

The contract is usable when the planning readiness validator reports:

```text
planning_gate: USABLE
ready_gate: PASS
```

If readiness is blocked, the validator emits stable blocker codes such as:

- `ARCH_PLACEHOLDER_PRESENT`
- `ARCH_PLANNING_SCOPE_RULES_MISSING`
- `ARCH_CAPABILITY_BOUNDARIES_MISSING`
- `ARCH_CONSTRAINTS_OR_DECISIONS_MISSING`
- `ARCH_PLAN_REVIEW_CHECKLIST_MISSING`
- `ARCH_SOURCE_MISSING`
- `ARCH_UNSUPPORTED_CONCLUSION`
- `ARCH_OPEN_QUESTION_STATUS_INVALID`

Blocked contracts can still expose useful questions, but downstream plans must not treat missing architecture decisions as permission to invent them.

## Internal Reasoning Model

The commands use 4+1 as an internal reasoning lens, not as the default artifact shape:

- Scenario lens: goals, actors, main paths, alternate paths, and failure paths.
- Logical lens: capability boundaries, domain concepts, ownership, state responsibility, and invariants.
- Process lens: runtime collaboration, handoffs, approval points, receipts, and failure closure.
- Development lens: module boundaries, dependency direction, package ownership, and code-organization constraints.
- Physical lens: deployment assumptions, external systems, runtime environment, fact sources, and operational constraints.

These lenses help prevent omissions, but downstream planning consumes the single planning contract.

## Files Written

Both default commands write only:

```text
.specify/memory/architecture.md
```

The commands do not edit:

```text
.specify/memory/uc.md
.specify/memory/constitution.md
feature specs
plans
tasks
source code
tests
root docs/
deployment manifests
package files
infrastructure files
runbooks
other `.specify/memory/architecture*.md` files
```

## Development

Validate the extension from a fresh project:

```bash
specify init /tmp/spec-kit-arch-test --ai codex --ignore-agent-tools --script sh
cd /tmp/spec-kit-arch-test
specify extension add --dev /home/administrator/github/spec-kit-arch
.specify/extensions/arch/scripts/bash/setup-arch.sh --json
.specify/extensions/arch/scripts/bash/validate-arch-artifacts.sh --json
```

Run the repository contract test after command, template, schema, setup-script, validator, or documentation changes:

```bash
bash tests/repository-first-contract.sh
```

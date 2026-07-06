# Spec Kit Extension Submission

Extension ID: arch
Name: Architecture Planning Contract
Version: 2.0.0
Description: Generate or reverse a planning-focused architecture contract that guides downstream Spec Kit plans
Author: bigsmartben
Repository URL: https://github.com/bigsmartben/spec-kit-arch
Download URL: https://github.com/bigsmartben/spec-kit-arch/archive/refs/tags/v2.0.0.zip
Documentation URL: https://github.com/bigsmartben/spec-kit-arch#readme
License: MIT
Required Spec Kit version: >=0.8.10.dev0
Commands count: 2
Hooks count: 0
Tags: architecture, planning-contract, workflow, design

Key features:
- Provides `/speckit.arch.generate` for forward generation of `.specify/memory/architecture.md` as a planning contract.
- Provides `/speckit.arch.reverse` for reverse generation from observable repository evidence.
- Keeps `.specify/memory/architecture.md` as the only generated architecture artifact.
- Uses 4+1 only as an internal reasoning lens so default output stays focused on downstream planning constraints.
- Defines plan-facing sections for planning scope rules, capability boundaries, required constraints, existing decisions, extension points, prohibited plan directions, open questions, and a plan review checklist.
- Ships a schema-backed artifact contract plus bash and PowerShell readiness validators that emit `planning_gate`, compatibility `ready_gate`, and stable blocker codes.
- Requires rule-bearing rows to include `Source / Basis`, validates open-question planning status, and blocks implementation-level conclusions from the architecture artifact.
- Restricts writes to `.specify/memory/architecture.md`.

Testing performed:
- Bash setup helper verified with `.specify/extensions/arch/scripts/bash/setup-arch.sh --json`.
- Bash readiness validator verified with `.specify/extensions/arch/scripts/bash/validate-arch-artifacts.sh --json`.
- Repository contract test: `bash tests/repository-first-contract.sh`.

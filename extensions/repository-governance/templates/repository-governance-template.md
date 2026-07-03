# Project Governance Projection Template

<!--
Sync Impact Report
-->

## Final Output

- active agent platform project-governance projection
- generated active agent platform target file

## Repository-Wide Instructions

- Framework: Project Governance Projection Framework.
- Treat this file as the active project-governance entrypoint for coding-agent work in this repository.
- Keep task reasoning grounded in source-backed repository facts, matched SSOT routes, and explicit user instructions.
- Keep edits scoped to the active task and matched path family.
- architecture methodology: owned by Architecture SSOT.

### Authority

1. Current user instruction
2. Safety and permission constraints
3. Vertical SSOT documents
4. Current repository code and configuration facts
5. Active `PROJECT GOVERNANCE` projection
6. Tests and CI results
7. Historical documents
8. Explicit assumptions for reversible local edits

- Active projection is generated routing guidance and is subordinate to explicit vertical SSOT documents or source-backed repository facts on substantive conflicts.

## SSOT Index

- Architecture SSOT: owns architecture boundaries, interfaces, dependencies, runtime constraints, deployment assumptions, and scenario-level architecture decisions.
- Engineering SSOT: owns branch, version, release, CI/CD, collaboration process, standard tools, command entrypoints, configuration templates, and execution constraints.
- Code Style SSOT: owns naming, formatting, comments, error handling, logging, tests, and quality standards.
- Directory Structure SSOT: owns directory layout, file placement, module organization, and configuration locations.
- Agent Harness SSOT: owns agent task boundaries, tool usage, permissions, audit, validation, and failure handling.
- Architecture SSOT index:
  - status: missing
  - source_refs: none detected
  - gap: NEEDS_CLARIFICATION:ARCHITECTURE
- Engineering SSOT index:
  - status: missing
  - source_refs: none detected
  - gap: NEEDS_CLARIFICATION:ENGINEERING
- Code Style SSOT index:
  - status: missing
  - source_refs: none detected
  - gap: NEEDS_CLARIFICATION:CODE_STYLE
- Directory Structure SSOT index:
  - status: missing
  - source_refs: none detected
  - gap: NEEDS_CLARIFICATION:DIRECTORY_STRUCTURE
- Agent Harness SSOT index:
  - status: missing
  - source_refs: none detected
  - gap: NEEDS_CLARIFICATION:AGENT_HARNESS

### Missing SSOT Handling

- If a vertical SSOT is missing or incomplete, treat repository evidence as descriptive context only.
- Before changing a surface governed by missing SSOT, ask for clarification or record `NEEDS_CLARIFICATION:<SSOT>` in handoff.
- Use existing code and config facts for narrow edits only when task scope and validation are explicit.
- Do not invent repository policy from descriptive repository evidence.

## Path And Task Scope Rules

- Source, API, route, runtime, infra, or dependency-boundary changes: read Architecture SSOT before planning edits.
- Build, release, CI, manifest, lockfile, command, template, or runtime configuration changes: read Engineering SSOT before edits.
- Formatting, linting, typing, testing, logging, comments, naming, or error-handling changes: read Code Style SSOT before edits.
- New files, moved files, generated assets, or directory responsibility changes: read Directory Structure SSOT before edits.
- Agent instructions, permissions, MCP, external tools, skills, validation, or failure-handling changes: read Agent Harness SSOT before edits.
- If multiple rules match, read every matched SSOT and apply the highest authority non-conflicting rule.

### Directory Structure Fallback

- Use only when Directory Structure SSOT is missing and the task scope is explicit.
- Treat scanned repository areas as descriptive context, not as approved directory policy.
- Keep new or moved files aligned with existing nearby conventions unless the user supplies a different target.
- Record `NEEDS_CLARIFICATION:DIRECTORY_STRUCTURE` in handoff when placement is ambiguous.

## Agent Harness

- Repository capability layer: source-backed repository-local skills and MCP candidates only.
- Agent adapter layer: use explicit integration support when available; otherwise use generic fallback rules.
- Platform projection layer: apply only rules supported by the active target file.
- Repository-local skills: evidence only unless an explicit Agent Harness SSOT source names them; read matching `SKILL.md` before planning or editing.
- MCP-backed external tools: indexed as MCP config candidates only; enumerate runtime tools before use.
- Repository config candidates are evidence only unless the active adapter supports them.
- If a matching skill lacks scope or validation guidance, ask for clarification before expanding writes.
- MCP default: read-only.
- MCP mutation: explicit user intent with target, action, and expected effect.
- Secrets: never log, never write.

## Write Boundaries

- Scope: active task only.
- Agent context files: edit only when the user explicitly asks for instruction changes.
- Protected files: implementation paths, CI configuration, MCP configuration, secrets, permissions, tool settings, and arbitrary repository paths outside the resolved write surface.
- Protected-file writes: explicit user request, named matching contract or regression test, and passing validation commands.

## Handoff

- changed files
- commands run
- validation result
- unresolved risks

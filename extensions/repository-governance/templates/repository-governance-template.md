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
- Keep task reasoning grounded in source-backed repository facts, matched directory-tree routes, and explicit user instructions.
- Keep edits scoped to the active task and matched fixed directory tree.
- Fixed directory-tree SSOT: when a path matches `agent-runtime/`, `engineering-runtime/`, `poc/`, `source-code/`, `test-code/`, or `other-tools/`, route it to that SSOT.

### Authority

1. Current user instruction
2. Safety and permission constraints
3. Fixed directory-tree SSOT documents
4. Current repository code and configuration facts
5. Active `PROJECT GOVERNANCE` projection
6. Tests and CI results
7. Historical documents
8. Explicit assumptions for reversible local edits

- Active projection is generated routing guidance and is subordinate to explicit fixed directory-tree SSOT documents or source-backed repository facts on substantive conflicts.

## SSOT Index

- `agent-runtime/`: `.codex/`, `.claude/`, `AGENTS.md`, `CLAUDE.md`, and other agent rule files.
- `engineering-runtime/`: `.github/workflows/`, Docker files, environment files, manifests, lockfiles, DevOps, infra, and secrets/key/password configuration surfaces.
- `poc/`: pre-iteration exploration for technical spikes, architecture drafts, UC designs, prototypes, research notes, validation reports, and validation conclusions.
- `source-code/`: client, server, API, route, library, service, script, command, and template code.
- `test-code/`: test code, fixtures, prepared data, test resources, reports, and test conclusions.
- `other-tools/`: `tools/`, `.codegraph/`, MCP config files, `.vscode/`, `.idea/`, and auxiliary tool settings.
- `agent-runtime/` SSOT index:
  - status: missing
  - source_refs: none detected
  - gap: NEEDS_CLARIFICATION:agent-runtime
- `engineering-runtime/` SSOT index:
  - status: missing
  - source_refs: none detected
  - gap: NEEDS_CLARIFICATION:engineering-runtime
- `poc/` SSOT index:
  - status: missing
  - source_refs: none detected
  - gap: NEEDS_CLARIFICATION:poc
- `source-code/` SSOT index:
  - status: missing
  - source_refs: none detected
  - gap: NEEDS_CLARIFICATION:source-code
- `test-code/` SSOT index:
  - status: missing
  - source_refs: none detected
  - gap: NEEDS_CLARIFICATION:test-code
- `other-tools/` SSOT index:
  - status: missing
  - source_refs: none detected
  - gap: NEEDS_CLARIFICATION:other-tools

### Missing SSOT Handling

- If a fixed directory-tree SSOT is missing or incomplete, treat repository evidence as descriptive context only.
- Before changing a surface governed by missing SSOT, ask for clarification or record `NEEDS_CLARIFICATION:<SSOT>` in handoff.
- Use existing code and config facts for narrow edits only when task scope and validation are explicit.
- Do not invent repository policy from descriptive repository evidence.

## Directory Tree And Task Scope Rules

- Routing rule: seeing a file in one fixed directory tree classifies it as that SSOT; no match falls through to Directory Tree Fallback.
- `agent-runtime/`: `.codex/`, `.claude/`, `AGENTS.md`, `CLAUDE.md`, and other agent rule files; read `agent-runtime/` SSOT before edits.
- `engineering-runtime/`: `.github/workflows/`, Docker files, environment files, manifests, lockfiles, DevOps, infra, secrets, key, password, and permission surfaces; read `engineering-runtime/` SSOT before edits.
- `poc/`: `technical-spikes/`, `architecture-drafts/`, `uc-designs/`, `prototypes/`, `research-notes/`, and `validation-reports/`; read `poc/` SSOT before edits.
- `poc/` content is not formal implementation.
- Before editing `source-code/` from POC work, create or cite a formal design or task; implement from that artifact, not by copying experimental code directly.
- POC conclusions must include validation record source_refs under `poc/validation-reports/`; otherwise record `NEEDS_CLARIFICATION:poc-validation-record` in handoff.
- `source-code/`: `src/`, `app/`, `client/`, `server/`, `api/`, `lib/`, `services/`, `scripts/`, `commands/`, and `templates/`; read `source-code/` SSOT before edits.
- `test-code/`: `tests/`, `test/`, `e2e/`, `fixtures/`, `testdata/`, `test-results/`, and `coverage/`; read `test-code/` SSOT before edits.
- `other-tools/`: `tools/`, `.codegraph/`, MCP config files, `.vscode/`, and `.idea/`; read `other-tools/` SSOT before edits.
- If multiple trees match, read every matched SSOT and apply the highest authority non-conflicting rule.

### Directory Tree Fallback

- Use only when no fixed directory-tree SSOT matches, or the matched tree has no source_refs and the task scope is explicit.
- Treat scanned repository areas as descriptive context, not as approved path policy.
- Keep new or moved files aligned with existing nearby conventions unless the user supplies a different target.
- Record the matched `NEEDS_CLARIFICATION:<SSOT>` gap in handoff when placement is ambiguous.

## agent-runtime

- Repository capability layer: source-backed repository-local skills and MCP candidates only.
- Agent adapter layer: use explicit integration support when available; otherwise use generic fallback rules.
- Platform projection layer: apply only rules supported by the active target file.
- Repository-local skills: evidence only unless an explicit `agent-runtime/` SSOT source names them; read matching `SKILL.md` before planning or editing.
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

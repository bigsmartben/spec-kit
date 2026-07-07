# Spec Kit Repository Governance

Generate project-governance projections for the active Spec Kit agent platform target.

## Output

- Active agent platform target from safe `context_file` override or Spec Kit integration metadata.
- Generated `PROJECT GOVERNANCE` projection file.
- Target file content is a runtime project-governance entrypoint for coding agents, not a generator operations manual.

## Scope

- Generate the resolved active agent platform target when missing.
- Update existing active target project-governance projections.
- Scan repository areas as bounded evidence for missing-SSOT fallback.
- Capture repository facts as bounded evidence for gap handling and CLI reporting.
- Structure generated instructions as repository-wide, directory-tree scope, and `agent-runtime/` guidance.
- Project agent platform adapter rules from Spec Kit integration metadata.
- Index explicit fixed directory-tree SSOT entrypoints in the generated SSOT index.
- Report repository-local skills and MCP config files as evidence candidates only unless an explicit `agent-runtime/` SSOT source names them.
- Analyze repository areas to depth 2 only for evidence and CLI summaries.
- Use Directory Tree fallback only when no fixed directory-tree SSOT matches, or the matched tree has no source_refs and task scope is explicit.
- Overwrite the active agent platform target on generation.
- Do not generate Copilot `.github/instructions/*.instructions.md` companion files.
- Generate repository evidence from the current repository state on every run.
- Review only the active agent platform target.
- Remove legacy managed sections only from non-active context files enumerated by `CONTEXT_FILES`.
- Missing fixed directory-tree SSOT is reported as a clarification need for governed changes; generated output must not invent repository policy from descriptive repository evidence.
- Do not project full repository fact inventories, repository area lists, skill capability lists, or development command lists into the active target.

## Install

```bash
specify extension add repository-governance --from https://github.com/bigsmartben/spec-kit-agent-governance/archive/refs/tags/v3.0.2.zip
```

Local development:

```bash
specify extension add --dev /path/to/spec-kit-agent-governance
```

## Run

```text
/speckit.repository-governance.generate
```

Helper:

```bash
uv run python .specify/extensions/repository-governance/scripts/generate_repository_governance.py
```

## Build

```bash
uv run python tools/build_repository_governance_zip.py
```

## Files

- `extension.yml`
- `commands/speckit.repository-governance.generate.md`
- `scripts/generate_repository_governance.py`
- `templates/repository-governance-template.md`

## SSOT Index

- `agent-runtime/` SSOT index: status, source_refs, and gap code.
- `engineering-runtime/` SSOT index: status, source_refs, and gap code.
- `poc/` SSOT index: status, source_refs, and gap code.
- `source-code/` SSOT index: status, source_refs, and gap code.
- `test-code/` SSOT index: status, source_refs, and gap code.
- `other-tools/` SSOT index: status, source_refs, and gap code.
- Repository-level and nested project evidence is scanned through fixed directory trees with bounded parent depth, and matched tree entrypoints become SSOT index source_refs.
- `agent-runtime/` examples include `.codex/`, `.claude/`, `AGENTS.md`, `CLAUDE.md`, and other agent rule files.
- `engineering-runtime/` examples include `.github/workflows/`, environment files, DevOps, CI/CD, Docker, manifests, lockfiles, permissions, password, key, and secrets surfaces.
- `poc/` examples include technical spikes, architecture drafts, UC designs, prototypes, research notes, validation reports, and validation conclusions before formal iteration.
- `source-code/` examples include client, server, API, route, library, script, command, and template code.
- `test-code/` examples include test code, fixtures, prepared data, resources, reports, and test conclusions.
- `other-tools/` examples include `.codegraph/`, editor tooling, MCP configs, and `tools/`.

## Instruction Layers

- Repository-wide instructions summarize authority, active-target scope, write boundaries, validation commands, and handoff expectations.
- SSOT index maps `agent-runtime/`, `engineering-runtime/`, `poc/`, `source-code/`, `test-code/`, and `other-tools/` to source_refs and gap codes.
- SSOT routing maps task types and repository paths to fixed directory-tree SSOT entries.
- Path and task scope rules keep generated guidance deterministic without expanding the write surface.
- `poc/` routing keeps exploration out of formal implementation: before editing `source-code/` from POC work, create or cite a formal design or task; POC conclusions need validation record source_refs under `poc/validation-reports/` or `NEEDS_CLARIFICATION:poc-validation-record`.
- Agent runtime instructions cover adapter behavior, repository-local skills, MCP discovery, external tools, permissions, and failure handling.
- The extension emits one active target file and does not generate platform companion instruction files.

## Evidence Discovery

- Repository facts are scanned from README files, project docs, repository policy files, feature specs, source/test paths, nested manifests, and runtime/build configuration.
- Development command sources are scanned from package scripts or Python/uv test conventions.
- Scanned facts feed missing-SSOT handling and CLI evidence summaries; only matched fixed directory-tree entrypoints are projected as SSOT source_refs.

## Agent Adapter

- Repository capability layer: source-backed repository-local skills and MCP candidates only.
- Agent adapter layer: use explicit integration support when available; otherwise use generic fallback rules.
- Platform projection layer: apply only rules supported by the active target file.

Repository-local `SKILL.md` files are reported as evidence and read when they match the task; they are not `agent-runtime/` SSOT source_refs unless an explicit `agent-runtime/` SSOT source names them. MCP config files are reported as candidates and evidence only; active servers, resources, and tools must be enumerated from the agent platform runtime before use.

## Verify

```bash
uv run --locked python -m py_compile scripts/generate_repository_governance.py tools/build_repository_governance_zip.py tests/test_governance_domains.py
uv run --locked pytest -q
```

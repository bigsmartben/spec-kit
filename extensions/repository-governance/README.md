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
- Structure generated instructions as repository-wide, path-scope, and agent-harness guidance.
- Project agent platform adapter rules from Spec Kit integration metadata.
- Index only explicit SSOT content entrypoints in the generated SSOT index.
- Report repository-local skills and MCP config files as evidence candidates only unless an explicit Agent Harness SSOT source names them.
- Analyze repository areas to depth 2 only for evidence and CLI summaries.
- Use Directory Structure fallback only when the Directory Structure SSOT is missing and task scope is explicit.
- Overwrite the active agent platform target on generation.
- Do not generate Copilot `.github/instructions/*.instructions.md` companion files.
- Generate repository evidence from the current repository state on every run.
- Review only the active agent platform target.
- Remove legacy managed sections only from non-active context files enumerated by `CONTEXT_FILES`.
- Missing vertical SSOT is reported as a clarification need for governed changes; generated output must not invent repository policy from descriptive repository evidence.
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

- Architecture SSOT index: status, source_refs, and gap code.
- Engineering SSOT index: status, source_refs, and gap code.
- Code Style SSOT index: status, source_refs, and gap code.
- Directory Structure SSOT index: status, source_refs, and gap code.
- Agent Harness SSOT index: status, source_refs, and gap code.
- Repository-level and nested project evidence is scanned through explicit path families with bounded parent depth, but only explicit SSOT content entrypoints become SSOT index source_refs.
- `extension.yml` and `.extensionignore` are Engineering SSOT refs only in this extension source repository; other projects report them as evidence.

## Instruction Layers

- Repository-wide instructions summarize authority, active-target scope, write boundaries, validation commands, and handoff expectations.
- SSOT index maps Architecture, Engineering, Code Style, Directory Structure, and Agent Harness categories to source_refs and gap codes.
- SSOT routing maps task types and path families to Architecture, Engineering, Code Style, Directory Structure, and Agent Harness SSOT entries.
- Path and task scope rules keep generated guidance deterministic without expanding the write surface.
- Agent harness instructions cover adapter behavior, repository-local skills, MCP discovery, external tools, permissions, and failure handling.
- The extension emits one active target file and does not generate platform companion instruction files.

## Evidence Discovery

- Repository facts are scanned from README files, project docs, repository policy files, feature specs, source/test paths, nested manifests, and runtime/build configuration.
- Development command sources are scanned from package scripts or Python/uv test conventions.
- Scanned facts feed missing-SSOT handling and CLI evidence summaries; they are not projected as SSOT source_refs or full content lists into the active target unless they are explicit SSOT content entrypoints.

## Agent Adapter

- Repository capability layer: source-backed repository-local skills and MCP candidates only.
- Agent adapter layer: use explicit integration support when available; otherwise use generic fallback rules.
- Platform projection layer: apply only rules supported by the active target file.

Repository-local `SKILL.md` files are reported as evidence and read when they match the task; they are not Agent Harness SSOT source_refs unless an explicit Agent Harness SSOT source names them. MCP config files are reported as candidates and evidence only; they are not SSOT source_refs, and active servers, resources, and tools must be enumerated from the agent platform runtime before use.

## Verify

```bash
uv run --locked python -m py_compile scripts/generate_repository_governance.py tools/build_repository_governance_zip.py tests/test_governance_domains.py
uv run --locked pytest -q
```

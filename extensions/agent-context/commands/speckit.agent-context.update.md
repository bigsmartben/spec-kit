---
description: "Refresh the managed Spec Kit section in coding agent context file(s)"
---

# Update Coding Agent Context

Refresh the managed Spec Kit section inside the active coding agent's context/instruction file (e.g. `CLAUDE.md`, `.github/copilot-instructions.md`, `AGENTS.md`).

## Behavior

The script reads the agent-context extension config at
`.specify/extensions/agent-context/agent-context-config.yml` to discover:

- `context_file` — the path of the coding agent context file to manage.
- `context_files` — optional project-relative paths for multiple coding agent context files. When non-empty, the script updates each listed file and the list takes precedence over `context_file`.
- `context_markers.start` / `.end` — the delimiters surrounding the managed section. Defaults to `<!-- SPECKIT START -->` and `<!-- SPECKIT END -->` when the field is missing.

It then creates, replaces, or appends the managed block so that it points at the active feature's currently available `spec.md`, `prototype.html`, `quickstart.md`, and `tasks.md`. The active directory comes from `.specify/feature.json`; when that file is unavailable or stale, the scripts safely discover the most recently updated feature under `specs/` by its `spec.md`.

If `context_files` and `context_file` are empty, the command reports nothing to do and exits successfully. Context file paths must stay project-relative; absolute paths, Windows drive paths, backslash separators, and `..` path segments are rejected.

## Execution

- **Bash**: `.specify/extensions/agent-context/scripts/bash/update-agent-context.sh [feature_directory]`
- **PowerShell**: `.specify/extensions/agent-context/scripts/powershell/update-agent-context.ps1 [feature_directory]`
- **Python**: `.specify/extensions/agent-context/scripts/python/update_agent_context.py [feature_directory]`

When `feature_directory` is omitted, the script derives it from
`.specify/feature.json`. If the recorded directory does not contain `spec.md`,
it falls back to safe recursive discovery under `specs/`, rejecting candidates
that resolve outside the project root.

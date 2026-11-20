# Personal Fork Agent Guide

This guide defines the default downstream workflow for `bigsmartben/spec-kit`.
It applies when an agent is asked to develop, publish, or install a personal
Spec Kit version. It does not authorize unrelated work or replace task-specific
approval requirements.

## Repository Roles

- `origin` must target `bigsmartben/spec-kit`.
- `upstream` must target `github/spec-kit`.
- Treat `upstream` as read-only unless the user explicitly requests an upstream
  contribution.
- Do not push to, open a pull request against, or post review activity in
  `github/spec-kit` unless that action is explicitly requested for the current
  task.

Before changing repository state, verify both remotes:

```powershell
git remote -v
git remote get-url origin
git remote get-url upstream
```

## Development Workflow

1. Preserve the user's existing commits, staged changes, and working tree.
2. Use a `feat/`, `fix/`, `docs/`, `community/`, or `chore/` branch in the
   personal fork. Include an issue number when one exists.
3. Read the relevant architecture and testing guidance indexed by `AGENTS.md`
   and `CONTRIBUTING.md` before changing implementation or behavior.
4. Make one focused change, add required positive/negative and regression
   coverage, and run the smallest relevant validation first.
5. Commit only the intended files. Agent-authored commits must include the
   `Assisted-by:` trailer required by `CONTRIBUTING.md`, and tool-generated
   `Co-authored-by:` trailers must be retained.
6. Push the feature branch to `origin`, never `upstream`.
7. For personal work, merge the branch into the personal fork's `main` only
   when the current task explicitly requests that lifecycle and the merge is
   safe. Open a pull request in `bigsmartben/spec-kit` when a review trail is
   useful; do not substitute an upstream pull request.

Do not reset, force-push, replace the personal `main`, or rewrite shared
history. If the local and remote histories have diverged, inspect and preserve
both lines before choosing a merge or a new integration branch.

## Upstream Synchronization

Synchronize through an integration branch:

```powershell
git fetch upstream
git fetch origin
git switch -c chore/sync-upstream-<date> origin/main
git merge upstream/main
```

Resolve conflicts without discarding personal changes, run the relevant tests,
and merge that integration branch into the personal fork only after the
task's requested validation succeeds. Do not rewrite the personal fork's
`main` to match upstream.

## Validation

Use this checkout's own environment:

```powershell
uv sync --extra test
uv pip install --python .venv\Scripts\python.exe -e .
.\.venv\Scripts\specify.exe --help
.\.venv\Scripts\python.exe -m pytest <affected-test-paths> -q
```

Add the required manual workflow evidence for slash-command behavior and
Windows PowerShell 5.1 evidence for PowerShell behavior. Do not run tests from
another checkout's editable install.

## Tags and Installation

For reproducible personal installation, prefer a commit SHA:

```powershell
uv tool install --force specify-cli --from "git+https://github.com/bigsmartben/spec-kit.git@<commit-sha>"
specify version
```

After a validated personal release, a stable personal tag may be used. Push
the exact tested commit and tag to `origin`:

```powershell
git tag personal-v<version>
git push origin personal-v<version>
```

Then install from that tag:

```powershell
uv tool install --force specify-cli --from "git+https://github.com/bigsmartben/spec-kit.git@personal-v<version>"
```

Do not wait for an upstream merge or PyPI release before using a validated
personal tag. A public fork is not a private artifact store; do not commit
credentials or confidential team data.

## Automation Boundary

This document and `AGENTS.md` guide coding agents. GitHub Actions does not read
or infer execution from them. Automation must be defined explicitly in
`.github/workflows/` only when a repeatable CI, build, or release task needs it.

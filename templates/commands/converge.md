---
description: Assess the codebase against the frozen Specify contract, Constitution principles and system boundaries, and tasks, then append only uncovered corrective work for Implement.
scripts:
  sh: scripts/bash/check-prerequisites.sh --json --require-contract --require-tasks --include-tasks
  ps: scripts/powershell/check-prerequisites.ps1 -Json -RequireContract -RequireTasks -IncludeTasks
  py: scripts/python/check_prerequisites.py --json --require-contract --require-tasks --include-tasks
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Pre-Execution Checks

**Check for extension hooks (before convergence)**:

- Check if `.specify/extensions.yml` exists in the project root.
- If it exists, read it and look for entries under the `hooks.before_converge` key
- If the YAML cannot be parsed or is invalid, do not skip silently: tell the user that `.specify/extensions.yml` could not be read (include the parser error) and that no hooks were checked, including any mandatory (`optional: false`) hooks registered there, then continue normally
- Filter out hooks where `enabled` is explicitly `false`. Treat hooks without an `enabled` field as enabled by default.
- For each remaining hook, do **not** attempt to interpret or evaluate hook `condition` expressions:
  - If the hook has no `condition` field, or it is null/empty, treat the hook as executable
  - If the hook defines a non-empty `condition`, skip the hook and leave condition evaluation to the HookExecutor implementation
- For each executable hook, output the following based on its `optional` flag:
  - **Optional hook** (`optional: true`):

    ```text
    ## Extension Hooks

    **Optional Pre-Hook**: {extension}
    Command: `/{command}`
    Description: {description}

    Prompt: {prompt}
    To execute: `/{command}`
    ```

  - **Mandatory hook** (`optional: false`):

    ```text
    ## Extension Hooks

    **Automatic Pre-Hook**: {extension}
    Executing: `/{command}`
    EXECUTE_COMMAND: {command}

    Wait for the result of the hook command before proceeding to the Goal.
    ```
    After emitting the block above you MUST actually invoke the hook and wait for it to finish before continuing. Run it the same way you would run the command yourself in this agent/session (the invocation may differ from the literal `{command}` id shown above, e.g. a skills-mode agent runs it as `/skill:speckit-...` or `$speckit-...`). Emitting the block alone does not run the hook.

- If no hooks are registered or `.specify/extensions.yml` does not exist, skip silently

## Goal

Close the gap between the frozen `spec.md`, `prototype.html`, and
`quickstart.md` contract, the Constitution principles and system boundaries,
plus `tasks.md` and what the codebase currently implements. Assess the current
state, determine which requirements, success criteria, prototype anchors, UAT
outcomes, Constitution obligations, system/subsystem/component boundaries, and
existing tasks are unmet, incomplete, or partially satisfied, and **append only
work that is not already represented by an existing task** at the bottom of
`tasks.md` so that
`__SPECKIT_COMMAND_IMPLEMENT__` can complete it. This command MUST run only after
`__SPECKIT_COMMAND_IMPLEMENT__` has run on the current `tasks.md`, and after `__SPECKIT_COMMAND_TASKS__` has produced a complete `tasks.md`.

This is **not** a diff tool and does **not** track changes. It assesses the present state
of the code relative to the feature's artifacts — no git, no branch comparison, no history.
Architecture drift may produce a corrective or refactoring `[BUILD]` task, but
the task MUST specify the required authority and observable outcome rather than
preselecting the implementation technique, file path, or internal class design.

## Operating Constraints

**APPEND-ONLY, NEVER REWRITE**: The command's **only** write is appending a new
`## Phase N: Convergence` section to `tasks.md`. It MUST NOT:

- modify the frozen `spec.md`, `prototype.html`, or `quickstart.md` contract
  or its UAT expectations in any way;
- rewrite, renumber, reorder, or delete any existing task (including tasks from a prior
  Convergence phase);
- modify, create, or delete any application code — completing the appended tasks is the
  job of `__SPECKIT_COMMAND_IMPLEMENT__`.

When the codebase already satisfies everything, the command MUST leave `tasks.md`
**byte-for-byte unchanged** (no empty Convergence header) and report a clean result.

**Constitution Authority**: The project constitution (`/memory/constitution.md`)
is **non-negotiable** for its governance principles and, when present, its
`Repository Architecture` boundary map. Treat only `SYS-*`, `SUB-*`, and
`CMP-*` responsibility boundaries as architecture authority. Product and
technical contracts remain owned by the frozen feature artifacts and any
explicit design artifact; do not infer them from the constitution. Code that
violates a MUST principle or a binding boundary produces a corresponding
remediation task. Feature artifacts may reference boundaries but MUST NOT
redefine system, subsystem, or component responsibility.

If the frozen product contract and Constitution conflict, STOP the affected
assessment path, report the authority conflict, and return the issue to
`__SPECKIT_COMMAND_CONSTITUTION__`, `__SPECKIT_COMMAND_SPECIFY__`, or
`__SPECKIT_COMMAND_CLARIFY__` as appropriate. Do not invent a task that lets code
silently satisfy only one side. If the constitution is an unfilled template,
skip constitution checks gracefully rather than failing. Do not treat an open
boundary decision as an approved rule.

## Execution Steps

### 1. Initialize Convergence Context

Run `{SCRIPT}` once from repo root and parse JSON for FEATURE_DIR and AVAILABLE_DOCS. Derive absolute paths:

- SPEC = FEATURE_DIR/spec.md
- PROTOTYPE = FEATURE_DIR/prototype.html
- QUICKSTART = FEATURE_DIR/quickstart.md
- TASKS = FEATURE_DIR/tasks.md
- CONSTITUTION = `/memory/constitution.md` (if present)
If the frozen contract or `tasks.md` is missing, STOP with a clear, actionable
message naming the prerequisite command to run (`__SPECKIT_COMMAND_SPECIFY__`
for a missing contract artifact,
`__SPECKIT_COMMAND_TASKS__` for missing tasks). Do not produce partial output.
For single quotes in args like "I'm Groot", use escape syntax: e.g 'I'\''m Groot' (or double-quote if possible: "I'm Groot").

### 2. Load Artifacts (Progressive Disclosure)

Load only the minimal necessary context from each artifact:

**From spec.md:**

- Functional Requirements (FR-###)
- Success Criteria (SC-###), including outcome and measurement-readiness work
- User Stories and their Acceptance Scenarios
- Edge Cases (if present)

**From prototype.html:**

- Exact `data-spec-ref` anchors and visible/state behavior

**From quickstart.md:**

- UAT IDs, expected results, source references, and recorded execution fields

**From tasks.md:**

- Task IDs (to compute the next ID and next phase number)
- Checkbox state and phase ownership
- Descriptions, task types, source references, dependencies, and completion
  conditions

**From constitution (if not an unfilled template):**

- Principle names and MUST/SHOULD normative statements
- If `## Repository Architecture` exists, build a boundary inventory from:
  - `SYS-*` system purpose and boundary
  - `SUB-*` subsystem responsibility and boundary
  - `CMP-*` component responsibility and boundary
- Do not interpret placeholders, template comments, or unresolved open
  boundary decisions as approved implementation obligations. Do not promote
  contract, interface, sequence, dependency, or invariant prose accidentally
  present in a legacy constitution into current architecture authority.

### 3. Build the Intent Inventory

Create an internal model (do not echo raw artifacts):

- **Requirements inventory**: one stable key per FR-### / SC-### / user-story
  acceptance scenario (for example, `US1/AC2`), every prototype anchor, every
  UAT, constitution principle that imposes a buildable obligation, and every
  resolved system boundary item.
- **Existing task map**: record every task ID, checkbox state, task type,
  exact source references, dependencies, phase, and observable `Done when`
  condition. Preserve each task's existing ownership; do not merge tasks solely
  because they share a source identifier.
- **UAT execution map**: resolve each `UAT-*` to its exactly one existing
  `[UAT]` task. Never infer that a new UAT execution task is needed merely
  because the existing task is unchecked, failed, blocked, or stale.
- **Code-scope map**: from task references, source identifiers, the implemented
  technology actually present in the repository, boundary evidence, and
  targeted source search, derive the files/components in scope. Do not infer
  technical obligations beyond the frozen product contract, Constitution
  authority, and existing tasks.

### 4. Assess the Codebase and Classify Findings

Include every existing task in the intent inventory, regardless of checkbox state or
Convergence phase: completion claims are not evidence. Verify current behavior against the frozen contract, tasks, and constitution;
for corrective task chains, assess the resulting
behavior, not superseded implementation details. Check both unmet obligations and
implementation that contradicts, exceeds, or falls outside the stated intent.
Assess Constitution boundary items only against the code's actual system,
subsystem, and component responsibility placement and boundary behavior. Assess
contract semantics, interface compatibility, interaction order, failure
behavior, and invariants from the frozen feature artifacts or an explicit
technical design artifact, not from the constitution.

For each item in the intent inventory, inspect the current code in scope and produce a
`Finding` only where there is a gap. Classify every finding by **gap type**:

- **`missing`**: the required work is absent from the code entirely.
- **`partial`**: the work exists but does not yet fully satisfy the requirement,
  acceptance criterion, prototype anchor, UAT outcome, system boundary, or task.
- **`contradicts`**: the code does something that conflicts with stated intent or a
  Constitution MUST principle or binding boundary obligation.
- **`unrequested`**: the code contains work not called for by the frozen
  contract, Constitution authority, or tasks
  (surfaced for awareness — converge does **not** delete code, it only appends a task to
  review/justify or remove it).

Each `Finding` records: a stable id, the `source-ref` it traces to, the `gap-type`,
a severity, a short human-readable description with the evidence (the file/area
observed), and one disposition:

- **`append_build`**: no existing task adequately covers the corrective work.
- **`reuse_task`**: an existing unchecked task, or an existing `[UAT]` task that
  must be re-executed, already covers the remaining work.

If the frozen contract, Constitution, or task authority is incomplete or
contradictory, STOP before Step 7; report the exact conflict to its owning
command and do not append implementation work that guesses how to reconcile it.

For a possible duplicate, compare exact source references and observable `Done
when` conditions; keyword similarity alone is insufficient. Reuse an existing
unchecked task when its completion condition already covers the finding. If an
existing task is checked but current evidence contradicts completion, append a
new corrective `[BUILD]` task rather than changing the old task.

**Edge cases:**

- Treat every `PENDING`, `FAIL`, or `BLOCKED` UAT as remaining work even when its
  task checkbox is checked. Treat `PASS` as evidence only when the Actual Result
  and Evidence fields are populated and remain consistent with the frozen
  Expected Result. Never rewrite the UAT baseline in Converge.
- Never append a new `[UAT]` task. Reuse the exactly one existing `[UAT]` task
  for a `UAT-*`; a `FAIL` or `BLOCKED` result may justify one or more `[BUILD]`
  remediation tasks, followed by re-execution of that original `[UAT]` task.
  `PENDING` alone reuses the original `[UAT]` task and does not create another
  execution task.
- **Little or no code yet**: treat the entire specified scope as `missing` remaining work
  rather than failing, and reuse the original unchecked tasks that already cover it.
- **Nothing remains**: produce zero findings and follow the converged branch in Step 7.

### 5. Assign Severity

- **CRITICAL**: violates a Constitution MUST principle, explicitly binding
  system boundary rule, or a `missing`/`contradicts` gap that
  blocks baseline functionality of a P1 user story.
- **HIGH**: a `missing` or `partial` gap on a core functional requirement or acceptance
  criterion, or a material system/subsystem/component responsibility or
  boundary gap.
- **MEDIUM**: a `partial` gap on a secondary requirement, or an `unrequested` addition with
  unclear justification.
- **LOW**: minor partial gaps, polish, or low-risk `unrequested` additions.

### 6. Present the In-Session Findings Summary

Before appending anything, output a compact, severity-graded summary (no file writes yet):

## Convergence Findings

| ID | Gap Type | Severity | Source | Evidence | Disposition | Remaining Work |
|----|----------|----------|--------|----------|-------------|----------------|
| F1 | missing  | HIGH     | Constitution CMP-007 | Example: component responsibility overlaps another boundary | append_build | Restore the declared component boundary |
| F2 | partial  | HIGH     | UAT-001 | Existing scenario is still unchecked | reuse_task | Execute T042 |

**Summary metrics:**

- Requirements / acceptance criteria checked
- Prototype anchors and UAT outcomes checked
- Constitution principles and boundary IDs checked, by ID class
  (`SYS`, `SUB`, `CMP`), or "skipped — template/no repository architecture"
- Findings by gap type (missing / partial / contradicts / unrequested)
- Findings by severity
- Findings by disposition (append_build / reuse_task)

### 7. Append Convergence Tasks (or report converged)

Before writing, resolve every finding against the existing task map:

- Reuse an existing unchecked task when its exact source references and
  observable completion condition already cover the remediation. Do not append
  a duplicate.
- Reuse the exactly one existing `[UAT]` task for UAT execution or re-execution.
- Confirm that no unresolved authority conflict remains; never convert one into
  guessed implementation work.
- Group uncovered findings into the smallest set of independently deliverable
  `[BUILD]` work packages. Multiple exact source references may share one task
  only when one observable `Done when` condition demonstrably closes every
  referenced finding; repeated symptoms MUST NOT become duplicate tasks.
- Append only `append_build` findings. A prior task with a checked state does not
  satisfy the finding when present-state evidence proves that the obligation
  remains unmet.

**If at least one `append_build` finding remains** (`tasks_appended` outcome):

Append to the **end** of `tasks.md`, per the append contract:

1. Scan all existing task IDs; let `M` be the maximum. Determine the next phase number `N`
   (highest existing phase + 1).
2. Write a single new section header `## Phase N: Convergence`.
3. Emit one checklist item per distinct uncovered remediation, ordered
   CRITICAL/HIGH first, assigning zero-padded IDs
   `T{M+1:03d}, T{M+2:03d}, …`:

   ```markdown
   - [ ] T042 [BUILD] <imperative description> | Refs: <source-ref> | Depends: none or task IDs | Done when: <observable condition> (<gap-type>)
   ```

   `<source-ref>` traces the task to its origin: e.g. `FR-003`, `SC-002`,
   `US1/AC2`, `proto:account-form`, `UAT-001`, `Constitution II`,
   or `Constitution CMP-007`.

   `<gap-type>` is one of `missing`, `partial`, `contradicts`, `unrequested`.

   Constitution-violation tasks MUST be emitted first and described as
   `CRITICAL`.
4. All appended Convergence tasks MUST use `[BUILD]`. Do not create another
   `[UAT]` task for an existing `UAT-*`. Complete the corrective `[BUILD]`
   task first, then re-execute the original `[UAT]` task as a separate next
   action. Describe the authoritative outcome and evidence, not a guessed
   refactoring technique, file path, framework, or internal design.
5. Never reuse or renumber existing IDs. If a prior Convergence phase exists, add a new,
   separately-numbered one below it — do not touch the old one.

**If findings remain but every one is a `reuse_task` and no append is needed**
(`existing_tasks_pending` outcome):

- Do **not** modify `tasks.md` and do not create an empty Convergence phase.
- List the exact existing task IDs to execute or re-execute, including the
  original `[UAT]` task IDs when re-execution is required.
- Report why no new task was appended.

**If there are no actionable findings** (`converged` outcome):

- Do **not** modify `tasks.md` at all — no empty phase header.
- Report: **"Converged - the implementation satisfies the frozen Specify
  contract, Constitution authority, and tasks."**
- Include the summary counts of what was checked.

### 8. Provide Next Actions (Handoff)

- On `tasks_appended`: state how many tasks were appended under which phase, and
  recommend running `__SPECKIT_COMMAND_IMPLEMENT__` to complete them and
  re-execute the original mapped `[UAT]` tasks after corrective work. Note that
  a follow-up converge run will find fewer or no remaining items.
- On `existing_tasks_pending`: recommend running
  `__SPECKIT_COMMAND_IMPLEMENT__` only for the exact existing task IDs listed;
  do not ask the user to run a duplicate Convergence task.
- On `converged`: recommend proceeding to review / opening a PR. No further implement pass
  is needed for this feature's specified scope and Constitution principles and boundaries.

### 9. Check for extension hooks

After producing the result, check if `.specify/extensions.yml` exists in the project root.

- If it exists, read it and look for entries under the `hooks.after_converge` key
- If the YAML cannot be parsed or is invalid, do not skip silently: tell the user that `.specify/extensions.yml` could not be read (include the parser error) and that no hooks were checked, including any mandatory (`optional: false`) hooks registered there, then continue normally
- Filter out hooks where `enabled` is explicitly `false`. Treat hooks without an `enabled` field as enabled by default.
- For each remaining hook, do **not** attempt to interpret or evaluate hook `condition` expressions:
  - If the hook has no `condition` field, or it is null/empty, treat the hook as executable
  - If the hook defines a non-empty `condition`, skip the hook and leave condition evaluation to the HookExecutor implementation
- Report the convergence outcome (`converged`, `tasks_appended`, or
  `existing_tasks_pending`) in-session before listing
  any hooks, so users can decide whether to run optional follow-up commands.
- For each executable hook, output the following based on its `optional` flag:
  - **Optional hook** (`optional: true`):

    ```text
    ## Extension Hooks

    **Optional Hook**: {extension}
    Command: `/{command}`
    Description: {description}

    Prompt: {prompt}
    To execute: `/{command}`
    ```

  - **Mandatory hook** (`optional: false`):

    ```text
    ## Extension Hooks

    **Automatic Hook**: {extension}
    Executing: `/{command}`
    EXECUTE_COMMAND: {command}
    ```
    After emitting the block above you MUST actually invoke the hook and wait for it to finish before continuing. Run it the same way you would run the command yourself in this agent/session (the invocation may differ from the literal `{command}` id shown above, e.g. a skills-mode agent runs it as `/skill:speckit-...` or `$speckit-...`). Emitting the block alone does not run the hook.

- If no hooks are registered or `.specify/extensions.yml` does not exist, skip silently

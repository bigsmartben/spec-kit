---
description: Analyze consistency and complete traceability across the frozen Specify contract and tasks.md.
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

**Check for extension hooks (before analysis)**:
- Check if `.specify/extensions.yml` exists in the project root.
- If it exists, read it and look for entries under the `hooks.before_analyze` key
- If the YAML cannot be parsed or is invalid, do not skip silently: tell the user that `.specify/extensions.yml` could not be read (include the parser error) and that no hooks were checked, including any mandatory (`optional: false`) hooks registered there, then continue normally
- Filter out hooks where `enabled` is explicitly `false`. Treat hooks without an `enabled` field as enabled by default.
- For each remaining hook, do **not** attempt to interpret or evaluate hook `condition` expressions:
  - If the hook has no `condition` field, or it is null/empty, treat the hook as executable
  - If the hook defines a non-empty `condition`, skip the hook and leave condition evaluation to the HookExecutor implementation
- For each executable hook, output the following based on its `optional` flag:
  - **Optional hook** (`optional: true`):
    ```
    ## Extension Hooks

    **Optional Pre-Hook**: {extension}
    Command: `/{command}`
    Description: {description}

    Prompt: {prompt}
    To execute: `/{command}`
    ```
  - **Mandatory hook** (`optional: false`):
    ```
    ## Extension Hooks

    **Automatic Pre-Hook**: {extension}
    Executing: `/{command}`
    EXECUTE_COMMAND: {command}

    Wait for the result of the hook command before proceeding to the Goal.
    ```
    After emitting the block above you MUST actually invoke the hook and wait for it to finish before continuing. Run it the same way you would run the command yourself in this agent/session (the invocation may differ from the literal `{command}` id shown above, e.g. a skills-mode agent runs it as `/skill:speckit-...` or `$speckit-...`). Emitting the block alone does not run the hook.
- If no hooks are registered or `.specify/extensions.yml` does not exist, skip silently

## Goal

Identify inconsistencies, duplications, ambiguities, and traceability gaps across
`spec.md`, `prototype.html`, `quickstart.md`, and `tasks.md` before
implementation. This command MUST run only after `__SPECKIT_COMMAND_TASKS__`
has successfully produced a complete `tasks.md`.

## Operating Constraints

**STRICTLY READ-ONLY**: Do **not** modify any files. Output a structured analysis report. Offer an optional remediation plan (user must explicitly approve before any follow-up editing commands would be invoked manually).

**Constitution Authority**: The project constitution (`/memory/constitution.md`)
is **non-negotiable** within this analysis scope. Constitution conflicts are
automatically CRITICAL and require adjustment at the owner phase: Specify for
contract conflicts or Task for work-package gaps. Never dilute, reinterpret, or
silently ignore a principle.

## Execution Steps

### 1. Initialize Analysis Context

Run `{SCRIPT}` once from repo root and parse JSON for FEATURE_DIR and AVAILABLE_DOCS. Derive absolute paths:

- SPEC = FEATURE_DIR/spec.md
- PROTOTYPE = FEATURE_DIR/prototype.html
- QUICKSTART = FEATURE_DIR/quickstart.md
- TASKS = FEATURE_DIR/tasks.md

Abort with an error message if any required file is missing (instruct the user to run missing prerequisite command).
For single quotes in args like "I'm Groot", use escape syntax: e.g 'I'\''m Groot' (or double-quote if possible: "I'm Groot").

### 2. Load Artifacts (Progressive Disclosure)

Load only the minimal necessary context from each artifact:

**From spec.md:**

- Overview/Context
- Functional Requirements
- Success Criteria (measurable outcomes — e.g., performance, security, availability, user success, business impact)
- User Stories
- Edge Cases (if present)

**From prototype.html:**

- Every `data-spec-ref`
- Visible layout, component/state behavior, interaction order, and responsive
  contract

**From quickstart.md:**

- Every `UAT-*`
- Preconditions, ordered actions, expected result, requirement references,
  prototype references, and execution state

**From tasks.md:**

- Task IDs
- Task type (`[BUILD]` or `[UAT]`)
- Descriptions
- Phase grouping
- Parallel markers [P]
- Exact source references, dependencies, completion conditions, and coverage
  matrix

**From constitution:**

- Load `/memory/constitution.md` for principle validation

### 3. Build Semantic Models

Create internal representations (do not include raw artifacts in output):

- **Requirements inventory**: Record every `FR-*` and `SC-*` by its stable ID.
  Do not discard post-launch or business-facing success criteria; Task must map
  each to observable work or measurement-readiness without weakening it.
- **User story/action inventory**: Discrete user actions with acceptance criteria
- **Prototype-anchor inventory**: Every unique `data-spec-ref` and source
  location
- **UAT inventory**: Every `UAT-*`, its expected result, source references, and
  exact prototype references
- **Task coverage mapping**: Use explicit IDs and anchors, never keyword
  inference, to map tasks to source obligations
- **Task-shape mapping**: One type per task; `[UAT]` tasks reference exactly one
  UAT and `[BUILD]` tasks define requirement-level outcomes, dependencies, and
  completion evidence
- **Constitution rule set**: Extract principle names and MUST/SHOULD normative statements

### 4. Detection Passes (Token-Efficient Analysis)

Focus on high-signal findings. Limit to 50 findings total; aggregate remainder in overflow summary.

#### A. Duplication Detection

- Identify near-duplicate requirements
- Mark lower-quality phrasing for consolidation

#### B. Ambiguity Detection

- Flag vague adjectives (fast, scalable, secure, intuitive, robust) lacking measurable criteria
- Flag unresolved placeholders (TODO, TKTK, ???, `<placeholder>`, etc.)

#### C. Underspecification

- Requirements with verbs but missing object or measurable outcome
- User stories missing acceptance criteria alignment
- Tasks that add technical choices, file paths, frameworks, components, or
  APIs not owned by the frozen contract
- Task completion conditions that are not observable or contradict the source

#### D. Constitution Alignment

- Any requirement, prototype/UAT contract, or task conflicting with a MUST principle
- Missing mandated sections or quality gates from constitution

#### E. Coverage Gaps

- Every FR or SC with zero associated tasks
- Every prototype anchor with zero associated `[BUILD]` task
- Every UAT with no `[BUILD]` coverage or without exactly one `[UAT]` task
- Tasks with no explicit source mapping
- UAT task references that do not resolve to one exact UAT ID
- Missing or incomplete source coverage matrix rows

#### F. Inconsistency

- Terminology drift (same concept named differently across files)
- Prototype or UAT references that contradict `spec.md`
- UAT actions/expected results that reference nonexistent or duplicate
  prototype anchors
- Task dependencies or ordering that contradict priority/acceptance dependencies
- `[UAT]` tasks that rewrite UAT expectations, source references, or execution
  fields
- `[BUILD]` tasks that preselect architecture, stack, libraries, APIs, or
  file/component paths

### 5. Severity Assignment

Use this heuristic to prioritize findings:

- **CRITICAL**: Violates a constitution MUST, missing frozen contract artifact,
  unresolved/contradictory UAT-to-source mapping, or requirement with zero
  coverage that blocks P1 behavior
- **HIGH**: Duplicate/conflicting requirement, ambiguous security/performance
  attribute, uncovered FR/SC/anchor/UAT, invalid `[UAT]` cardinality, or a task
  that changes the frozen acceptance contract; retain CRITICAL escalation above
- **MEDIUM**: Terminology drift, missing non-functional task coverage, underspecified edge case
- **LOW**: Style/wording improvements, minor redundancy not affecting execution order

### 6. Produce Compact Analysis Report

Output a Markdown report (no file writes) with the following structure:

## Specification Analysis Report

| ID | Category | Severity | Location(s) | Summary | Recommendation |
|----|----------|----------|-------------|---------|----------------|
| A1 | Duplication | HIGH | spec.md:L120-134 | Two similar requirements ... | Merge phrasing; keep clearer version |

(Add one row per finding; generate stable IDs prefixed by category initial.)

**Coverage Summary Table:**

| Requirement Key | Has Task? | Task IDs | Notes |
|-----------------|-----------|----------|-------|

**Prototype and UAT Coverage:**

| Source ID / Anchor | Kind | Task IDs | Coverage / Consistency Notes |
|--------------------|------|----------|------------------------------|

Use exact source locations and task IDs. Keyword inference never counts as
coverage.

**Constitution Alignment Issues:** (if any)

**Unmapped Tasks:** (if any)

**Metrics:**

- Total FR/SC Requirements
- Total Prototype Anchors
- Total UATs
- Total Tasks by type
- Coverage % for each source class
- Ambiguity Count
- Duplication Count
- Critical Issues Count

### 7. Provide Next Actions

At end of report, output a concise Next Actions block:

- If CRITICAL issues exist: Recommend resolving before `__SPECKIT_COMMAND_IMPLEMENT__`
- If only LOW/MEDIUM: User may proceed, but provide improvement suggestions
- Provide explicit command suggestions: e.g., "Run
  __SPECKIT_COMMAND_SPECIFY__ to repair the source contract" or "Run
  __SPECKIT_COMMAND_TASKS__ to regenerate work packages after source repair."

### 8. Offer Remediation

Ask the user: "Would you like me to suggest concrete remediation edits for the top N issues?" (Do NOT apply them automatically.)

### 9. Check for extension hooks

After reporting, check if `.specify/extensions.yml` exists in the project root.
- If it exists, read it and look for entries under the `hooks.after_analyze` key
- If the YAML cannot be parsed or is invalid, do not skip silently: tell the user that `.specify/extensions.yml` could not be read (include the parser error) and that no hooks were checked, including any mandatory (`optional: false`) hooks registered there, then continue normally
- Filter out hooks where `enabled` is explicitly `false`. Treat hooks without an `enabled` field as enabled by default.
- For each remaining hook, do **not** attempt to interpret or evaluate hook `condition` expressions:
  - If the hook has no `condition` field, or it is null/empty, treat the hook as executable
  - If the hook defines a non-empty `condition`, skip the hook and leave condition evaluation to the HookExecutor implementation
- For each executable hook, output the following based on its `optional` flag:
  - **Optional hook** (`optional: true`):
    ```
    ## Extension Hooks

    **Optional Hook**: {extension}
    Command: `/{command}`
    Description: {description}

    Prompt: {prompt}
    To execute: `/{command}`
    ```
  - **Mandatory hook** (`optional: false`):
    ```
    ## Extension Hooks

    **Automatic Hook**: {extension}
    Executing: `/{command}`
    EXECUTE_COMMAND: {command}
    ```
    After emitting the block above you MUST actually invoke the hook and wait for it to finish before continuing. Run it the same way you would run the command yourself in this agent/session (the invocation may differ from the literal `{command}` id shown above, e.g. a skills-mode agent runs it as `/skill:speckit-...` or `$speckit-...`). Emitting the block alone does not run the hook.
- If no hooks are registered or `.specify/extensions.yml` does not exist, skip silently

## Operating Principles

### Context Efficiency

- **Minimal high-signal tokens**: Focus on actionable findings, not exhaustive documentation
- **Progressive disclosure**: Load artifacts incrementally; don't dump all content into analysis
- **Token-efficient output**: Limit findings table to 50 rows; summarize overflow
- **Deterministic results**: Rerunning without changes should produce consistent IDs and counts

### Analysis Guidelines

- **NEVER modify files** (this is read-only analysis)
- **NEVER hallucinate missing sections** (if absent, report them accurately)
- **Prioritize constitution violations** (these are always CRITICAL)
- **Use examples over exhaustive rules** (cite specific instances, not generic patterns)
- **Report zero issues gracefully** (emit success report with coverage statistics)

## Context

{ARGS}

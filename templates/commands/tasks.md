---
description: Translate the frozen Specify contract into traceable, dependency-ordered work packages in tasks.md.
handoffs:
  - label: Analyze For Consistency
    agent: speckit.analyze
    prompt: Run a project analysis for consistency
    send: true
  - label: Implement Project
    agent: speckit.implement
    prompt: Start the implementation in phases
    send: true
scripts:
  sh: scripts/bash/setup-tasks.sh --json
  ps: scripts/powershell/setup-tasks.ps1 -Json
  py: scripts/python/setup_tasks.py --json
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Pre-Execution Checks

**Check for extension hooks (before tasks generation)**:
- Check if `.specify/extensions.yml` exists in the project root.
- If it exists, read it and look for entries under the `hooks.before_tasks` key
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

    Wait for the result of the hook command before proceeding to the Outline.
    ```
    After emitting the block above you MUST actually invoke the hook and wait for it to finish before continuing. Run it the same way you would run the command yourself in this agent/session (the invocation may differ from the literal `{command}` id shown above, e.g. a skills-mode agent runs it as `/skill:speckit-...` or `$speckit-...`). Emitting the block alone does not run the hook.
- If no hooks are registered or `.specify/extensions.yml` does not exist, skip silently

## Outline

1. **Setup**: Run `{SCRIPT}` from the repository root and parse `FEATURE_DIR`,
   `FEATURE_SPEC`, `PROTOTYPE`, `QUICKSTART`, `AVAILABLE_DOCS`,
   `TASKS_TEMPLATE_CONTENT`, and `TASKS_TEMPLATE`. Contract and template paths
   must be absolute when provided. For arguments containing single quotes, use
   safe shell quoting.

2. **Load the frozen Specify contract**:
   - **Required**: `spec.md` for user stories, priorities, `FR-*`, `SC-*`,
     acceptance scenarios, scope boundaries, and assumptions
   - **Required**: `prototype.html` for exact `data-spec-ref` anchors and the
     visible behavior/state contract
   - **Required**: `quickstart.md` for `UAT-*`, ordered user actions, expected
     results, requirement references, prototype references, and pending state
   - **IF EXISTS**: `/memory/constitution.md` for governing constraints
   - Treat `spec.md`, `prototype.html`, and `quickstart.md` as read-only
     authority. Task may create or replace only `tasks.md`; it must never
     "repair" the source contract or alter UAT expectations.
   - Do not read or infer a technical plan from `plan.md`, data-model documents,
     API contracts, research files, the current implementation, or unstated
     repository conventions. Implement owns those decisions.

3. **Validate before generation**:
   - Build source inventories for every user story, `FR-*`, `SC-*`, unique
     `data-spec-ref`, and `UAT-*`.
   - Reject duplicate or malformed source IDs/anchors.
   - Resolve every prototype and requirement reference used by a UAT to an
     exact source item.
   - Detect contradictions among a UAT's expected result, referenced
     requirement(s), and referenced prototype behavior. Report exact source
     locations.
   - Confirm every user-visible story has at least one UAT and every material
     visible contract item has a stable prototype anchor.
   - If any source is missing, empty, contradictory, unresolved, or cannot be
     translated into an independently verifiable obligation, **STOP**. Do not
     invent or repair requirements, do not reinterpret the prototype/UAT, and
     do not write a new or partial `tasks.md`. Explain what must return to
     `__SPECKIT_COMMAND_SPECIFY__` or `__SPECKIT_COMMAND_CLARIFY__`.

4. **Derive work packages**:
   - Translate user stories and requirements into independently deliverable
     outcomes in priority order.
   - Use `[BUILD]` tasks for delivery obligations and `[UAT]` tasks for one
     explicit execution task per `UAT-*`.
   - State requirement-level outcomes, source references, dependencies, and
     observable completion conditions.
   - Never choose or imply a language, framework, library, database, protocol,
     architecture, class/component boundary, API shape, test framework, or
     repository file path.
   - Use only the frozen contract's terminology. Do not copy long source
     passages when a stable ID or exact prototype anchor is sufficient.

5. **Generate dependencies and parallel boundaries**:
   - Express dependencies by task ID.
   - Mark `[P]` only when the work packages have no incomplete dependency and
     can produce independent acceptance evidence.
   - Group shared obligations only when one deliverable can satisfy multiple
     stories without changing the priority/delivery boundary.
   - Every `[UAT]` task must depend on all `[BUILD]` tasks needed to make its
     scenario observable and must identify the matching `UAT-*`.

6. **Prove complete coverage before writing**:
   - Every `FR-*` maps to at least one `[BUILD]` task.
   - Every `SC-*` maps to at least one task with an observable completion
     condition. When an outcome cannot be fully observed until operation,
     create the requirement-preserving measurement/readiness work package;
     do not weaken or invent the criterion.
   - Every `data-spec-ref` maps to at least one `[BUILD]` task.
   - Every `UAT-*` maps to at least one `[BUILD]` task and exactly one `[UAT]`
     execution task.
   - Every task maps to at least one explicit user story, requirement,
     prototype anchor, or UAT source reference.
   - Reconcile the generated coverage matrix with the inventories. Any gap is a
     generation failure and must be corrected or reported as a blocking source
     defect before returning.

7. **Write `tasks.md`**: Use `TASKS_TEMPLATE_CONTENT` as the structure. For
   compatibility with older setup scripts that omit that field, read
   `TASKS_TEMPLATE` instead. The generated file must contain:
   - A frozen-contract summary identifying all three inputs
   - One delivery phase per priority-ordered user story
   - Cross-story requirement/completion phases when required
   - A UAT execution phase with one task per `UAT-*`
   - Strict checklist items following Task Generation Rules
   - A source coverage matrix for every required inventory class
   - Dependencies and parallel opportunities expressed at work-package level
   - An incremental delivery strategy based on completed observable outcomes

## Mandatory Post-Execution Hooks

**You MUST complete this section before reporting completion to the user.**

Check if `.specify/extensions.yml` exists in the project root.
- If it does not exist, or no hooks are registered under `hooks.after_tasks`, skip to the Completion Report.
- If it exists, read it and look for entries under the `hooks.after_tasks` key.
- If the YAML cannot be parsed or is invalid, do not skip silently: tell the user that `.specify/extensions.yml` could not be read (include the parser error) and that no hooks were checked, including any mandatory (`optional: false`) hooks registered there, then continue to the Completion Report.
- Filter out hooks where `enabled` is explicitly `false`. Treat hooks without an `enabled` field as enabled by default.
- For each remaining hook, do **not** attempt to interpret or evaluate hook `condition` expressions:
  - If the hook has no `condition` field, or it is null/empty, treat the hook as executable
  - If the hook defines a non-empty `condition`, skip the hook and leave condition evaluation to the HookExecutor implementation
- For each executable hook, output the following based on its `optional` flag:
  - **Mandatory hook** (`optional: false`) — **You MUST emit `EXECUTE_COMMAND:` for each mandatory hook**:
    ```
    ## Extension Hooks

    **Automatic Hook**: {extension}
    Executing: `/{command}`
    EXECUTE_COMMAND: {command}
    ```
    After emitting the block above you MUST actually invoke the hook and wait for it to finish before continuing. Run it the same way you would run the command yourself in this agent/session (the invocation may differ from the literal `{command}` id shown above, e.g. a skills-mode agent runs it as `/skill:speckit-...` or `$speckit-...`). Emitting the block alone does not run the hook.
  - **Optional hook** (`optional: true`):
    ```
    ## Extension Hooks

    **Optional Hook**: {extension}
    Command: `/{command}`
    Description: {description}

    Prompt: {prompt}
    To execute: `/{command}`
    ```

## Completion Report

Output path to generated tasks.md and summary:
- Total task count
- Task count by `[BUILD]` and `[UAT]`
- Task count per user story and cross-story work
- Parallel opportunities identified
- Coverage totals for FR, SC, prototype anchors, and UAT
- Suggested MVP scope (typically just User Story 1)
- Blockers: state "none" only after preflight and coverage validation pass
- Format validation: confirm every task has a checkbox, ID, type, source
  references, dependencies, and an observable completion condition

Context for task generation: {ARGS}

The generated `tasks.md` must be sufficient for Implement to choose the
technical approach without any Plan artifact. It must remain faithful to the
frozen Specify contract and not copy entire source documents into task prose.

## Task Generation Rules

**CRITICAL**: Organize delivery by user story so each priority can produce an
independently verifiable increment.

**Tests are OPTIONAL except for UAT**: Generate additional deterministic test work
only when the frozen contract requests it or the user explicitly requests a
development approach. Every UAT is mandatory and always has an explicit `[UAT]`
task.

### Checklist Format (REQUIRED)

Every task MUST strictly follow this format:

```text
- [ ] T001 [P] [US1] [BUILD] Requirement-level outcome | Refs: FR-001, proto:page-main, UAT-001 | Depends: none | Done when: observable condition
```

**Format Components**:

1. **Checkbox**: ALWAYS start with `- [ ]` (markdown checkbox)
2. **Task ID**: Sequential number (T001, T002, T003...) in execution order
3. **[P] marker**: Include ONLY when the work package has no incomplete
   dependency and can deliver independent acceptance evidence. Do not infer
   this from file paths because Implement chooses the paths.
4. **[Story] label**: REQUIRED for user story phase tasks only
   - Format: [US1], [US2], [US3], etc. (maps to user stories from spec.md)
   - User Story phases: MUST have story label
   - Cross-story requirements: NO story label unless one story owns the work
   - UAT tasks: include the story label when the UAT belongs to one story
5. **Type**: Exactly one of:
   - `[BUILD]` for a deliverable or verification-enabling obligation
   - `[UAT]` for executing one frozen `UAT-*` scenario
6. **Description**: Clear requirement-level deliverable without implementation
   choices.
7. **Refs**: One or more exact IDs/anchors, such as `FR-001`, `SC-002`,
   `US1`, `proto:<data-spec-ref>`, or `UAT-003`.
8. **Depends**: `none` or an explicit comma-separated list of task IDs.
9. **Done when**: Observable acceptance condition derived from the frozen
   contract. A `[UAT]` task is complete only when the matching quickstart entry
   records `Status: PASS`, actual result, evidence, and deviation. These
   completion conditions are the acceptance evidence Implement must produce;
   they are not technical instructions.

No task may introduce a framework, library, architecture, protocol, API,
component boundary, or repository file path. If a task needs such a choice,
describe the outcome and leave the technical decision to Implement. Implement
owns the paths and all other realization choices.

**Examples**:

- CORRECT: `- [ ] T001 [US1] [BUILD] Deliver the account creation outcome | Refs: FR-001, proto:account-form | Depends: none | Done when: the specified account flow and visible states are available`
- CORRECT: `- [ ] T014 [US1] [UAT] Execute UAT-001 for account creation | Refs: UAT-001, FR-001, proto:account-form | Depends: T001 | Done when: quickstart.md records Status: PASS, actual result, evidence, and deviation`
- WRONG: `- [ ] T001 [BUILD] Use React and create src/components/Form.tsx` (technology/path lock-in)
- WRONG: `- [ ] T001 Deliver account creation` (missing type, references, dependencies, and completion condition)
- WRONG: `- [ ] T014 [UAT] Run acceptance tests` (missing UAT ID and exact contract references)

### Task Organization

1. **From User Stories (`spec.md`) - PRIMARY ORGANIZATION**:
   - Each user story (P1, P2, P3...) gets its own phase
   - Each phase names its story goal and observable independent outcome
   - Add only the work required for that frozen story boundary
   - Keep story dependencies explicit and minimal; shared work must not blur
     ownership or alter delivery priority

2. **From Functional Requirements (`FR-*`) and Success Criteria (`SC-*`)**:
   - Map every item to at least one `[BUILD]` or cross-story task
   - Preserve identifiers and measurable outcomes
   - Do not convert a user/business outcome into an assumed implementation
     architecture or monitoring system

3. **From the Prototype (`data-spec-ref`)**:
   - Map every stable anchor to at least one `[BUILD]` task
   - Group anchors only when they form one observable contract outcome
   - Never soften the prototype as inspiration or redesign a state in Task

4. **From the UAT baseline (`UAT-*`)**:
   - Map every UAT to the `[BUILD]` work needed to make the scenario executable
   - Emit exactly one `[UAT]` task per UAT ID in the UAT execution phase
   - Preserve user/role, preconditions, ordered actions, expected result, and
     exact references; Implement executes them later
   - A `[UAT]` task never changes expected results or source references

### Phase Structure

- **Phase 1+**: User Stories in priority order (P1, P2, P3...)
  - `[BUILD]` work needed for each independently verifiable increment
  - Optional requested test-enabling work when it is part of the contract
  - Completion checkpoint expressed as an observable outcome
- **Cross-Story Phase**: Only for explicit requirements shared across stories
- **Final UAT Phase**: Exactly one `[UAT]` task per `UAT-*`
- **No implicit Setup/Foundation phase**: If the contract requires a shared
  prerequisite, identify the actual requirement/SC and task it in a requirement
  phase. Implement creates technical setup as needed.

## Done When

- [ ] `tasks.md` generated from the frozen contract with all task metadata
- [ ] Every FR, SC, prototype anchor, and UAT appears in the coverage matrix
- [ ] Every UAT has exactly one `[UAT]` execution task
- [ ] No framework, architecture, library, API, component, or file-path choice
      was introduced by Task
- [ ] Every missing/conflicting/unresolvable contract condition blocked
      generation instead of being designed around
- [ ] Extension hooks dispatched or skipped according to the rules in Mandatory Post-Execution Hooks above
- [ ] Completion reported with counts, coverage, blockers, and MVP scope

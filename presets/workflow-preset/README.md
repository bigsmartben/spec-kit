# Workflow Preset

This Spec Kit community preset combines behavior-first specification, design-aware planning, and scoped change governance.

It wraps `/speckit.specify`, `/speckit.clarify`, `/speckit.checklist`, `/speckit.constitution`, `/speckit.plan`, `/speckit.tasks`, and `/speckit.analyze` with BDD, NFR, and UI/UX specification readiness gates, Change Scope Granularity and Architecture SSOT governance, Phase 0 behavior projection, optional design artifacts for internal object design and service sequencing, and task-time validation strategy derivation. It replaces `/speckit.implement` with the upstream standard implementation workflow.

## Goal

`workflow-preset` turns a Spec Kit feature from a single broad implementation prompt into a staged workflow with stable design context and explicit worker boundaries.

The preset has four goals:

- Make BDD/NFR/UI/UX readiness explicit before planning by checking `spec.md` for observable, verifiable behavior, explicit non-functional requirement declarations, and complete UI/UX requirements when relevant.
- Project accepted requirements into BDD, UIF intent, and fixture intent drafts during `/speckit.plan` Phase 0.
- Preserve richer planning intent so downstream tasks and implementation do not lose object design, service-flow, or validation decisions.
- Keep implementation scope explicit by applying Change Scope Granularity from planning onward: M + U boundaries are locked before execution maps them to concrete paths and O-level edits.
- Execute the complete `tasks.md` plan in order, with its defined dependencies, validation checkpoints, and completion tracking.

## Problem Addressed

Large Spec Kit features can overload the implementation phase. A single `/speckit.implement` run may need to keep product requirements, technical decisions, domain details, interface contracts, object design, service flows, test strategy, task ordering, and current code changes in one prompt. As the context grows, the agent is more likely to drift from earlier design decisions, blur task boundaries, read unrelated documents, update the wrong files, or mark tasks complete without enough validation evidence.

`workflow-preset` reduces that failure mode in three complementary ways:

- Requirement enhancement keeps product requirements in `spec.md` and gates planning with a BDD/NFR/UI/UX specification readiness checklist.
- Scope governance keeps broad repository context from becoming implementation scope by applying the R/M/U/O model once planning begins.
- Plan enhancement projects accepted behavior drafts, then gives object design, service sequencing, and validation intent stable homes before tasks are generated.

The intent is not to add ceremony to simple features. The intent is to preserve reasoning quality by making requirements, planning, tasks, and validation explicit before execution.

## Capabilities

Requirement capabilities:

- Wraps `/speckit.specify` so it produces or updates `spec.md` only.
- Wraps `/speckit.clarify` so it resolves requirement ambiguity in `spec.md` only.
- Adds a wrapping `spec-template` that owns the stable source-agnostic `UI/UX Specification` shape.
- Assigns stable `UX-###` IDs to journeys, navigation, feedback, and usability outcomes and `UI-###` IDs to surfaces, states, responsive behavior, accessibility, content, and observable visual outcomes.
- Wraps `/speckit.checklist` to add `checklists/behavior-testability.md` as a BDD readiness gate, NFR readiness gate, and UI/UX specification readiness gate.
- Checks user stories, acceptance criteria, Given/When/Then readiness, roles, permissions, states, data, validation, boundary, exception, state_conflict behavior, and non-functional requirements directly from `spec.md`.
- Adds a Case Coverage Matrix with one row per story or capability case type so positive, negative, boundary, permission, validation, and state_conflict cases are marked Required, Not Applicable, or Unknown before planning.
- Adds a UI/UX Coverage Matrix that keeps requirement Applicability (`Required | Not Applicable | Unknown`) separate from specification Readiness (`Ready | Blocked`).
- Checks experience goals, navigation, interaction feedback, UI states, responsive behavior, accessibility, content, visual hierarchy, and objective acceptance criteria before planning.
- Requires NFR dimensions to be marked Required, Not Applicable, or Unknown in product language before planning.
- Blocks planning when readiness gaps or missing or unverifiable NFR assumptions must return to `/speckit.clarify` or `/speckit.specify`.

Governance capabilities:

- Wraps `/speckit.constitution` and the constitution template with Change Scope Granularity and Architecture SSOT governance.
- Defines the fixed R/M/U/O model: R is Repository / Workspace, M is Module / Capability, U is Unit / Design Object, and O is Operation / Detail. These letters must not be renamed or expanded with alternate nouns.
- Blocks constitution writes when a generated draft changes the fixed R/M/U/O mapping.
- Routes architecture decisions, domain facts, object design, flows, and interface contracts to architecture SSOT artifacts instead of embedding concrete implementation content in ratified constitution principles.
- Requires planning to lock M + U before execution maps units to concrete paths.
- Treats unresolved U -> path mapping as a context gap instead of widening execution to repository-wide or broad module scope.

Planning capabilities:

- Wraps `/speckit.plan` to run Phase 0 preflight, Phase 0 behavior projection, and optional/contextual design artifacts when useful.
- Requires the BDD, NFR, and UI/UX specification readiness gates to pass before planning.
- Treats Phase 0 preflight failures as report-only/no-write failures.
- Writes `behavior/bdd.draft.feature`, `behavior/behavior-scenarios.draft.json`, `behavior/uif.intent.json`, and `behavior/data-fixtures.intent.json` during Phase 0 behavior projection.
- Projects Required case coverage into `behavior/behavior-scenarios.draft.json` instead of allowing Required cases to disappear behind positive-only drafts.
- Consumes Phase 0 behavior drafts and must formalize them into `contracts/bdd/`, `contracts/uif/`, and `contracts/behavior/` when the BDD, NFR, and UI/UX specification readiness gates have passed.
- Requires failure scenarios in `contracts/behavior/` to carry an explicit trigger, case kind, error code, failure feedback, and state invariant, rollback, or compensation assertion reference.
- Records `N/A or blocker` and `case_coverage_blockers` when behavior drafts cannot be formalized.
- Keeps `plan.md` focused on technical decisions and navigation.
- Adds plan-template navigation to the core plan output.
- Stores internal object design in `class-diagram.md`.
- Stores service, command, event, async, retry, rollback, and failure-path flows in `contracts/sequences.md`.
- Records validation decisions in `research.md` and validation paths in `quickstart.md`.
- When UI/UX requirements are in scope, `research.md` records planning decisions, contracts formalize accepted interaction and state constraints, and `contracts/sequences.md` records UI state flow only when it affects cross-boundary sequencing.
- Keeps product requirements in `spec.md`, domain facts in `data-model.md`, interface schemas in `contracts/`, and executable validation guidance in `quickstart.md`.

Task generation capabilities:

- Wraps `/speckit.tasks` so task generation can consume the design artifacts.
- Uses formal BDD, UIF, and behavior contracts to derive test-first fixture, acceptance test, implementation, and verification tasks.
- Treats missing Required failure behavior scenarios as blockers instead of generating complete-looking happy-path-only tasks.
- Performs test strategy derivation from BDD contracts, Expected UIF contracts, behavior contracts, interface contracts, `research.md`, and `quickstart.md` without writing a separate strategy artifact.
- Derives UI setup, implementation, accessibility, and acceptance tasks from Required and Ready `UI-###` / `UX-###` requirements.
- Preserves UI/UX requirement IDs through implementation and acceptance tasks.
- Uses design artifacts to derive implementation, integration, orchestration, failure-handling, and validation tasks.
- Adds Final Code Review tasks for boundary, interface contract, UI/UX, data side-effect, behavior contract, and sequence consistency scopes when applicable.
- Preserves the existing checklist format and user-story organization.

Analysis capabilities:

- Wraps `/speckit.analyze` to check vertical consistency from `spec.md` through BDD/UIF intent, formal contracts, and `tasks.md`.
- Checks that user stories, Given/When/Then steps, UIF API calls, behavior contracts, tasks, and quickstart validation paths remain traceable.
- Adds case coverage checks so Required case types remain traceable through behavior drafts, formal contracts, tasks, and quickstart validation paths.
- Treats UIF as a requirement behavior projection, formalized during planning as Expected UIF contracts.

Implementation capabilities:

- Replaces `/speckit.implement` with the upstream standard command.
- Runs prerequisite checks, reports checklist status, and loads the complete implementation context.
- Executes `tasks.md` phase by phase, honors dependencies and TDD ordering, and validates each phase.
- Runs configured pre- and post-implementation extension hooks.
- Marks completed tasks in `tasks.md` and reports completion status.

## Workflow

1. `/speckit.constitution` preserves Change Scope Granularity and Architecture SSOT governance when the project constitution is created or updated.
2. `/speckit.specify` keeps the core requirements output in `spec.md`.
3. `/speckit.clarify` resolves requirement ambiguity in `spec.md`.
4. `/speckit.checklist` checks BDD, NFR, and UI/UX specification readiness directly from `spec.md` and blocks planning when readiness gaps remain.
5. `/speckit.plan` applies Change Scope Granularity, runs Phase 0 preflight, performs Phase 0 behavior projection, formalizes behavior drafts into contracts, and adds design artifacts when they help implementation.
6. `/speckit.tasks` reads the core plan outputs, optional design artifacts, behavior contracts, interface contracts, `research.md`, and `quickstart.md`, then produces executable tasks with inline test level, data strategy, UI/UX requirement IDs, acceptance criteria, and evidence requirements.
7. `/speckit.analyze` checks vertical consistency across requirements, behavior drafts, contracts, and tasks.
8. `/speckit.implement` runs the task plan, marks completed tasks, validates the resulting implementation, and reports closeout status.

## Non-Goals

- It does not make every feature produce large diagrams or test matrices.
- It does not move product requirements out of `spec.md`.
- It does not move API or message schemas out of `contracts/`.
- It does not replace `data-model.md`, `research.md`, or `quickstart.md`.
- It does not infer UIF from built code; UIF remains a requirement and planning contract.
- It does not provide a Python orchestration script, workflow shell runner, or integration adapter layer.

## Install

Release install:

```bash
specify preset add workflow-preset --from https://github.com/bigsmartben/spec-kit-workflow-preset/releases/download/v1.3.12/spec-kit-workflow-preset-v1.3.12.zip
```

Local development install:

```bash
specify preset add --dev /path/to/workflow-preset
```

## Usage

Run the behavior-first workflow:

```text
/speckit.constitution
/speckit.specify
/speckit.clarify
/speckit.checklist
/speckit.plan
/speckit.tasks
/speckit.analyze
```

### Source-Agnostic UI/UX Requirements

`workflow-preset` accepts explicit product text and confirmed product decisions without depending on how those requirements were collected.

```text
confirmed product requirements -> /speckit.specify -> UI/UX Specification in spec.md
```

UI/UX Applicability uses `Required`, `Not Applicable`, or `Unknown`. The checklist evaluates specification Readiness separately as `Ready` or `Blocked`. Unresolved product decisions return to `/speckit.clarify`.

Then run the standard implementation workflow:

```text
/speckit.implement
```

## Files Written

The core governance and planning workflow still owns its normal artifacts:

- `.specify/memory/constitution.md`
- `specs/<feature>/plan.md`
- `specs/<feature>/research.md`
- `specs/<feature>/data-model.md`
- `specs/<feature>/contracts/`
- `specs/<feature>/quickstart.md`
- `specs/<feature>/tasks.md`

This preset adds checklist artifacts:

- `specs/<feature>/checklists/behavior-testability.md`

This preset adds Phase 0 behavior artifacts:

- `specs/<feature>/behavior/bdd.draft.feature`
- `specs/<feature>/behavior/behavior-scenarios.draft.json`
- `specs/<feature>/behavior/uif.intent.json`
- `specs/<feature>/behavior/data-fixtures.intent.json`

This preset adds planning-phase formal behavior contracts:

- `specs/<feature>/contracts/bdd/`
- `specs/<feature>/contracts/uif/`
- `specs/<feature>/contracts/behavior/`

This preset adds optional/contextual planning artifacts:

- `specs/<feature>/class-diagram.md`
- `specs/<feature>/contracts/sequences.md`

Contract files packaged by the preset:

- `schemas/speckit.behavior.scenarios.draft.v1.schema.json`
- `schemas/speckit.behavior.uif.intent.v1.schema.json`
- `schemas/speckit.behavior.data-fixtures.intent.v1.schema.json`
- `schemas/speckit.behavior.uif.expected.v1.schema.json`
- `schemas/speckit.behavior.scenario-instances.v1.schema.json`
- `schemas/speckit.behavior.data-fixtures.v1.schema.json`
- `schemas/speckit.behavior.assertions.v1.schema.json`

Governance templates packaged by the preset:

- `templates/constitution-template.md`
- `templates/spec-template.md`

## Artifact Roles

`checklists/behavior-testability.md` is the BDD, NFR, and UI/UX specification readiness gate. It checks `spec.md` before planning so behavior, NFRs, and source-agnostic UI/UX requirements are ready for behavior projection and planning. Its Case Coverage Matrix uses one row per story or capability case type; rows mark Required, Not Applicable, or Unknown, cite source sections, and list Blocker IDs while Scenario IDs remain a `/speckit.plan` output. Its UI/UX Coverage Matrix keeps Applicability separate from Readiness and checks states, responsive behavior, accessibility, content, visual hierarchy, and acceptance criteria. Missing Required case coverage, Unknown applicability, Blocked UI/UX readiness, or missing NFR criteria blocks planning when it affects downstream behavior projection or design.

`behavior/bdd.draft.feature` captures Phase 0 behavior projection in readable Given/When/Then form. `behavior/behavior-scenarios.draft.json`, `behavior/uif.intent.json`, and `behavior/data-fixtures.intent.json` make the same draft behavior machine-readable enough for planning formalization.

`contracts/bdd/`, `contracts/uif/`, and `contracts/behavior/` contain planning-phase formal behavior contracts. They are generated from Phase 0 drafts after planning has resolved fixture strategy, data model, interface contracts, and validation paths, unless planning records `N/A or blocker` for missing planning input. `contracts/behavior/scenario-instances.json` carries `case_coverage_blockers` for Required cases that cannot be formalized. Failure scenarios must be structured enough to constrain implementation, including error code, failure feedback, and state invariant, rollback, or compensation assertion references.

`class-diagram.md` captures internal implementation object structure: classes, interfaces, abstract types, composition, dependencies, references, and design pattern participants. It is the object design map that helps implementation preserve boundaries between services, adapters, repositories, strategies, factories, controllers, coordinators, and extension points.

`contracts/sequences.md` captures service-call, command, event, external-system, retry, rollback, compensation, async, and failure-path sequencing. It is the flow design map that helps implementation preserve call order, service boundaries, async behavior, idempotency, compensation, and error propagation. Sequences always live at this path, even when there are no other contract files.

For UI/UX planning, `research.md` records implementation decisions needed by accepted `UI-###` and `UX-###` requirements. Contracts formalize observable interaction, feedback, state, responsive, and accessibility constraints. `contracts/sequences.md` records UI state flow only when it affects cross-boundary sequencing, async results, retries, rollback, compensation, or error propagation.

Test strategy derivation happens during `/speckit.tasks`. The command derives unit, contract, integration, and end-to-end validation work from BDD contracts, Expected UIF contracts, behavior contracts, interface contracts, `research.md`, and `quickstart.md`, then writes the strategy inline on the relevant `tasks.md` checklist items. It also defines UI implementation, non-visual acceptance, contract validation, data-side-effect validation, integration/e2e validation, and scope-aware code review tasks in `tasks.md`; `/speckit.implement` executes those tasks without inventing validation strategy, changing requirements, updating contracts, or widening scope.

See `commands/speckit.implement.md` for the standard implementation workflow.

## Safety Boundaries

Planning artifacts are optional/contextual. Simple features may produce concise files or `N/A` sections with concrete reasons. The command should avoid large placeholder artifacts and should not move product requirements out of `spec.md`, interface schemas out of `contracts/`, validation decisions out of `research.md`, or quick validation instructions out of `quickstart.md`.

## Development

Runtime requirements:

- Spec Kit CLI `>=0.8.10.dev0`
- An agent environment capable of running the standard `/speckit.implement` workflow

Development and release tooling:

- Python 3.10 or newer
- PyYAML and jsonschema for contract tests
- Git
- GitHub CLI `gh` for repository and release publishing

Install development test dependencies:

```bash
python3 -m pip install -r requirements-dev.txt
```

Run the contract tests:

```bash
python3 -m unittest tests/test_preset_contract.py
```

## Preset CI Boundary

This repository owns preset artifact health:

- run `tests/test_preset_contract.py`;
- build `spec-kit-workflow-preset-v<version>.zip`;
- smoke-install this checkout on an Ubuntu GitHub runner with a `specify` CLI built from `bigsmartben/spec-kit`;
- publish or confirm the release artifact for a tag or manual release run;
- create or update a `workflow-preset-release-v<version>` integration PR in `bigsmartben/spec-kit` on tag releases or manual runs with `create_integration_pr=true`.

Manual release runs default to the next patch version when `version` is omitted. For example, a `preset.yml` version of `1.3.12` defaults to release version `1.3.13`.

The integration PR step requires a repository secret named `SPEC_KIT_FORK_PR_TOKEN` with permission to push branches and open pull requests in `bigsmartben/spec-kit`. If a tag release or manual `create_integration_pr=true` run reaches that step without the secret, the workflow fails fast instead of skipping integration PR creation.

This repository owns the release artifact and the fork integration PR. It does not open pull requests to `github/spec-kit`. The `bigsmartben/spec-kit` fork owns downstream integration validation, core workflow fixes, catalog resolver checks, and any later community catalog PR flow.

Optional local CLI sanity check:

```bash
specify preset add --dev /path/to/workflow-preset
specify preset info workflow-preset
specify preset remove workflow-preset
```

Release install smoke validation is intentionally owned by GitHub Actions, not by a local WSL environment.

After tagging a release, validate archive installation:

```bash
specify preset add workflow-preset --from https://github.com/bigsmartben/spec-kit-workflow-preset/releases/download/v1.3.12/spec-kit-workflow-preset-v1.3.12.zip
```

## Source Rationale

See `2026-05-15-plan-design-artifacts-proposal.md` for the design artifact proposal that this preset incorporates.

---
description: Wrap task generation with optional design artifact awareness.
strategy: wrap
---

## Derivation Boundary

Preserve the planned `M + U` scope in task text when deriving implementation, validation, and integration tasks. Do not generate execution metadata or write-path fields.

## Task-Derivation Subagents

Follow cross-agent protocol profile: `speckit.tasks.stage_local_derivation`.

Use a context-reduced multi-subagent derivation model when the command runtime supports subagents. This is a derivation-time partitioning rule only: do not create implementation transfer artifacts, manifests, context digests, execution modes, persistent orchestration files, schemas, scripts, or task write-path metadata. If subagents are unavailable, the Tasks Core Agent must apply the same scoped-read and output-contract rules sequentially.

The Tasks Core Agent coordinates task derivation, partitions source inputs by user story or review scope, and assembles the final `tasks.md`. It must consume only subagent drafts, structured summaries, blocker reports, and the current command inputs. It must not consume full conversation history as task-derivation context.

Use these subagent roles only for task derivation:

- Tasks Core Agent: orchestration, scope partitioning, blocker aggregation, deduplication, final checklist assembly, and preservation of the planned `M + U` scope.
- Story Task Agent: story-local implementation, fixture, validation, evidence, and integration task chains.
- Contract Validation Agent: interface contract, BDD, behavior contract, UIF `api_call`, sequence, external-system, data side-effect, retry, rollback, and quickstart validation task derivation.
- UI/UX Task Agent: UI/UX readiness, UIF `user_event`, UI implementation, accessibility, responsive behavior, state coverage, acceptance, and requirement traceability.
- Review Task Agent: final review tasks for `boundary`, `interface_contract`, `ui_ux`, `data_side_effect`, `behavior_contract`, and `sequence_consistency` scopes.

Every subagent payload must declare:

- `assigned_scope`: the user story, contract group, UI/UX requirement group, review scope, or blocker-check scope assigned to the subagent.
- `allowed_read_paths`: the exact files, directories, or glob groups the subagent may read.
- `allowed_sections`: the exact headings, table names, contract IDs, scenario IDs, UI/UX requirement IDs, or summary slices the subagent may inspect within allowed files.
- `output_contract`: the required draft shape, including task candidates, evidence refs, source refs, blockers, and `context_gaps`.

Subagents must not read full `spec.md`, `plan.md`, `research.md`, or `contracts/` trees unless the payload explicitly lists those files or directories in `allowed_read_paths` and lists the permitted headings, IDs, or contract groups in `allowed_sections`. Prefer scoped excerpts, extracted summaries, contract IDs, scenario IDs, and readiness rows over whole-file reads. A subagent that needs context outside its declared payload must return a `context_gaps` entry instead of widening its own reads.

`context_gaps` is a blocking output whenever required derivation context is absent, contradictory, outside the subagent payload, or only available by reading an unapproved full artifact. Each gap must include blocker code `TASK_DERIVATION_CONTEXT_GAP`, the missing or inaccessible source, the affected assigned scope, the task type that cannot be derived, and the reason the existing payload is insufficient. The Tasks Core Agent must surface unresolved `context_gaps` as blockers and must not generate complete-looking tasks for the affected scope.

Keep task granularity compact. Split checklist items only when the validation level, implementation owner, dependency order, evidence source, or review scope differs. Otherwise keep one scenario as a single fixture -> test or validation -> implementation -> evidence chain.

## Planning Input Taxonomy

If any listed file exists under FEATURE_DIR, task generation must consume it as an input:

- `class-diagram.md`: internal object structure, dependency direction, and design pattern participants.
- `contracts/sequences.md`: service, command, event, async, retry, rollback, and failure-path flows.
- `research.md`: selected validation level, fixture strategy, external-system execution mode, and error-branch validation decisions.
- `quickstart.md`: executable validation paths and evidence collection guidance.
- `spec.md` UI/UX requirements: accepted `UI-###` and `UX-###` requirements for journeys, navigation, feedback, states, responsive behavior, accessibility, content, and observable visual outcomes.
- `checklists/behavior-testability.md` UI/UX Specification Readiness: Applicability, Readiness, coverage, and Blocking Items for each UI/UX requirement.
- `contracts/bdd/`: formal BDD acceptance contracts.
- `contracts/uif/`: Expected UIF interaction contracts.
- `contracts/behavior/`: formal scenario instance, fixture, and assertion contracts.
- `contracts/`: interface schemas and API/message contracts used by validation tasks.

Use these inputs to derive implementation, integration, orchestration, failure-handling, and non-visual validation tasks. For behavior contracts, derive test-first task chains in user-story order: fixture setup, BDD/E2E or contract test, implementation, and verification evidence. Keep task output in the existing checklist format and user-story organization.

`/speckit.tasks` owns implementation, validation, and review task definition in `tasks.md`. Task derivation must not invent validation strategy, add lifecycle roles, change requirements, update contracts, or widen scope.

Use UI/UX Specification Readiness as the only UI/UX planning-readiness source. Generate UI/UX tasks only for rows whose Applicability is `Required` and Readiness is `Ready`. Do not generate implementation, validation, acceptance, or review tasks for `Not Applicable`, `Unknown`, or `Blocked` rows. Route `Unknown` and `Blocked` requirement rows back to `/speckit.clarify` or `/speckit.checklist`. `/speckit.tasks` only decomposes UI/UX specifications that passed the readiness gate.

Missing Required case coverage is a coverage blocker, not silently skipped work. If `checklists/behavior-testability.md` marks a case type Required but the matching BDD or behavior contract is absent and no `Not Applicable` rationale or `case_coverage_blockers` entry exists, report the missing case instead of generating a complete-looking task list.

## Validation Task Derivation

Do not create or require a standalone test strategy artifact. Instead, derive the validation level, fixture strategy, external-system execution mode, and inline evidence requirement while generating `tasks.md`.

Use this validation level taxonomy for each scenario or validation path:

- `unit`: pure domain rules, data validation, state transitions, or behavior assertions that do not cross a process, network, database, browser, or external-system boundary.
- `contract`: API, message, schema, BDD request/response, or Expected UIF contract step with type `api_call` that can be verified at an interface boundary.
- `integration`: service orchestration, persistence, async events, retries, rollback, callbacks, external sandbox calls, or `contracts/sequences.md` failure branches.
- `e2e`: user-visible journeys that require frontend/CLI interaction plus backend behavior, multiple services, or final feedback verification.

Use this fixture strategy and external-system execution mode taxonomy:

- Attach fixture IDs and setup strategies from `contracts/behavior/` when they exist.
- Use fixture intent only when it is recorded in `research.md` or formal `contracts/behavior/` blocker notes for a scenario documented as `Not Applicable` or blocked by `case_coverage_blockers`.
- Use mock, sandbox, or real-system decisions from `research.md`.
- External-system validation must use mock or sandbox unless `research.md` and `quickstart.md` explicitly require a real-system validation path.
- Add a separate validation task for high-risk, non-functional, external-system, async, retry, rollback, permission, validation, state_conflict, negative, boundary, or error behavior.

Evidence binding: every generated test or validation task must name at least one relevant BDD scenario, behavior assertion, API contract, UIF path, UI/UX requirement ID, quickstart validation path, or command output.

Generate explicit validation tasks from this validation task taxonomy instead of relying on final code review for primary validation responsibility:

- `contract_validation`: contract ref, implementation surface, validation command, and evidence; report a blocker when mapping is unavailable.
- `ui_acceptance`: user-facing UIF path or BDD scenario, applicable `UI-###` or `UX-###` requirement ID, required state and viewport coverage, accessibility behavior, quickstart validation path, and observable evidence.
- `data_side_effect_validation`: affected entity or state transition, expected write behavior, rollback/compensation/retry/migration/backfill or invariant assertion when applicable, and validation evidence.
- `integration_e2e_validation`: user-visible journey or cross-boundary flow, scenario/assertion refs, external-system strategy, quickstart validation path, and captured command output.

Task shape: checklist item plus story tag, validation level, strategy when applicable, and evidence refs.

Behavior traceability must be explicit:

- For each BehaviorScenarioInstance, create a fixture task, BDD/E2E or contract test task, implementation task, and verification evidence task unless the scenario is documented as `Not Applicable` or blocked by `case_coverage_blockers`.
- For each BehaviorScenarioInstance with type `negative`, `boundary`, `permission`, `validation`, or `state_conflict`, derive fixture, contract or BDD test, implementation, and verification evidence tasks. For failure outcomes, name the expected error code, failure feedback, and state invariant, rollback, or compensation assertion when present.
- For each Expected UIF contract step with type `user_event`, create the frontend, CLI, or interaction task that emits or handles the event.
- For each Expected UIF contract step with type `api_call`, create the backend/API or contract task that provides the declared method and path.
- For each quickstart validation path, create a validation task that can collect evidence for the relevant scenario IDs and assertions.

Use only this UI/UX task taxonomy when a user story includes `contracts/uif/` or ready `UI-###` / `UX-###` requirements:

- Maintain story-local task granularity: `ui_setup` -> `ui_implementation` -> `ui_accessibility` and/or `ui_acceptance` as needed. Do not create a separate UI/UX lifecycle phase.
- `ui_setup`: prepare UI fixtures, viewport configuration, test data, and user-visible content required by accepted requirements.
- `ui_implementation`: implement accepted journeys, navigation, states, interaction feedback, responsive behavior, content, and observable visual outcomes.
- `ui_accessibility`: implement and validate keyboard, focus, semantics, contrast, announcement, and error behavior required by accepted requirements.
- `ui_acceptance`: verify the relevant UIF path, BDD scenario, or UI/UX requirement through user action, feedback, page state, responsive behavior, accessibility behavior, and visible result.
- UI/UX tasks must name the applicable `UI-###` or `UX-###` requirement ID, concrete implementation surface, test or fixture path, and validation path when derivable; otherwise report a readiness blocker instead of generating an ambiguous task.
- UI acceptance tasks must verify the same UIF path, UI/UX requirement ID, scenario ID, or quickstart validation path as the implementation task, including required state, viewport, and accessibility coverage.

Generate UI/UX tasks only from Required and Ready checklist rows. Not Applicable rows create no tasks; Unknown or Blocked rows remain upstream requirement-quality blockers.

When an implementation task depends on `contracts/`, include a paired contract validation task that names the contract ref, expected implementation surface, validation command or quickstart path, and evidence requirement. Do not instruct implementers to modify `spec.md`, `contracts/`, readiness checklists, or UI/UX Specification Readiness to make implementation pass; report a blocker if implementation requires requirement or contract changes.

When persistence, migrations, external writes, retries, rollback, or compensation are in scope, include a data-side-effect validation task before final code review. The task must name the affected entity, expected mutation behavior, invariant or rollback/compensation assertion, and evidence source.

## Final Code Review

When generating `tasks.md`, append the final phase after user-story tasks in the same checklist format. Use this final review scope taxonomy when applicable: `boundary`, `interface_contract`, `ui_ux`, `data_side_effect`, `behavior_contract`, and `sequence_consistency`. Checked sources include `class-diagram.md`, `contracts/sequences.md`, `contracts/`, `contracts/uif/`, `research.md`, `quickstart.md`, `spec.md` UI/UX requirements, and `checklists/behavior-testability.md` UI/UX Specification Readiness, plus data side-effect review and real-system e2e environment readiness.

Code review task text must require review of runtime database writes and other persistent data changes, including field-level update/delete behavior, bulk writes, soft deletes, ORM whole-object saves, migrations/backfills, retries, rollback/compensation, and external-system writes. Do not generate field-level mutation allowlists or pre-implementation data-write gates in normal tasks.

Code review task text must require boundary review: task scope stays within planned `M + U`, implementation matches the referenced contracts, validation evidence covers quickstart or contract paths, and no implementation task changed `spec.md`, `contracts/`, readiness checklists, or UI/UX Specification Readiness to make execution pass.

Code review task text may require UI consistency review when UI/UX acceptance was in scope. The review must reconcile implemented journeys, navigation, states, viewport behavior, accessibility behavior, content, and visible results with accepted `UI-###` and `UX-###` requirements, readiness rows, and UIF paths.

Review evidence binding: final review tasks must name concrete review scope, source artifacts, implementation surfaces, and evidence refs. If review scope exposes drift from the plan, sequences, contracts, or data-side-effect expectations, express it as review evidence, bounded repair permission, or a blocker. If resolving the drift would require changing `spec.md`, `contracts/`, `research.md`, `quickstart.md`, readiness checklists, or planning artifacts, record a blocker instead of treating the change as implementation work. Real-system e2e environment gaps must remain visible as evidence gaps instead of treated as passing evidence.

{CORE_TEMPLATE}

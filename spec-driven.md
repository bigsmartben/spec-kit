# Specification-Driven Development (SDD)

## The Power Inversion

For decades, code has been king. Specifications served code—they were
scaffolding built and often discarded once the "real work" of coding began.
PRDs guided implementation, design documents explained it, and diagrams
visualized it, but the implementation remained the authoritative description
of what the product did.

Spec-Driven Development (SDD) inverts that relationship. The product contract
describes intended behavior before implementation begins, and code must satisfy
that contract. Spec Kit makes the boundary explicit with three first-party
stages:

**Specify → Task → Implement**

Specify freezes `spec.md`, `prototype.html`, and the pending UAT baseline in
`quickstart.md`. Task converts that frozen contract into independently
deliverable, requirement-level work packages. Implement chooses the technology
and architecture, executes the work, and records UAT results.

There is no required core `plan.md` stage. Technical decisions belong to
Implement, after the observable behavior and acceptance contract are stable.
Historical or user-owned `plan.md` files remain valid project records, but they
are not inputs required by Task and are not created or updated by the current
core workflow.

The result is not a claim that code can be generated mechanically from a prose
file. It is a disciplined handoff: product intent is frozen first, work is
packaged without invention, and implementation owns the decisions that depend
on the actual codebase and technology.

## The SDD Workflow in Practice

The workflow begins with an idea, often vague or incomplete. Through dialogue
and review, Specify turns that idea into a complete, testable product contract.
It does not select a production stack, component structure, or source layout.

### Specify: Freeze the observable contract

Specify creates and validates three artifacts together:

- `spec.md` defines user stories, functional requirements, edge cases, and
  measurable success criteria.
- `prototype.html` is a self-contained, executable construction contract with
  stable `data-spec-ref` anchors for visible layout, interactions, and states.
  Its rendered page contains only product UI and user-facing copy; traceability
  stays in nonvisual attributes and the other Specify artifacts. Specification
  journeys and UAT action order do not become visible navigation unless the
  user-facing requirements explicitly call for it.
  It is evaluated as a production product screen: prototype-only demos, service
  providers, technical settings, and unrelated cross-feature data explanations
  do not appear unless the user-facing contract explicitly requires them.
  The default composition is one coherent current-task screen with clear
  context, current content or input, a primary action, contextual secondary
  actions, and state feedback. Advanced options and explanations are revealed
  progressively rather than presented as a feature tour.
- `quickstart.md` defines pending `UAT-*` scenarios, expected observable
  results, and exact requirement and prototype references.

Every UAT begins as `PENDING`. Specify does not execute the scenario, claim a
result, or supply implementation evidence. Clarification is part of this stage:
when an important behavior is ambiguous, `/speckit.clarify` resolves it and
keeps all three artifacts aligned.

### Task: Package the contract without designing the implementation

Task reads only the frozen Specify contract plus the project constitution. It
does not inspect the source tree, choose dependencies, or use an old `plan.md`
as permission to add implementation details.

Task writes independently deliverable, dependency-ordered work packages in
`tasks.md`. Each package states an observable requirement-level outcome and
references the source contract it fulfills. Packages do not lock a stack,
architecture, framework, file, module, directory, or implementation path.

Before completing, Task verifies complete coverage. At least one package must
map to every:

- `FR-*` functional requirement
- `SC-*` success criterion
- prototype `data-spec-ref`
- `UAT-*` acceptance scenario

If the contract is inconsistent or one of those mappings is missing, Task
blocks and reports the problem to Specify. It does not invent a missing
requirement, prototype state, UAT case, or technical design.

### Implement: Own technical decisions and UAT execution

Implement receives the frozen contract and requirement-level work packages. It
may inspect the codebase, evaluate existing constraints, and choose the stack,
architecture, libraries, interfaces, files, and implementation paths needed to
deliver them.

Implementation includes the UAT work mapped by Task. For every scenario it
executes, Implement updates only these fields in the corresponding
`quickstart.md` entry:

- `Status`
- `Actual Result`
- `Evidence`
- `Deviation`

The UAT identifier, user actions, expected result, requirement references, and
prototype references remain frozen. If execution reveals a product-level
conflict or missing rule, Implement returns it to Specify rather than silently
rewriting the contract. A revised contract must be repackaged by Task before
the dependent work continues.

## Why SDD Matters Now

AI can produce substantial code quickly, but generation without stable role
boundaries makes requirement invention, premature architecture, and
untraceable changes look like progress. SDD gives each stage one clear job.

- **Specify protects product intent.** Technology changes do not quietly rewrite
  expected user behavior.
- **Task protects scope.** Every requirement, prototype anchor, and UAT case has
  a delivery owner before implementation begins.
- **Implement has the necessary flexibility.** It can make technically sound
  choices against the real repository without forcing the Task stage to
  predict files or architecture.
- **UAT evidence stays attached to intent.** Acceptance results link to the
  original expected behavior rather than to an implementation-only test plan.

When requirements change, the contract changes first. Task packages are
regenerated from that contract, and Implement applies new technical choices
while preserving the changed behavior. Technical discoveries that do not alter
intent stay implementation decisions. Product discoveries return to Specify.

## Core Principles

### Frozen contract

`spec.md`, `prototype.html`, and `quickstart.md` are one traceable product
contract. They are frozen as Task's input so missing information cannot be
silently replaced with assumptions about the implementation.

### Observable, executable specification

Requirements need directly observable acceptance scenarios. The self-contained
prototype makes the visible layout and interaction order executable without
assuming a production framework or backend.

### Complete traceability

Task coverage is not optional. Every `FR-*`, `SC-*`, prototype
`data-spec-ref`, and `UAT-*` must have at least one independently deliverable
work package.

### No invention in Task

Task may structure and map agreed requirements, but it cannot add missing
requirements or design the implementation. Conflicts and gaps block back to
Specify.

### Technology-neutral work packages

A work package describes an outcome and its contract references. It does not
commit the team to a language, framework, service boundary, architecture, file,
module, directory, or path.

### Technical ownership in Implement

Implement owns engineering choices and applies the constitution to the real
codebase. Different implementations may satisfy the same frozen contract using
different technologies.

### Evidence at the acceptance boundary

UAT results are persisted with the corresponding acceptance scenario.
Implement may record evidence of execution, but it cannot alter the frozen
expectations to match the code it produced.

## Implementation Approaches

Teams can practice SDD with:

- AI assistants for iterative contract development
- Self-contained prototypes for visible product behavior
- Requirement-level work packages for decomposition and coordination
- Coding agents and conventional engineering tools for implementation
- Automated and manual UAT evidence for acceptance
- Version-control and review systems appropriate to the project

The same frozen contract can support greenfield delivery, iterative
enhancement, or multiple technical explorations. A brownfield implementation
may reuse its existing architecture, but that fact is considered by Implement,
not assumed by Task.

## Streamlining SDD with Commands

### `/speckit.specify`

Specify turns a natural-language feature request into the frozen contract:

1. Creates the feature directory and records the active feature.
2. Writes `spec.md` with testable requirements and measurable success criteria.
3. Writes a self-contained `prototype.html` with stable
   `data-spec-ref` anchors.
4. Writes `quickstart.md` with complete, pending UAT cases.
5. Validates that requirements, prototype anchors, and UAT references agree.

### `/speckit.tasks`

Task consumes only the three Specify artifacts and the constitution:

1. Extracts the requirement, success-criterion, prototype, and UAT identities.
2. Builds independently deliverable requirement-level work packages.
3. Records dependency and parallelism information without fixing file paths.
4. Proves complete FR/SC/prototype/UAT coverage.
5. Blocks inconsistent or incomplete contracts back to Specify.

### `/speckit.implement`

Implement turns the accepted work packages into code and evidence:

1. Inspects the project and chooses the technical approach.
2. Executes packages in dependency order.
3. Applies the constitution and repository conventions.
4. Runs the mapped UAT scenarios.
5. Updates only UAT `Status`, `Actual Result`, `Evidence`, and `Deviation`.

Clarify, checklist, and analyze commands can add review around this core
sequence. They do not transfer ownership away from Specify, Task, or Implement.

## Example: Building a Chat Feature

```text
# Step 1: Freeze the product contract
/speckit.specify Real-time chat with message history and visible user presence

# Step 2: Generate requirement-level, technology-neutral work packages
/speckit.tasks

# Step 3: Choose the implementation and execute the mapped UAT scenarios
/speckit.implement
```

Specify creates the following contract:

```text
specs/003-chat-system/
├── spec.md
├── prototype.html
└── quickstart.md
```

Task adds `tasks.md`. That file contains independently deliverable packages,
complete FR/SC/prototype/UAT mappings, and dependencies, but no chosen stack,
architecture, or source paths.

During Implement, the agent may decide how to provide real-time transport,
history, presence, persistence, and tests. It may create whatever technical
records are useful to the project, but a separate core `plan.md` is neither
required nor read by Task.

## Template-Driven Quality

Templates constrain the model at the point where each stage owns a decision.

### Prevent premature implementation details

The Specify template focuses on user value and observable behavior:

```text
- ✅ Focus on WHAT users need and WHY
- ❌ Do not choose production languages, frameworks, APIs, or file structure
```

### Make prototype intent executable

Every meaningful page, region, component, interaction, and state receives a
stable `data-spec-ref`. The prototype remains self-contained so the visible
contract can be reviewed before production code exists.

### Freeze acceptance before execution

Every UAT captures role, preconditions, ordered actions, expected result,
requirement references, prototype references, and a pending status. Actual
results and evidence are not filled during Specify.

### Reject Task invention

Task templates and generation rules require complete mapping and forbid
technology locking. Missing or contradictory contract content is an error to
return to Specify, not an invitation to improvise.

### Preserve UAT expectations during Implement

Implement may add execution evidence to a UAT entry but may not make the
baseline easier by rewriting actions or expected results after seeing the
implementation.

### Keep work independently deliverable

Dependencies are explicit, and packages are small enough to review and deliver
without requiring Task to predict the entire implementation. A package can
state a user-observable outcome and its acceptance references without naming
source files.

## The Constitutional Foundation

At the heart of Spec Kit is the project constitution: the principles that
govern how the frozen contract is packaged and implemented. Task reads the
constitution for process and governance constraints. Implement applies it to
technical choices and the source tree.

The constitution is not a license to rewrite the product contract. If a
constitutional rule conflicts with a requirement, the conflict is surfaced
for explicit resolution at the owning stage.

### The Nine Articles of Development

The constitution defines nine articles that shape technical delivery.

#### Article I: Library-First Principle

When implementation adds reusable capability, implement it as a clear library
boundary rather than embedding it directly in unrelated application code.
Implement decides the concrete boundary; Task does not preselect a module or
file.

#### Article II: CLI Interface Mandate

Libraries that need a CLI must accept text input, produce text output, and
support a structured format when the constitution requires one.

#### Article III: Test-First Imperative

When the constitution requires test-driven development, Implement writes and
observes the failing test before the corresponding production change.

#### Articles IV, V & VI: Project-Defined Governance

These articles encode project-specific concerns such as security, observability,
versioning, or compatibility. Teams replace placeholders with the
principles that match their system and organization.

#### Articles VII & VIII: Simplicity and Anti-Abstraction

Implement should prefer direct, minimal solutions and justify added
complexity. Task keeps its packages neutral; it does not prescribe the
architecture that simplicity will require.

#### Article IX: Integration-First Testing

Where realistic integration evidence is required, Implement uses real
environments and external boundaries where practical rather than allowing
mocks alone to stand in for product behavior.

### Constitutional Enforcement Across the Three Stages

- **Specify** checks the contract for constraints that affect observable
  behavior.
- **Task** ensures its work packages do not conflict with constitution-level
  process or governance rules and does not invent technical decisions.
- **Implement** makes architecture and code choices consistent with the
  constitution and records UAT evidence.

This division avoids duplicating a frozen constitution snapshot into a
required planning artifact. The constitution remains a live project input, but
its application is owned by the stage making the affected decision.

## The Transformation

SDD is not about replacing developers or automating creativity. It amplifies
human judgment by separating product intent, deliverable packaging, and
technical execution.

Specifications become stable enough to coordinate work without pretending to
predict every implementation detail. Work packages guarantee traceability
without locking technology. Implement owns the engineering choices and leaves
evidence where the acceptance expectations were defined.

The resulting feedback loop is deliberate:

1. Learn something during implementation.
2. Decide whether it changes only the technical approach or the intended
   product behavior.
3. Keep technical choices in Implement when intent is unchanged.
4. Return product-level changes to Specify, then regenerate Task and resume
   implementation.

That boundary is what turns fast generation into a reviewable, evolvable
development process.

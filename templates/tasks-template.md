---
description: "Traceable work-package template for the frozen Specify contract"
---

# Tasks: [FEATURE NAME]

**Input contract**:
- [spec.md](./spec.md)
- [prototype.html](./prototype.html)
- [quickstart.md](./quickstart.md)

**Authority**: Specify defines what must be delivered. Task translates that
frozen contract into independently deliverable, verifiable work. Implement
chooses the technical approach, repository paths, and testing mechanisms.

**Task types**:
- `[BUILD]`: a requirement-level delivery or verification-enabling obligation
- `[UAT]`: execution of one frozen `UAT-*` scenario by Implement

**Format**:

```text
- [ ] T001 [P] [US1] [BUILD] Requirement-level outcome | Refs: FR-001, proto:anchor | Depends: none | Done when: observable condition
```

<!--
  Replace every sample phase and task below.
  Do not create work for technology choices that the frozen contract does not
  make. Do not name frameworks, architectures, libraries, APIs, component
  classes, or file paths. Keep stable IDs and prototype anchors exact.
-->

## Phase 1: User Story 1 - [TITLE] (Priority: P1)

**Goal**: [Observable value delivered by this story]

**Independent Outcome**: [How this increment is verifiable on its own]

- [ ] T001 [US1] [BUILD] [Requirement-level work outcome] | Refs: [US1, FR-###, SC-###, proto:anchor] | Depends: none | Done when: [observable contract condition]
- [ ] T002 [P] [US1] [BUILD] [Additional independent work outcome] | Refs: [FR-###, proto:anchor] | Depends: none | Done when: [observable contract condition]

**Checkpoint**: [User Story 1 is complete as an independently observable increment]

---

## Phase 2: User Story 2 - [TITLE] (Priority: P2)

**Goal**: [Observable value delivered by this story]

**Independent Outcome**: [How this increment is verifiable on its own]

- [ ] T003 [US2] [BUILD] [Requirement-level work outcome] | Refs: [US2, FR-###, SC-###, proto:anchor] | Depends: [task IDs, or none] | Done when: [observable contract condition]

**Checkpoint**: [User Story 2 is complete independently]

---

<!-- Add one phase per additional story in priority order. -->

## Phase [N]: Cross-Story Obligations

**Purpose**: Explicit FR/SC obligations that cannot be owned by one story
without changing the contract.

- [ ] TXXX [BUILD] [Requirement-level cross-story outcome] | Refs: [FR-###, SC-###, proto:anchor] | Depends: [task IDs] | Done when: [observable contract condition]

Remove this phase when no cross-story obligation exists.

---

## Phase [N+1]: UAT Execution

**Purpose**: Execute every frozen user-acceptance scenario and record evidence in
the matching `quickstart.md` entry.

- [ ] TXXX [US1] [UAT] Execute UAT-001: [scenario name] | Refs: UAT-001, [FR-###], proto:[anchor] | Depends: [all required BUILD task IDs] | Done when: quickstart.md records Status: PASS, actual result, evidence, and deviation
- [ ] TXXX [US2] [UAT] Execute UAT-002: [scenario name] | Refs: UAT-002, [FR-###], proto:[anchor] | Depends: [all required BUILD task IDs] | Done when: quickstart.md records Status: PASS, actual result, evidence, and deviation

Implement MUST leave a failed or blocked UAT task unchecked.

---

## Contract Coverage

| Source Kind | Source ID | Task IDs | Coverage Note |
|-------------|-----------|----------|---------------|
| FR | FR-001 | T001 | [How the work satisfies the requirement] |
| SC | SC-001 | T001 | [Observable completion evidence] |
| Prototype | [data-spec-ref] | T001 | [Behavior/state covered] |
| UAT | UAT-001 | T001, T00X | [BUILD and UAT execution coverage] |

Every source item in `spec.md`, `prototype.html`, and `quickstart.md` must have
at least one task mapping. Every UAT must have exactly one `[UAT]` task.

---

## Dependencies & Execution Order

### Phase Dependencies

- [User Story 1]: [none or exact task/phase dependency]
- [User Story 2]: [exact dependency; do not assume all stories are independent]
- Cross-Story Obligations: [exact dependency]
- UAT Execution: Depends on every BUILD task required by each scenario

### Within Each Phase

- List task-ID dependencies explicitly.
- Respect the frozen acceptance scenarios and requirement boundaries.
- Complete observable delivery before its dependent UAT task.
- Mark `[P]` only for independently deliverable work packages.

### Parallel Opportunities

- [Task IDs that can proceed independently]
- [Task IDs that are sequential because they share a contract dependency]

---

## Incremental Delivery

1. Complete the P1 story and its directly dependent UAT tasks.
2. STOP and confirm the frozen acceptance evidence.
3. Complete the next priority story without regressing completed outcomes.
4. Complete shared obligations and remaining UAT tasks.

Implement may choose how to realize the work, but may not use that freedom to
alter the frozen requirements, prototype contract, UAT expectations, or source
references.

## Notes

- `[P]` means independent work packages, not different guessed file paths.
- `[BUILD]` does not prescribe a technical design.
- `[UAT]` executes the exact frozen scenario and updates only its execution
  fields in `quickstart.md`.
- Stop and return to Specify/Clarify for missing, conflicting, or unresolvable
  contract information.

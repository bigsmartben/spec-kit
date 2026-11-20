# [PROJECT_NAME] Constitution
<!-- Example: Spec Constitution, TaskFlow Constitution, etc. -->
<!--
  This is the repository's only generated authority template. Governance rules
  and the repository architecture SSOT are part of the same document so existing
  downstream commands continue to inherit both through constitution.md.
-->

## Core Principles

### [PRINCIPLE_1_NAME]
<!-- Example: I. Library-First -->
[PRINCIPLE_1_DESCRIPTION]
<!-- Example: Every feature starts as a standalone library; Libraries must be self-contained, independently testable, documented; Clear purpose required - no organizational-only libraries -->

### [PRINCIPLE_2_NAME]
<!-- Example: II. CLI Interface -->
[PRINCIPLE_2_DESCRIPTION]
<!-- Example: Every library exposes functionality via CLI; Text in/out protocol: stdin/args -> stdout, errors -> stderr; Support JSON + human-readable formats -->

### [PRINCIPLE_3_NAME]
<!-- Example: III. Test-First (NON-NEGOTIABLE) -->
[PRINCIPLE_3_DESCRIPTION]
<!-- Example: TDD mandatory: Tests written -> User approved -> Tests fail -> Then implement; Red-Green-Refactor cycle strictly enforced -->

### [PRINCIPLE_4_NAME]
<!-- Example: IV. Integration Testing -->
[PRINCIPLE_4_DESCRIPTION]
<!-- Example: Focus areas requiring integration tests: New library contract tests, Contract changes, Inter-service communication, Shared schemas -->

### [PRINCIPLE_5_NAME]
<!-- Example: V. Observability, VI. Versioning & Breaking Changes, VII. Simplicity -->
[PRINCIPLE_5_DESCRIPTION]
<!-- Example: Text I/O ensures debuggability; Structured logging required; Or: MAJOR.MINOR.BUILD format; Or: Start simple, YAGNI principles -->

## [SECTION_2_NAME]
<!-- Example: Security Requirements, Performance Standards, Compliance Constraints, etc. -->

[SECTION_2_CONTENT]
<!--
  Use repository-wide constraints that govern work. Keep concrete component
  ownership, public interfaces, and system sequences in the architecture SSOT
  below rather than duplicating them here.
-->

## [SECTION_3_NAME]
<!-- Example: Development Workflow, Review Process, Quality Gates, etc. -->

[SECTION_3_CONTENT]
<!-- Example: Code review requirements, testing gates, deployment approval process, etc. -->

## Repository Blueprint (Architecture SSOT)

[ARCHITECTURE_AUTHORITY_SCOPE]

<!--
  This section is part of the constitution and is governed by the same version,
  amendment policy, and compliance review. It is the only repository blueprint.
  Feature artifacts reference its stable IDs but do not redefine them.
-->

### 1. System Capability Use Cases

<!-- Repeat for each durable repository-level capability. -->

#### CAP-[CAPABILITY_NUMBER]: [CAPABILITY_NAME]

- **Actor or trigger**: [CAPABILITY_ACTOR]
- **User or business value**: [CAPABILITY_VALUE]
- **Outcome**: [CAPABILITY_OUTCOME]
- **Scope**: [CAPABILITY_SCOPE]
- **Exclusions**: [CAPABILITY_EXCLUSIONS]
- **Evidence**: [CAPABILITY_EVIDENCE]

### 2. System Acceptance Use Cases

<!-- Repeat for the primary happy paths that prove architecture closure. -->

#### ACCEPT-[ACCEPTANCE_NUMBER]: [ACCEPTANCE_NAME]

- **Capability**: CAP-[CAPABILITY_NUMBER]
- **Actor**: [ACCEPTANCE_ACTOR]
- **Preconditions**: [ACCEPTANCE_PRECONDITIONS]
- **Observable path**: [ACCEPTANCE_START] -> [ACCEPTANCE_SUCCESS]
- **Architecture participants**: [ACCEPTANCE_PARTICIPANTS]
- **Evidence source**: [ACCEPTANCE_EVIDENCE]

### 3. Responsibility Boundaries

<!--
  Model the repository as System -> Subsystem -> Component. Assign each mutable
  domain concept one owner and avoid source-file or private-class prescriptions.
-->

#### SYS-[SYSTEM_ID]: [SYSTEM_NAME]

- **Purpose**: [SYSTEM_PURPOSE]
- **Boundary**: [SYSTEM_BOUNDARY]

##### SUB-[SUBSYSTEM_ID]: [SUBSYSTEM_NAME]

- **Responsibility**: [SUBSYSTEM_RESPONSIBILITY]
- **Boundary**: [SUBSYSTEM_BOUNDARY]

###### CMP-[COMPONENT_ID]: [COMPONENT_NAME]

- **Responsibility**: [COMPONENT_RESPONSIBILITY]
- **Owns state and transitions**: [COMPONENT_OWNERSHIP]
- **Depends on**: [COMPONENT_DEPENDENCIES]
- **Dependency direction rule**: [COMPONENT_DEPENDENCY_DIRECTION]
- **Accepts**: [COMPONENT_INPUTS]
- **Produces**: [COMPONENT_OUTPUTS]
- **Collaborates with**: [COMPONENT_COLLABORATORS]
- **Does not own**: [COMPONENT_EXCLUSIONS]

### 4. Component Sequences

<!-- Repeat for each ACCEPT-* happy path. Keep interactions at public boundaries. -->

#### SEQ-[SEQUENCE_NUMBER]: [SEQUENCE_NAME]

- **Acceptance use case**: ACCEPT-[ACCEPTANCE_NUMBER]
- **Participants**: [SEQUENCE_PARTICIPANTS]
- **Successful owner**: CMP-[SUCCESSFUL_COMPONENT_ID]
- **Contracts used**: [SEQUENCE_CONTRACTS]

[SEQUENCE_STEPS]

### 5. Public Contracts

<!--
  This is the only public contract structure. Include only cross-component
  semantics that require long-term stability across feature iterations. Exclude
  feature-private contracts, local interfaces, source details, and internal
  implementations. Feature contracts cite the governing CON-* and may only
  refine it without changing owner, guarantees, compatibility, or failure
  semantics.
-->

#### CON-[CONTRACT_ID]: [CONTRACT_NAME]

- **Version and compatibility**: [CONTRACT_VERSIONING]
- **Long-term stability need**: [CONTRACT_STABILITY_NEED]
- **Authority**: [CONTRACT_AUTHORITY]
- **Owner**: [CONTRACT_OWNER]
- **Allowed consumers**: [CONTRACT_CONSUMERS]
- **Triggering capability**: [CONTRACT_CAPABILITY]
- **Semantics**: [CONTRACT_SEMANTICS]
- **Required fields and types**: [CONTRACT_REQUIRED_FIELDS]
- **Optional fields and types**: [CONTRACT_OPTIONAL_FIELDS]
- **Validation and trust boundary**: [CONTRACT_BOUNDARY_RULES]
- **Success result**: [CONTRACT_SUCCESS]
- **Externally meaningful failures**: [CONTRACT_FAILURES]
- **Ordering, delivery, idempotency, and timeout guarantees**: [CONTRACT_GUARANTEES]
- **Backward compatibility**: [CONTRACT_BACKWARD_COMPATIBILITY]
- **Feature refinement rule**: [CONTRACT_REFINEMENT_RULE]
- **Change and migration procedure**: [CONTRACT_CHANGE_PROCEDURE]
- **Required evidence**: [CONTRACT_EVIDENCE]
- **Affected acceptance paths**: [CONTRACT_ACCEPTANCE_PATHS]

### 6. Architectural Invariants

<!-- Repeat for repository-wide constraints that must survive local design choices. -->

#### INV-[INVARIANT_NUMBER]: [INVARIANT_NAME]

- **Rule**: [INVARIANT_RULE]
- **Rationale**: [INVARIANT_RATIONALE]
- **Affected elements**: [INVARIANT_SCOPE]
- **Evidence**: [INVARIANT_EVIDENCE]
- **Violation consequence**: [INVARIANT_CONSEQUENCE]

### 7. Traceability

| Capability | Acceptance paths | Components | Contracts | Invariants |
| --- | --- | --- | --- | --- |
| [CAPABILITY_TRACE_ROW] | [ACCEPTANCE_TRACE_ROW] | [COMPONENT_TRACE_ROW] | [CONTRACT_TRACE_ROW] | [INVARIANT_TRACE_ROW] |

| Acceptance | Sequences | Participating components | Contracts | Evidence |
| --- | --- | --- | --- | --- |
| [ACCEPTANCE_ID] | [SEQUENCE_IDS] | [PARTICIPATING_COMPONENT_IDS] | [CONTRACT_IDS] | [TRACE_EVIDENCE] |

### 8. Open Architecture Decisions

- **[DECISION_ID]**: [DECISION_DESCRIPTION]
  - **Owner**: [DECISION_OWNER]
  - **Affected authority**: [DECISION_SCOPE]
  - **Resolution condition**: [DECISION_CONDITION]

### Architecture Change Control

[ARCHITECTURE_CHANGE_CONTROL]

<!--
  State that feature artifacts consume stable architecture IDs without
  redefining them, and that contract or invariant changes return through the
  constitution workflow and amend this single document.
-->

## Governance
<!--
  Define amendment, review, versioning, and compliance rules for both the
  principles and the embedded architecture SSOT. Neither section may silently
  override the other; contradictions require an explicit reviewed amendment.
-->

[GOVERNANCE_RULES]
<!--
  Example: All PRs/reviews verify compliance; architecture CON/CMP/INV changes
  use this constitution's amendment process and version; feature artifacts may
  refine but must not redefine repository authority.
-->

**Version**: [CONSTITUTION_VERSION] | **Ratified**: [RATIFICATION_DATE] | **Last Amended**: [LAST_AMENDED_DATE]
<!-- Example: Version: 2.1.1 | Ratified: 2025-06-13 | Last Amended: 2025-07-16 -->

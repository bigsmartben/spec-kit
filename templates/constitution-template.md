# [PROJECT_NAME] Constitution
<!-- Example: Spec Constitution, TaskFlow Constitution, etc. -->
<!--
  This template governs repository-wide principles and work constraints. Its
  architecture section records only the approved system/subsystem/component
  boundary decomposition; product behavior and technical design details belong
  in feature specifications or design artifacts.
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
  Use repository-wide constraints that govern work. Keep system boundary
  decomposition in the architecture section below rather than duplicating it
  here.
-->

## [SECTION_3_NAME]
<!-- Example: Development Workflow, Review Process, Quality Gates, etc. -->

[SECTION_3_CONTENT]
<!-- Example: Code review requirements, testing gates, deployment approval process, etc. -->

## Repository Architecture

[ARCHITECTURE_BOUNDARY_SCOPE]

<!--
  Keep this section limited to the repository's approved system, subsystem,
  and component boundary decomposition. Record purpose, responsibility, and
  boundary only; keep all other behavioral or technical detail in its owning
  feature or design artifact.
-->

### Responsibility Boundaries

<!--
  Model the repository as System -> Subsystem -> Component. Assign each mutable
  domain concept one responsibility boundary and avoid source-file, interface,
  or private-class prescriptions.
-->

#### SYS-[SYSTEM_ID]: [SYSTEM_NAME]

- **Purpose**: [SYSTEM_PURPOSE]
- **Boundary**: [SYSTEM_BOUNDARY]

##### SUB-[SUBSYSTEM_ID]: [SUBSYSTEM_NAME]

- **Responsibility**: [SUBSYSTEM_RESPONSIBILITY]
- **Boundary**: [SUBSYSTEM_BOUNDARY]

###### CMP-[COMPONENT_ID]: [COMPONENT_NAME]

- **Responsibility**: [COMPONENT_RESPONSIBILITY]
- **Boundary**: [COMPONENT_BOUNDARY]

## Governance
<!--
  Define amendment, review, versioning, and compliance rules for both the
  principles and the system boundary map. Behavioral and technical details are
  governed by their own owning artifacts, not by this boundary map.
-->

[GOVERNANCE_RULES]
<!--
  Example: All PRs/reviews verify compliance; SYS/SUB/CMP boundary changes use
  this constitution's amendment process and version; feature artifacts may
  consume the boundary map but must not redefine it.
-->

**Version**: [CONSTITUTION_VERSION] | **Ratified**: [RATIFICATION_DATE] | **Last Amended**: [LAST_AMENDED_DATE]
<!-- Example: Version: 2.1.1 | Ratified: 2025-06-13 | Last Amended: 2025-07-16 -->

# Behavior Testability Checklist

## User Story Readiness
- [ ] Each applicable user story has observable acceptance behavior.
- [ ] Each story identifies the actor or system responsible for the behavior.
- [ ] Each story has enough context to distinguish primary, alternate, and exception behavior when applicable.

## Acceptance Criteria Quality
- [ ] Acceptance criteria are observable and verifiable from `spec.md`.
- [ ] Acceptance criteria avoid implementation-only wording.
- [ ] Business rules include precise success, rejection, validation, permission, boundary, and state_conflict outcomes when applicable.

## Scenario Coverage
- [ ] Primary success behavior is covered.
- [ ] Alternate and exception behavior is covered when applicable.
- [ ] Boundary, permission, validation, and state_conflict behavior is covered when applicable.

## Case Coverage Matrix
For each user story or capability, record one row per story or capability case type. Status: Required|Not Applicable|Unknown.

| Case ID | Story/Capability | Case Type | Status | Source `spec.md` section | Blocking Item ID | Rationale |
| --- | --- | --- | --- | --- | --- | --- |
| CASE-PERMISSION-001 | Example | permission | Required | `spec.md#...` |  | reason |
| CASE-BOUNDARY-001 | Example | boundary | Not Applicable | `spec.md#...` |  | reason |
| CASE-VALIDATION-001 | Example | validation | Unknown | `spec.md#...` | BI-... | missing rule |

- [ ] Required case type must cite the source `spec.md` section.
- [ ] Each row must have a stable Case ID.
- [ ] Scenario IDs and `case_coverage_blockers` are assigned during `/speckit.plan`.
- [ ] Not Applicable requires rationale.
- [ ] Unknown must appear in Blocking Items.

## Given Readiness
- [ ] Required roles and permissions are explicit.
- [ ] Required starting state, entity state, and data are explicit enough for later fixture setup.
- [ ] Required data does not depend on production-only records.

## When Readiness
- [ ] Each trigger is an executable user action, request case, or system trigger.
- [ ] Required inputs, selections, uploads, and submitted values are explicit.

## Then Readiness
- [ ] Each outcome maps to user feedback, business state, error semantics, or assertion intent.
- [ ] Failure outcomes include precise feedback or error semantics.

## Non-Functional Requirement Readiness
- [ ] Performance - Status: Required|Not Applicable|Unknown; requirement or rationale is explicitly declared in `spec.md`.
- [ ] Security and Privacy - Status: Required|Not Applicable|Unknown; requirement or rationale is explicitly declared in `spec.md`.
- [ ] Reliability and Recovery - Status: Required|Not Applicable|Unknown; requirement or rationale is explicitly declared in `spec.md`.
- [ ] Accessibility - Status: Required|Not Applicable|Unknown; requirement or rationale is explicitly declared in `spec.md`.
- [ ] Compliance and Auditability - Status: Required|Not Applicable|Unknown; requirement or rationale is explicitly declared in `spec.md`.
- [ ] Observability - Status: Required|Not Applicable|Unknown; requirement or rationale is explicitly declared in `spec.md`.
- [ ] Compatibility - Status: Required|Not Applicable|Unknown; requirement or rationale is explicitly declared in `spec.md`.
- [ ] Data Lifecycle - Status: Required|Not Applicable|Unknown; requirement or rationale is explicitly declared in `spec.md`.
- [ ] Cost and Operational Constraints - Status: Required|Not Applicable|Unknown; requirement or rationale is explicitly declared in `spec.md`.
- [ ] Required NFR entries have verifiable product-level criteria without prescribing architecture.
- [ ] Unknown NFR entries that affect downstream design are listed as blocking items.

## UI/UX Specification Readiness

- [ ] Apply this section when `spec.md` marks UI/UX Applicability as Required or Unknown.
- [ ] UI/UX Applicability is declared as `Required`, `Not Applicable`, or `Unknown`.
- [ ] Not Applicable includes a concrete product-level rationale.
- [ ] Unknown applicability appears in Blocking Items when it affects downstream planning.
- [ ] Every applicable requirement has a stable `UI-###` or `UX-###` ID.
- [ ] Required UI/UX requirements describe observable user outcomes rather than implementation details.
- [ ] Experience goals and critical journeys are explicit.
- [ ] Information architecture and navigation outcomes are explicit when applicable.
- [ ] Interaction feedback, validation behavior, and recovery outcomes are explicit.
- [ ] Required default, loading, empty, error, disabled, success, hover, and focus states are explicit.
- [ ] Responsive reflow, scrolling, safe-area, viewport, and long-content behavior are explicit.
- [ ] Keyboard, focus, semantics, contrast, announcements, and error accessibility behavior are explicit.
- [ ] Required copy, visual hierarchy, typography, color use, iconography, imagery, and formatting are explicit.
- [ ] Every Required UI/UX requirement has an objective acceptance criterion.

## UI/UX Coverage Matrix

| Requirement ID | Source `spec.md` Section | Applicability | Readiness | States Covered | Responsive Coverage | Accessibility Coverage | Blocking Item ID |
| --- | --- | --- | --- | --- | --- | --- | --- |
| UI-001 | `spec.md#...` | Required | Ready|Blocked | default, error | mobile, desktop | keyboard, announcement | BI-... or none |

- [ ] Applicability uses only `Required`, `Not Applicable`, or `Unknown`.
- [ ] Readiness uses only `Ready` or `Blocked`.
- [ ] Applicability and Readiness are evaluated independently.
- [ ] Every Required row cites its source `spec.md` section.
- [ ] Missing observable requirement text, required states, responsive behavior, accessibility behavior, content rules, or acceptance criteria sets Readiness to Blocked and lists a Blocking Item ID.
- [ ] Unknown applicability sets Readiness to Blocked when the unresolved decision prevents planning.
- [ ] Not Applicable rows include rationale and do not create implementation work.
- [ ] UI/UX Coverage Matrix is the only UI/UX specification-readiness matrix.

## Gate Status
Gate Status: PASS|BLOCKED
Blocking Items:
- none

---
schema_version: "1.0"
artifact: "user-acceptance-baseline"
baseline_status: "PENDING"
---

# User Acceptance Baseline: [FEATURE NAME]

**Feature**: [Link to spec.md]

**Prototype**: [Link to prototype.html]

**Created**: [DATE]

## Contract

This document freezes the user-observable acceptance expectations defined by
`__SPECKIT_COMMAND_SPECIFY__`. Every item starts as `PENDING`. The Specify
command must not prefill an actual result, evidence, deviation, or pass/fail
decision.

Replace the sample item below with the complete set of `UAT-*` scenarios.
Remove this sample item rather than leaving it as an unfilled artifact.

## Acceptance Baseline

### UAT-001 - [SHORT SCENARIO NAME]

- **User / Role**: [Who performs the scenario]
- **Preconditions**: [Required account, data, permissions, or starting state]
- **User Actions**:
  1. [Observable user action]
  2. [Next observable user action]
- **Expected Result**:
  - [Technology-agnostic, directly observable result]
  - [Visible state or business outcome]
- **Requirement Refs**: [US-###, FR-###, SC-###]
- **Prototype Refs**: [Exact `data-spec-ref` values]
- **Status**: PENDING
- **Actual Result**: Not executed
- **Evidence**: Not provided
- **Deviation**: Not evaluated

## Traceability Summary

| UAT ID | Requirement Refs | Prototype Refs | Status |
|--------|------------------|----------------|--------|
| UAT-001 | [US-### / FR-### / SC-###] | [data-spec-ref] | PENDING |

## Baseline Validation

- [ ] Every UAT ID is unique and follows `UAT-###` format
- [ ] Every user story with user-visible behavior has at least one UAT
- [ ] Every UAT maps to at least one requirement and one existing prototype reference
- [ ] Every prototype reference resolves exactly to a `data-spec-ref`
- [ ] Expected results are observable and do not assume a specific implementation
- [ ] Every status is `PENDING`
- [ ] Actual result, evidence, and deviation contain no execution claim

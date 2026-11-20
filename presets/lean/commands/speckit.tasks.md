---
description: Convert the frozen feature contract into traceable requirement-level work packages.
---

## User Input

```text
$ARGUMENTS
```

## Outline

1. Read `.specify/feature.json` to get the feature directory path.

2. **Treat the Specify artifacts as a frozen contract** and read:
   - `.specify/memory/constitution.md`
   - `<feature_directory>/spec.md`
   - `<feature_directory>/prototype.html`
   - `<feature_directory>/quickstart.md`

3. Create dependency-ordered, requirement-level work packages in
   `<feature_directory>/tasks.md`.
   - Use the checklist form
     `- [ ] T001 [P] [US1] [BUILD] Observable outcome | Refs: ... | Depends: ... | Done when: ...`.
   - Use `[BUILD]` for delivery work and `[UAT]` for acceptance execution.
   - Organize packages by the user story, requirement, and acceptance priority
     represented in the frozen contract.
   - Give every `[BUILD]` package explicit `FR-*` and `SC-*` coverage, the exact
     `data-spec-ref` anchors it fulfills, and the `UAT-*` cases that prove it.
   - Create exactly one `[UAT]` task for every `UAT-*`. Each depends on all
     `[BUILD]` work required to make the scenario observable and is done only
     when `quickstart.md` records `Status: PASS`, plus actual result, evidence,
     and deviation.
   - Include a traceability summary covering every requirement, success
     criterion, prototype anchor, and UAT case without duplication or gaps.
   - State observable outcomes and tests. Do **not** prescribe a technology,
     architecture, API shape, dependency, command, component, or file path.
   - Preserve `spec.md`, `prototype.html`, and `quickstart.md` unchanged.

4. Validate that:
   - Every `FR-*`, `SC-*`, and prototype anchor has a `[BUILD]` package.
   - Every `UAT-*` has `[BUILD]` coverage and exactly one `[UAT]` task.
   - Every package points only to IDs and anchors present in the frozen contract.
   - No package contains technical choices or file-path lock-in.
   - Missing, conflicting, duplicate, or unresolved contract items block output
     and return to Specify or Clarify; Task does not fill them in.

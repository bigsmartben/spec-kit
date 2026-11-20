---
description: Choose and execute the implementation, then run the frozen UAT contract.
---

## User Input

```text
$ARGUMENTS
```

Select this invocation's scope from `$ARGUMENTS` before executing work:
- With no explicit scope, use every unchecked work package and every UAT it
  references.
- With an explicit task, phase, or acceptance scope, execute only that selection.
- Do not silently add omitted work. An incomplete dependency outside the
  selected scope blocks the dependent work.
- Leave out-of-scope work unchanged, including task checkboxes and UAT entries.

## Outline

1. Read `.specify/feature.json` to get the feature directory path.

2. **Load the frozen contract and work packages**:
   - `.specify/memory/constitution.md`
   - `<feature_directory>/spec.md`
   - `<feature_directory>/prototype.html`
   - `<feature_directory>/quickstart.md`
   - `<feature_directory>/tasks.md`

3. **Own the technical choices** for the selected scope. Select the
   architecture, dependencies, file layout, implementation details, test
   strategy, and commands needed to satisfy the frozen contract and selected
   work packages.

4. Execute selected work packages in dependency order:
   - Complete each selected package before moving to a dependent package.
   - Mark a package complete only after its completion condition is satisfied,
     by changing `- [ ]` to `- [x]` in `tasks.md`.
   - Halt on a blocking failure, report the issue, and keep the failed package
     unchecked.

5. Run the selected or explicitly mapped `UAT-*` scenarios in `quickstart.md`.
   For each executed scenario:
   - Locate the exact `[UAT]` task for the scenario. If it is missing or
     duplicated, stop and regenerate tasks; Implement does not create task
     structure.
   - Set `Status` to `PASS`, `FAIL`, or `BLOCKED` only from observed execution.
   - Update **only** the existing `Status`, `Actual Result`, `Evidence`, and
     `Deviation` fields. Do not rewrite the frozen preconditions, actions,
     expected result, requirement references, or prototype references.
   - Mark the `[UAT]` task complete only for `PASS`; for `FAIL` or `BLOCKED`,
     leave it unchecked.
   - If the failure shows the frozen contract itself is wrong, missing, or
     contradictory, stop and return the issue to Specify or Clarify, then
     regenerate the dependent tasks before continuing.

6. Validate all selected work and report whether the invocation is `COMPLETE`,
   `PARTIAL`, or `BLOCKED`. The run is complete only when all selected work
   satisfies its completion condition and every selected UAT passes. Report the
   implementation approach, test evidence, deviations, untouched out-of-scope
   work, and any blocked cases.

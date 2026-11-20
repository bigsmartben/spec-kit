---
description: Choose and execute the implementation, then run the frozen UAT contract.
---

## User Input

```text
$ARGUMENTS
```

## Outline

1. Read `.specify/feature.json` to get the feature directory path.

2. **Load the frozen contract and work packages**:
   - `.specify/memory/constitution.md`
   - `<feature_directory>/spec.md`
   - `<feature_directory>/prototype.html`
   - `<feature_directory>/quickstart.md`
   - `<feature_directory>/tasks.md`

3. **Own the technical choices**. Select the architecture, dependencies, file
   layout, implementation details, test strategy, and commands needed to satisfy
   the frozen contract and work packages.

4. Execute the work packages in dependency order:
   - Complete each package before moving to a dependent package.
   - Mark completed packages by changing `- [ ]` to `- [x]` in `tasks.md`.
   - Halt on a blocking failure and report the issue.

5. Run every `UAT-*` scenario in `quickstart.md`. For each scenario, update
   **only** the existing `Status`, `Actual Result`, `Evidence`, and `Deviation`
   fields. Do not rewrite the frozen preconditions, actions, expected result,
   requirement references, or prototype references.

6. Validate that every work package and UAT scenario is complete, and report the
   implementation approach, test evidence, deviations, and any blocked cases.

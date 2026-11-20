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
     `- [ ] WP001 [Priority/Story] Observable outcome and completion condition`.
   - Organize packages by the user story, requirement, and acceptance priority
     represented in the frozen contract.
   - Give every package explicit `FR-*` and `SC-*` coverage, the exact
     `data-spec-ref` anchors it fulfills, and the `UAT-*` cases that prove it.
   - Include a traceability summary covering every requirement, success
     criterion, prototype anchor, and UAT case without duplication or gaps.
   - State observable outcomes and tests. Do **not** prescribe a technology,
     architecture, API shape, dependency, command, component, or file path.
   - Preserve `spec.md`, `prototype.html`, and `quickstart.md` unchanged.

4. Validate that:
   - Every `FR-*`, `SC-*`, prototype anchor, and `UAT-*` case has a package.
   - Every package points only to IDs and anchors present in the frozen contract.
   - No package contains technical choices or file-path lock-in.

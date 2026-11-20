---
description: Create a specification, construction-contract prototype, and pending UAT baseline.
---

## User Input

```text
$ARGUMENTS
```

## Outline

1. **Ask the user** for the feature directory path (e.g., `specs/my-feature`) when it was not supplied.

2. Create the directory and write `.specify/feature.json`:
   ```json
   { "feature_directory": "<feature_directory>" }
   ```

3. Resolve all three composed templates at runtime using the script variant
   installed by `.specify/init-options.json`:
   - Bash: run `.specify/scripts/bash/resolve-template.sh <template-name> --json`
   - PowerShell: run `.specify/scripts/powershell/resolve-template.ps1 <template-name> -Json`
   - Python: run the selected Python interpreter on `.specify/scripts/python/resolve_template.py <template-name> --json`
   - Use `<template-name>` values `spec-template`, `prototype-template`, and
     `quickstart-template`.
   - Stop if any resolver call fails; do not read or copy an uncomposed template file.

4. From the user input, create:
   - `<feature_directory>/spec.md` with testable requirements and scenarios
   - `<feature_directory>/prototype.html` as self-contained executable HTML with
     stable, unique `data-spec-ref` anchors. Treat the visual and interaction
     behavior as a construction contract, not as inspiration.
   - `<feature_directory>/quickstart.md` with stable `UAT-*` cases mapped to
     requirements and exact prototype anchors. Set every status to `PENDING`
     and record no actual result, evidence, or pass/fail decision.

5. Validate the artifacts together before reporting completion:
   - Every user-visible story has UAT coverage
   - Every UAT resolves to a requirement and an existing prototype anchor
   - The prototype has no external runtime dependency
   - All UAT entries are pending

6. Report all three artifact paths.

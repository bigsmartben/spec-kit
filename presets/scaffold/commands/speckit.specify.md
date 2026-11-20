---
description: "Create the feature specification, prototype, and pending UAT baseline (preset override)"
scripts:
  sh: scripts/bash/create-new-feature.sh "{ARGS}"
  ps: scripts/powershell/create-new-feature.ps1 "{ARGS}"
---

## User Input

```text
$ARGUMENTS
```

Given the feature description above:

1. Create the feature branch and initial directory by running
   `{SCRIPT} --json --short-name "<short-name>" "<description>"`. The JSON
   output contains `BRANCH_NAME` and `SPEC_FILE`; derive the feature directory
   from `SPEC_FILE`.

2. Resolve the composed templates using the script variant installed by
   `.specify/init-options.json`:
   - Bash: `.specify/scripts/bash/resolve-template.sh <template-name> --json`
   - PowerShell: `.specify/scripts/powershell/resolve-template.ps1 <template-name> -Json`
   - Python: the selected Python interpreter on
     `.specify/scripts/python/resolve_template.py <template-name> --json`
   Use `spec-template`, `prototype-template`, and `quickstart-template`. Stop
   if any composition fails.

3. Write `spec.md` from the composed spec template.

4. Write `prototype.html` from the composed prototype template. It must be
   self-contained executable HTML, define unique `data-spec-ref` anchors, and
   act as the construction contract for visible and interactive behavior.

5. Write `quickstart.md` from the composed UAT template. Define stable `UAT-*`
   scenarios mapped to requirements and exact prototype anchors. Every status
   must be `PENDING`, with no actual result, evidence, deviation, or conclusion.

6. Validate that all three artifacts agree, then report all paths.

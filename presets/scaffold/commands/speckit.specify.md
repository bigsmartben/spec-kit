---
description: "Create the feature specification, prototype, and pending UAT baseline (preset override)"
scripts:
  sh: scripts/bash/resolve-template.sh spec-template --json
  ps: scripts/powershell/resolve-template.ps1 spec-template -Json
  py: scripts/python/resolve_template.py spec-template --json
---

## User Input

```text
$ARGUMENTS
```

Given the feature description above:

1. Resolve the active `spec-template` with `{SCRIPT}`, then resolve the
   `prototype-template` and `quickstart-template` by replacing the literal
   `spec-template` argument in the same resolver command. Stop if any
   composition fails.

2. Create or select the feature directory and persist its path in
   `.specify/feature.json`.

3. Write `spec.md` from the composed spec template.

4. Write `prototype.html` from the composed prototype template. It must be
   self-contained executable HTML, define unique `data-spec-ref` anchors, and
   act as the construction contract for visible and interactive behavior.

5. Write `quickstart.md` from the composed UAT template. Define stable `UAT-*`
   scenarios mapped to requirements and exact prototype anchors. Every status
   must be `PENDING`, with no actual result, evidence, deviation, or conclusion.

6. Validate that all three artifacts agree, then report all paths.

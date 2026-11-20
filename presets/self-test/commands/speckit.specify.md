---
description: "Self-test override of the Specify command with prototype and UAT outputs"
scripts:
  sh: scripts/bash/resolve-template.sh spec-template --json
  ps: scripts/powershell/resolve-template.ps1 spec-template -Json
  py: scripts/python/resolve_template.py spec-template --json
---

<!-- preset:self-test -->

You are following the self-test preset's version of the specify command.

When creating a specification, follow this process:

1. Read the user's requirements from $ARGUMENTS.
2. Resolve `spec-template` with `{SCRIPT}`, then resolve `prototype-template`
   and `quickstart-template` by replacing the literal template argument in the
   same resolver command. Stop if any template is missing or invalid.
3. Create `spec.md`, `prototype.html`, and `quickstart.md`.
4. Include all standard sections plus the self-test marker in each artifact.
5. Make the prototype executable and self-contained, with stable
   `data-spec-ref` anchors.
6. Create `UAT-*` scenarios mapped to the requirements and prototype anchors;
   keep every status `PENDING` and leave execution results empty.
7. Validate cross-artifact references and report all three paths.

> This command is provided by the self-test preset.

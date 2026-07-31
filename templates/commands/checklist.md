---
description: Generate or recompute requirement-quality gates before implementation planning.
scripts:
  sh: scripts/bash/check-prerequisites.sh --json
  ps: scripts/powershell/check-prerequisites.ps1 -Json
  py: scripts/python/check_prerequisites.py --json
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding.

## Responsibility

This command is the requirement-stage gate builder. It treats the specification
as executable prose and checks whether requirements are complete, clear,
consistent, measurable, and traceable. It does not test an implementation and
does not create plan-stage behavior-testability artifacts.

Expected lifecycle:

```text
__SPECKIT_COMMAND_SPECIFY__
  → __SPECKIT_COMMAND_CHECKLIST__
  → __SPECKIT_COMMAND_CLARIFY__
  → recompute affected gates
  → aggregate Planning Readiness PASS
```

Planning Readiness is an in-memory aggregate. Never create
`planning-readiness.md`. Never create
`checklists/behavior-testability.md`; that legacy path is non-authoritative.

## Pre-Execution Hooks

Read `.specify/extensions.yml` when present and process enabled
`hooks.before_checklist` entries:

- Ignore invalid YAML and hooks with `enabled: false`.
- Run an entry only when `condition` is absent or empty.
- For a mandatory hook (`optional: false`), emit `EXECUTE_COMMAND: {command}`,
  invoke it using the current agent's command syntax, and wait for completion.
- For an optional hook, show its command, description, and prompt without
  invoking it.

## Execution

1. Run `{SCRIPT}` once from the repository root and parse `FEATURE_DIR`,
   `FEATURE_SPEC`, and `IMPL_PLAN`.
2. Require `FEATURE_SPEC` to exist. If it does not, stop and direct the user to
   `__SPECKIT_COMMAND_SPECIFY__`.
3. If `IMPL_PLAN` already exists, stop. Requirement gates are authored before
   planning and cannot be regenerated from plan or tasks.
4. Read only `FEATURE_SPEC` and, if present, `/memory/constitution.md`. Do not read `plan.md` or `tasks.md`.
5. Compute the SHA-256 digest of the exact `spec.md` bytes and format it as
   `sha256:<lowercase-hex>`. Use the platform-native equivalent of
   `sha256sum`/`shasum -a 256` or `Get-FileHash -Algorithm SHA256`.
6. Evaluate the standard requirement domains:
   `requirements`, `behavior`, `ux`, `security`, `nfr`, and `visual`.
   - Each domain must have an explicit result.
   - Use `APPLICABLE` when the spec contains or requires that domain.
   - Use `NOT_APPLICABLE` only with a concrete reason derived from the spec.
   - A workflow preset may add domains but may not silently omit the standard
     domain evaluation.
7. Create or recompute `FEATURE_DIR/checklists/<domain>.md`. The existing
   `requirements.md` created by specify is the baseline requirements domain.
8. Custom user-requested helper checklists default to `Gate: advisory`. Only
   files explicitly marked `Gate: planning-readiness` block planning.

## Checklist Contract

Every generated checklist starts with:

```markdown
**Stage**: requirements
**Domain**: <domain>
**Gate**: planning-readiness | advisory
**Applicability**: APPLICABLE | NOT_APPLICABLE
**Status**: PASS | BLOCKED
**Spec Revision**: sha256:<spec-content-hash>
```

For `NOT_APPLICABLE`, include `**Applicability Reason**: <reason>` and set
`Status: PASS`.

Use stable, domain-namespaced IDs such as `CHK-SEC-001` or `CHK-NFR-003`.
Blocking items must declare their routing:

```markdown
- [ ] CHK-SEC-003 [blocker:product-decision] [spec:FR-012] Is the guest export policy specified?
- [ ] CHK-VIS-004 [blocker:provider-evidence] [return:source-evidence] Is the approved design revision referenced?
```

- `product-decision` means clarify may ask the user and update `spec.md`.
- `provider-evidence` means the item remains blocked and returns to the
  responsible source-evidence/provider workflow.
- Checked items are satisfied requirement-quality assertions. Unchecked
  planning-gate items make that checklist `BLOCKED`.

Regeneration is recomputation, not append-only:

- Reuse stable IDs for the same requirement concern.
- Replace generated status and blocker sections atomically.
- Remove blockers that no longer apply.
- Preserve unrelated manual notes, but never accumulate duplicate Gate Status
  blocks or duplicate IDs.

Checklist items must ask about what is written in the requirements. Good:
“Is retry behavior quantified for each external dependency?” Bad: “Test that
retry works.”

At least 80% of applicable items must reference a requirement ID/section or a
`[Gap]`, `[Ambiguity]`, `[Conflict]`, or `[Assumption]` marker.

## Aggregate Planning Readiness

After writing all domain results, compute and report the aggregate without
creating another file:

- PASS only when every standard domain was evaluated, every
  `planning-readiness` checklist carries the current spec revision, and every
  applicable gate is `PASS`.
- `NOT_APPLICABLE` is acceptable only with a reason.
- Missing domains, stale revisions, malformed metadata, or any `BLOCKED` gate
  produce BLOCKED.
- Advisory checklists are shown separately and never affect the aggregate.

When BLOCKED, list each blocker ID and route:

- product decisions → `__SPECKIT_COMMAND_CLARIFY__`
- provider evidence → source-evidence/provider workflow

## Post-Execution Hooks

After gate files and the aggregate result are complete, process enabled
`hooks.after_checklist` using the same mandatory/optional and condition rules as
the pre-execution hooks. Mandatory hooks must be invoked and awaited.

## Completion Report

Report:

- evaluated domains and applicability;
- created/recomputed file paths;
- current spec revision;
- per-domain status;
- aggregate Planning Readiness PASS or BLOCKED;
- product-decision blockers and provider-evidence blockers in separate lists;
- suggested next command.

## Done When

- [ ] Only requirement-stage sources were read
- [ ] Every standard domain has an explicit result
- [ ] Stable metadata and IDs were written without duplicate stale blockers
- [ ] No planning-readiness or behavior-testability checklist file was created
- [ ] Planning Readiness was aggregated in memory and reported
- [ ] Extension hooks were processed

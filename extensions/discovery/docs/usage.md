# Usage

Use the `discovery` extension before formal development when an interface boundary is important enough to validate before writing production code.

The extension provides one focused command:

- `/speckit.discovery.contract`: finds the key interface design from `uc.md`, `spec.md`, or `arch.md`, validates that design with non-persistent evidence, and produces the single artifact `interface-contract.md`.

## When To Use It

Use this command when the open question is:

- What interface designs are implied by the use case, spec, or architecture notes?
- Which interface design is most important to validate before implementation?
- Can the selected design satisfy the required contract fields before implementation starts?
- What request, response, event, error, auth, retry, timeout, observability, versioning, or compatibility terms should be handed to planning?

Good candidates include:

- External API or webhook integration.
- Internal service boundary.
- SDK method or CLI command contract.
- Message, event, queue, or topic contract.
- Batch job or scheduled interface with an explicit input/output boundary.
- Cross-system interface with contract-visible payloads.

## Inputs

```text
/speckit.discovery.contract [source docs or feature scope] [interface design focus] [constraints]
```

Source discovery order:

1. Explicit source paths passed in the command.
2. The active feature directory.
3. Repository files named `uc.md`, `spec.md`, or `arch.md`.

If several interface designs are present, the command selects the highest-impact design needed to validate feasibility before implementation.

## Example

```text
/speckit.discovery.contract Source: features/invoice-sync/uc.md, features/invoice-sync/arch.md. Focus: invoice status update webhook. Constraints: idempotent retry handling, signed requests, p95 handler time below 200ms for synthetic payloads.
```

Expected result:

- `interface-contract.md`
- source refs for extracted candidate designs
- selected key interface design
- validation evidence or blocker codes
- `Contract Status`: `validated`, `validated-with-risks`, `blocked`, or `inconclusive`

## Validation Rules

The command may run validation only when all preconditions are true:

- Dependencies are installed or already declared by the repository.
- Commands are read-only or leave no persistent workspace changes.
- Inputs are inline synthetic samples, existing fixtures, or explicitly approved current-conversation samples.
- No production data, live write APIs, real secrets, or behavior-changing external side effects are used.
- Expected runtime is under 5 minutes.

If a precondition fails, the command records `BLOCKED_PRECONDITION` and still produces the contract with explicit gaps.

The command must not create separate PoC files, validation directories, logs, fixtures, screenshots, generated payload files, or other persistent evidence artifacts. All evidence is summarized inside `interface-contract.md`.

## Recommended Flow

1. Draft or update `uc.md`, `spec.md`, or `arch.md`.
2. Run `/speckit.discovery.contract` for the interface boundary with the highest implementation risk.
3. Review `interface-contract.md`.
4. Continue to formal Spec Kit planning only when `Contract Status` is `validated` or `validated-with-risks` and remaining risks are accepted.

# Verified Interface Contract

## Source Intake

| Source ID | File | Section or lines | Contract relevance | Evidence status |
|---|---|---|---|---|

Evidence status values: `source-backed`, `repo-backed`, `validated`, `assumption`, or `unknown`.

## Candidate Interface Designs

| Candidate interface design | Classification | Actors or systems | Trigger | Input data | Output data | Constraint or risk | Source refs |
|---|---|---|---|---|---|---|---|

Classification values: `required`, `optional`, or `unclear`.

Selection rule: choose from `required` candidates first. The selected candidate must have a source-backed input/output boundary, the highest implementation risk, and validation evidence that would change formal planning. If no `required` candidate exists, record `AMBIGUOUS_CAPABILITY` and ask one concise clarifying question instead of selecting an optional candidate by default. If candidates tie, select the one with the strongest source emphasis and record `AMBIGUOUS_CAPABILITY` for the others.

## Key Interface Design Under Validation

State the selected interface design and why it is the key design to validate before implementation.

| Field | Value | Evidence | Source refs |
|---|---|---|---|
| Interface name |  |  |  |
| Boundary |  |  |  |
| Direction |  |  |  |
| Transport or invocation style |  |  |  |
| Caller or producer |  |  |  |
| Callee or consumer |  |  |  |
| Primary operation |  |  |  |
| Why this design is key |  |  |  |

## Design Validation Route

Include only choices that change the selected interface design, validation feasibility, or contract risk. Do not create a general technology matrix.

| Option | Fit for selected design | Evidence | Route status |
|---|---|---|---|

Route status values: `used`, `rejected`, `needs-validation`, or `unknown`.

Selected validation route:

Rationale:

Rejected validation routes:

## Contract Definition

### Operation

| Field | Value | Evidence |
|---|---|---|
| Method, topic, command, or function |  |  |
| Path, channel, queue, or entry point |  |  |
| Sync or async behavior |  |  |
| Auth or trust boundary |  |  |
| Idempotency or retry behavior |  |  |
| Timeout, rate, or size constraints |  |  |
| Versioning or compatibility rule |  |  |
| Observability expectations |  |  |

### Request Or Event Payload

| Field | Type | Required | Meaning | Evidence | Validation notes |
|---|---|---|---|---|---|

### Response, Result, Or Emitted Event

| Field | Type | Required | Meaning | Evidence | Validation notes |
|---|---|---|---|---|---|

### Errors And Edge Cases

| Code or condition | Trigger | Contract behavior | Evidence | Validation notes |
|---|---|---|---|---|

## Validation Evidence

Validation question:

Hypothesis:

Scope: selected interface design feasibility only. Do not summarize an unrelated PoC, benchmark, prototype, or implementation plan.

Persistence rule: evidence must come from source refs, existing commands, existing tests, read-only probes, or temporary snippets. Do not reference generated validation files.

| Check | Method | Command or evidence ref | Result | Notes |
|---|---|---|---|---|

Result values: `passed`, `failed`, `blocked`, or `inconclusive`.

## Blockers And Gaps

| Code | Gap or blocker | Impact on contract | Required resolution |
|---|---|---|---|

Suggested blocker codes: `MISSING_SOURCE_DOC`, `AMBIGUOUS_CAPABILITY`, `UNSUPPORTED_FIELD`, `BLOCKED_PRECONDITION`, `VALIDATION_FAILED`, `RUNTIME_DEPENDENT`, `EXTERNAL_CLARIFICATION_NEEDED`.

## Contract Handoff

| Item | Value |
|---|---|
| Contract status |  |
| Ready for formal planning |  |
| Unresolved validation gaps |  |
| Persistent artifact | `interface-contract.md` |
| Commands run |  |
| Workspace cleanliness check |  |

Contract Status allowed values: `validated`, `validated-with-risks`, `blocked`, or `inconclusive`.

Status gate: `validated` requires all required selected-design fields to be `source-backed`, `repo-backed`, or `validated`, all required source refs present, and no unresolved blocker codes. `validated-with-risks` allows bounded assumptions but no `unknown` required fields; risk acceptance must come from the user or source docs, while repository evidence may only bound the risk. `blocked` applies when source docs, input/output boundary, required fields, validation preconditions, blocker resolution, or workspace cleanliness checks fail. `inconclusive` applies only when available evidence is mixed, contradictory, runtime-dependent, or insufficient after allowed validation.

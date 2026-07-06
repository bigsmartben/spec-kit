# Spec Kit Discovery Extension

`spec-kit-discovery` provides a focused `discovery` extension for one pre-development job: find the key interface design implied by `uc.md`, `spec.md`, or `arch.md`, validate that design, then produce one verified interface contract artifact.

```text
/speckit.discovery.contract [source docs or feature scope] [interface design focus] [constraints]
```

Use it before `/speckit.specify`, `/speckit.plan`, or implementation work when the main uncertainty is an API, event, command, SDK method, webhook, batch job, or cross-system service boundary.

## Output

The command creates or updates only one persistent artifact:

- `interface-contract.md`

The contract records:

- source-backed candidate interface designs extracted from `uc.md`, `spec.md`, or `arch.md`
- the selected key interface design and validation route
- request, response, event, error, auth, retry, timeout, observability, versioning, and compatibility contract details
- static or executable validation evidence
- blocker codes and remaining gaps
- `Contract Status`: `validated`, `validated-with-risks`, `blocked`, or `inconclusive`

Validation evidence must be embedded in `interface-contract.md`. The command does not create separate PoC files, validation directories, logs, fixtures, screenshots, or generated payload artifacts.

## Installation

From a Spec Kit project:

```bash
specify extension add --dev /path/to/spec-kit-discovery
```

From this repository during local development:

```bash
specify extension add --dev . --force
```

After installation, restart or refresh your AI coding agent if the new command does not appear immediately.

## Command

### `speckit.discovery.contract`

Finds the key interface design from the input material, validates feasibility with source refs, existing commands, existing tests, read-only probes, or temporary snippets, and renders `templates/interface-contract.md`.

Minimum useful input:

- Source docs or feature scope: explicit paths, a feature directory, or a feature name.
- Interface design focus: API, event, command, SDK method, internal service boundary, webhook, batch job with an explicit input/output boundary, or cross-system interface.
- Constraints: runtime, protocol, framework, auth, data, performance, compatibility, migration, rollout, or operational constraints.

Example:

```text
/speckit.discovery.contract Source: specs/payments/spec.md and specs/payments/arch.md. Focus: Stripe webhook ingestion contract. Constraints: idempotent retries, signature verification, no duplicate invoice updates.
```

When source docs are not passed explicitly, the command looks for `uc.md`, `spec.md`, or `arch.md` in the active feature directory or repository.

## Repository Structure

```text
.
├── extension.yml
├── commands/
│   └── discovery.md
├── templates/
│   └── interface-contract.md
├── docs/
│   └── usage.md
├── CHANGELOG.md
├── LICENSE
└── README.md
```

## Development

Validate manifest references before release:

```bash
specify extension add --dev /path/to/spec-kit-discovery --force
specify extension info discovery
```

## License

MIT

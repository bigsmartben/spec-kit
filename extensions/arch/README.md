# Spec Kit Architecture Command Migration Extension

This v3 extension retires standalone Architecture generation.

Project Architecture now belongs to the standard Constitution stage, provided by
`workflow-preset`. The Constitution command maintains two separate long-lived
artifacts:

```text
.specify/memory/constitution.md
.specify/memory/architecture.md
```

`constitution.md` contains durable governance. `architecture.md` contains the
project boundary, conceptual model, technical direction and evidence, planning
constraints, and unresolved gaps.

## Why This Extension Still Exists

Existing projects may still have these command names installed:

```text
/speckit.arch.generate
/speckit.arch.reverse
```

In v3 they are compatibility entrypoints only. They perform no discovery,
generation, setup, validation, or writes. Each command returns
`ARCH_COMMAND_RETIRED` and directs the user to `/speckit.constitution`.

For example, replace:

```text
/speckit.arch.reverse
```

with:

```text
/speckit.constitution Brownfield amendment. Use README.md and services/api/
configuration as authorized evidence, exclude Git history, and update Architecture.
```

## Target Architecture Workflow

Install or enable
[workflow-preset](https://github.com/bigsmartben/spec-kit-workflow-preset),
then run:

```text
/speckit.constitution
```

The Constitution stage first confirms:

- greenfield, brownfield, or amendment mode;
- the goal of the run;
- user-selected sources and the role of each source;
- excluded sources;
- whether repository inspection is allowed and its scope;
- whether Constitution, Architecture, or both may be updated.

No UC path or discovered file is automatically authoritative.

The resulting single-file Architecture uses:

```text
System Boundary
  -> Conceptual Model
  -> Technical Decisions & Evidence
  -> Planning Guardrails & Gaps
```

There is no 4+1 reasoning, secondary Architecture model, PoC generation,
working-model Schema, or Markdown readiness Validator in this extension.

## Upgrade Notes

Existing v2 `.specify/memory/architecture.md` files are not rewritten by the
compatibility commands. Run `/speckit.constitution`, authorize an Architecture
amendment, and include the existing file as a selected source. The Constitution
stage reports `ARCH_LEGACY_FORMAT` before migrating the old nine-section or 4+1
shape.

Remove this extension after all integrations and team documentation use
`/speckit.constitution`; the two compatibility commands are then unnecessary.

## Install

Published v3 release:

```bash
specify extension add arch --from https://github.com/bigsmartben/spec-kit-arch/releases/download/v3.0.1/arch-v3.0.1.zip
```

Local development checkout:

```bash
specify extension add --dev /path/to/spec-kit-arch
```

## Development

Run the source contract:

```bash
bash tests/repository-first-contract.sh
```

The test verifies that both legacy command names remain safe, write-free
migration entrypoints and that the removed generation stack is not packaged.

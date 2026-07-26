# SDD Inception Extension

Run optional product inception before formal Spec Kit specification.

## Product Inception

`/speckit.inception.product` converges user-confirmed product ideas into:

```text
inception/product/uc.md
inception/product/wireflow-medium.html
inception/product/wireflow-high.html
```

`wireflow-medium.html` and `wireflow-high.html` are derived from `uc.md`. They
must not create new product facts or overwrite the product boundary established
in `uc.md`.

Product inception is optional. Its outputs become downstream inputs only when
the user selects them for a later command.

## Retired Architecture Inception

`/speckit.inception.arch` is retained only as a write-free compatibility
entrypoint. It returns `INCEPTION_ARCH_COMMAND_RETIRED` and directs the user to:

```text
/speckit.constitution
```

The compatibility command does not read `inception/product/uc.md`, create
`inception/arch/`, run PoC code, or write project Architecture.

For example:

```text
/speckit.constitution Greenfield. Use inception/product/uc.md as the selected
product-intent source, exclude wireflow HTML, and update Constitution and Architecture.
```

The user may select `inception/product/uc.md`, another product document,
conversation input, existing Architecture, authorized repository evidence, or
external constraints. No conventional path is mandatory.

## Boundaries

The inception extension does not create formal Spec Kit artifacts:

```text
.specify/memory/constitution.md
.specify/memory/architecture.md
spec.md
plan.md
tasks.md
OpenAPI
database schema
application implementation
test suite changes
```

Use `/speckit.constitution` for project governance and Architecture, then
`/speckit.specify` for feature requirements.

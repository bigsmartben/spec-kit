# SDD Inception Extension

Run the pre-iteration inception stage before formal Spec Kit specification and planning.

This extension provides two conversational workflow commands:

```text
/speckit.inception.product
/speckit.inception.arch
```

The commands guide the user through confirmation points, then write only inception artifacts under the project root `inception/` directory.

## Product Inception

`/speckit.inception.product` converges product ideas into:

```text
inception/product/uc.md
inception/product/wireflow-medium.html
inception/product/wireflow-high.html
```

`wireflow-medium.html` and `wireflow-high.html` are derived from `uc.md`. They must not create new product facts and must not overwrite the product boundary established in `uc.md`.

## Architecture Inception

`/speckit.inception.arch` uses one formal input:

```text
inception/product/uc.md
```

It writes:

```text
inception/arch/api-capability.md
inception/arch/api-poc.md
inception/arch/system-boundary.md
inception/arch/domain-model.md
inception/arch/arch.md
inception/arch/api-poc-runs/
```

`api-capability.md` includes a technology selection matrix that compares candidate options for high-value or high-risk capabilities, then records recommended, backup, and rejected options with tradeoff rationale.

`api-poc.md` records real code execution evidence. Before running any POC code, the command must confirm the target capability, validation hypothesis, runtime environment, dependencies, credential/config needs, sample input, external service access, allowed side effects, and stop conditions with the user.

POC code and outputs are confined to:

```text
inception/arch/api-poc-runs/<capability-slug>/
```

## Boundaries

The inception commands do not create formal Spec Kit artifacts:

```text
spec.md
plan.md
tasks.md
OpenAPI
database schema
application implementation
test suite changes
```

Use `/speckit.specify` after product inception, and use `/speckit.plan` after formal specs and architecture context are ready.

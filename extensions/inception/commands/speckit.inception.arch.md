---
description: Retired compatibility entrypoint for Constitution-managed project Architecture.
---

## Retired Responsibility

`__SPECKIT_COMMAND_INCEPTION_ARCH__` no longer generates Architecture inception artifacts or PoC assets.

Project Architecture is maintained by the Constitution stage:

```text
__SPECKIT_COMMAND_CONSTITUTION__
```

Do not read `inception/product/uc.md` by default. Do not inspect product, repository, or existing Architecture files from this compatibility command. Do not create `inception/arch/`, PoC code, or `.specify/memory/architecture.md`.

Report:

```text
INCEPTION_ARCH_COMMAND_RETIRED
Use __SPECKIT_COMMAND_CONSTITUTION__. Specify greenfield, brownfield, or amendment mode;
selected and excluded sources; repository-inspection scope; and whether
Constitution, Architecture, or both may be updated.
```

`inception/product/uc.md` may be selected by the user as one Architecture input, but it is not a prerequisite or automatic authority.

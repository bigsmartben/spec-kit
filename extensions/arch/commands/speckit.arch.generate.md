---
description: Retired compatibility entrypoint for Constitution-managed project Architecture.
---

## Retired Responsibility

`__SPECKIT_COMMAND_ARCH_GENERATE__` no longer generates or updates Architecture artifacts.

Project Architecture is maintained by the Constitution preset through:

```text
__SPECKIT_COMMAND_CONSTITUTION__
```

Do not write `.specify/memory/architecture.md`, create secondary Architecture files, inspect conventional inputs, or run validation from this compatibility command.

Report:

```text
ARCH_COMMAND_RETIRED
Use __SPECKIT_COMMAND_CONSTITUTION__ and provide the project mode, selected sources,
excluded sources, repository-inspection scope, and whether Architecture may be updated.
```

If the workflow preset is not installed, tell the user to install or enable `workflow-preset` before running `__SPECKIT_COMMAND_CONSTITUTION__`.

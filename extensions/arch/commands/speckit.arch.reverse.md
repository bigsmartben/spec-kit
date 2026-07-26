---
description: Retired compatibility entrypoint for brownfield Constitution-managed Architecture.
---

## Retired Responsibility

`__SPECKIT_COMMAND_ARCH_REVERSE__` no longer derives or updates Architecture from repository evidence.

Brownfield Architecture is maintained by the Constitution preset through:

```text
__SPECKIT_COMMAND_CONSTITUTION__
```

Do not inspect the repository, Git history, README files, configuration, source, tests, or other candidate evidence from this compatibility command. Do not write `.specify/memory/architecture.md` or create secondary Architecture artifacts.

Report:

```text
ARCH_COMMAND_RETIRED
Use __SPECKIT_COMMAND_CONSTITUTION__ in brownfield mode. Explicitly authorize the repository
scope and the role of each selected evidence source.
```

If the workflow preset is not installed, tell the user to install or enable `workflow-preset` before running `__SPECKIT_COMMAND_CONSTITUTION__`.

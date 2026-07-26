# Changelog

## 2.0.0

- Move Architecture inception into the Constitution-managed single-file
  project Architecture lifecycle.
- Retain `/speckit.inception.arch` only as a write-free compatibility
  entrypoint returning `INCEPTION_ARCH_COMMAND_RETIRED`.
- Remove the five `inception/arch/` templates and automatic PoC responsibility.
- Make product inception optional and require users to select its outputs
  explicitly when using them as Constitution-stage inputs.

## 1.0.0

- Add product and architecture inception workflow commands.
- Add template-backed inception artifacts under `inception/product/` and `inception/arch/`.
- Require user-confirmed preparation before running real API POC code.

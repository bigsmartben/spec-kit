# Extension Scaffold

Contract-first starter for a Spec Kit Extension.

## Quick Start

1. Copy this directory:

   ```bash
   cp -r extensions/template my-extension
   cd my-extension
   ```

2. Rename every `my-extension` identifier and keep command filenames aligned
   with their canonical IDs.
3. Put workflow routing in `commands/`, stable semantics in `contracts/`,
   persistent shapes in `templates/`, and machine structure in `schemas/`.
4. Replace the example focused tests with tests for the actual contract and
   lifecycle.
5. Validate before installing:

   ```bash
   uv run python scripts/validate-component-standard.py extensions/my-extension
   .venv/bin/python -m pytest extensions/my-extension/tests
   ```

6. Test installation from a Spec Kit project:

   ```bash
   specify extension add /path/to/my-extension --dev
   specify extension remove my-extension --force
   ```

## Files in This Template

- `extension.yml`: package contract and canonical command declarations.
- `commands/`: agent-neutral workflow prompts.
- `contracts/`: stable domain semantics.
- `templates/`: persistent artifact shapes.
- `schemas/`: machine-readable structure.
- `validators/`: deterministic cross-field readiness.
- `tests/`: focused executable evidence.
- `config-template.yml`: user configuration defaults.
- `README.md`, `CHANGELOG.md`, `LICENSE`: release evidence.

## Customization Checklist

- [ ] Update `extension.yml` with your extension details
- [ ] Keep command IDs and filenames in `speckit.<id>.<command>` form
- [ ] Keep platform rendering out of command sources
- [ ] Align Template, Schema, Validator, and tests
- [ ] Cover install, repeated install, rollback, and removal as applicable
- [ ] Update README, CHANGELOG, and LICENSE
- [ ] Run component validation and focused tests

## Normative Reference

See
[`docs/preset-extension-coding-standard.md`](../../docs/preset-extension-coding-standard.md).

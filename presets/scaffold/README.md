# Preset Scaffold

A contract-first starter for a custom Spec Kit Preset.

## Templates Included

| Template | Type | Description |
|----------|------|-------------|
| `spec-template` | template | Custom feature specification template (overrides core and extensions) |
| `myext-template` | template | Override of the myext extension's report template |
| `speckit.specify` | command | Custom specification command (overrides core) |
| `speckit.myext.myextcmd` | command | Override of the myext extension's myextcmd command |

## Development

1. Copy this directory: `cp -r presets/scaffold my-preset`
2. Edit `preset.yml` and keep every declared file aligned with its role.
3. Keep command routing in `commands/` and persistent shapes in `templates/`.
4. Add `schemas/` and pure in-memory `validators/` for structured artifacts.
5. Replace the example tests with focused contract and composition tests.
6. Validate and test:

   ```bash
   uv run python scripts/validate-component-standard.py presets/my-preset
   .venv/bin/python -m pytest presets/my-preset/tests
   ```

7. Test lifecycle and resolution:

   ```bash
   specify preset add ./my-preset --dev
   specify preset resolve spec-template
   specify preset remove my-preset
   ```

## Manifest Reference (`preset.yml`)

Required fields:

- `schema_version` — always `"1.0"`
- `preset.id` — lowercase alphanumeric with hyphens
- `preset.name` — human-readable name
- `preset.version` — semantic version (e.g. `1.0.0`)
- `preset.description` — brief description
- `requires.speckit_version` — version constraint (e.g. `>=0.1.0`)
- `provides.templates` — list of templates with `type`, `name`, and `file`

## Template Types

- **template** — Document scaffolds (spec-template.md, plan-template.md, tasks-template.md, etc.)
- **command** — AI agent workflow prompts (e.g. speckit.specify, speckit.plan)
- **script** — Custom scripts (reserved for future use)

Composition strategies:

- `replace`, `prepend`, `append`, and `wrap` for Template or Command.
- `replace` and `wrap` only for Script.
- `wrap` requires `{CORE_TEMPLATE}` or `$CORE_SCRIPT`.

## Normative Reference

See
[`docs/preset-extension-coding-standard.md`](../../docs/preset-extension-coding-standard.md).

# Spec Kit Extension Submission

Extension ID: preview
Name: Spec Kit Preview
Version: 1.3.0
Description: Generate one fidelity-specific HTML design artifact from spec.md and uc.md inputs with required low, mid, or high fidelity
Author: bigsmartben
Repository URL: https://github.com/bigsmartben/spec-kit-preview
Download URL: https://github.com/bigsmartben/spec-kit-preview/archive/refs/tags/v1.3.0.zip
Documentation URL: https://github.com/bigsmartben/spec-kit-preview/blob/main/README.md
License: MIT
Required Spec Kit version: >=0.8.10.dev0
Commands count: 1
Hooks count: 0
Tags: preview, prototype, html, wireflow, ux

## Key Features

- Adds `speckit.preview.wireflow` as the single preview command.
- Requires `low`, `mid`, or `high` as the first command argument.
- Generates one HTML design artifact at `specs/<feature>/preview/wireflow.html`.
- Requires `spec.md` and `uc.md` as first-class source inputs for design synthesis.
- Runs an Input-to-Design Synthesis Pass before composing the design artifact.
- Preserves `schemas/preview/mid-ir-adapter.schema.json` as an optional supporting input boundary for `mid` fidelity.
- Uses evidence and quality conclusions to improve the fidelity-specific design artifact by exposing supported flows, gaps, and design questions.
- Uses fixed `templates/preview/wireflow.html` output structure with design input mapping, interaction, state, and preserved design-note slots.
- Uses `schemas/preview/contract.json` and `schemas/preview/contract.schema.json` as the structural validation source.
- Keeps the preview self-contained with inline CSS and template-local JavaScript.
- Explicitly avoids production source, spec, plan, and task file changes.

## Testing Performed

- `python -m py_compile tests/validate-extension.py`
- `python tests/validate-extension.py`
- Validator verified the manifest registers one `speckit.preview.wireflow` command.
- Validator verified the command/template file set contains only `commands/speckit.preview.wireflow.md` and `templates/preview/wireflow.html`.
- Validator verified declared schema files, including `schemas/preview/mid-ir-adapter.schema.json`.
- Validator verified documentation alignment for `speckit.preview.wireflow` and `wireflow.html`.

## Release Checklist

- Create release `v1.3.0` from this revision.
- Install release ZIP in a fresh Spec Kit project:
  `specify extension add preview --from https://github.com/bigsmartben/spec-kit-preview/archive/refs/tags/v1.3.0.zip`

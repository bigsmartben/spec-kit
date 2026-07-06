# Spec Kit Extension Submission

Extension ID: discovery
Name: Spec Kit Discovery Extension
Version: 0.3.0
Description: Validate pre-development interface feasibility by finding the key interface design from uc.md, spec.md, or arch.md, validating that design with non-persistent evidence, and producing one verified interface contract artifact.
Author: bigsmartben
Repository URL: https://github.com/bigsmartben/spec-kit-discovery
Source commit SHA: 38f660c815f3ef95d80f143dac6c6411b12a9f04
Download URL: https://github.com/bigsmartben/spec-kit-discovery/archive/38f660c815f3ef95d80f143dac6c6411b12a9f04.zip
Documentation URL: https://github.com/bigsmartben/spec-kit-discovery#readme
License: MIT
Required Spec Kit version: >=0.1.0
Commands count: 1
Hooks count: 0
Tags: discovery, interface-contract, api, event, webhook, technical-validation, pre-development, validation

## Key Features

- Adds `/speckit.discovery` as the single public discovery command.
- Extracts candidate interface designs from `uc.md`, `spec.md`, or `arch.md`.
- Selects the key source-backed interface design to validate before formal development.
- Produces one persistent artifact: `interface-contract.md`.
- Keeps validation evidence non-persistent and embedded in the contract.

## Testing Performed

- Confirmed source `commands/` contains only `discovery.md`.
- Confirmed source `templates/` contains only `interface-contract.md`.
- Confirmed source `extension.yml` registers `speckit.discovery` with `commands/discovery.md`.
- Checked old command/template naming residuals with `rg`; no matches.
- Ran `git diff --check`; passed.
- Checked Markdown/YAML trailing whitespace with `rg`; no matches.

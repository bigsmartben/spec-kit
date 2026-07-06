# Changelog

## v1.3.0

- Replaces separate fidelity and format commands with one `speckit.preview` command.
- Requires `low`, `mid`, or `high` as the first command argument.
- Makes HTML the only generated artifact at `specs/<feature>/preview/wireflow.html`.
- Uses `spec.md` and `uc.md` as required primary inputs for input-to-design synthesis.
- Keeps structured IR mapping non-blocking for `mid` fidelity: missing, partial, or unmappable IR falls back to primary design inputs and is reported as a design question or delivery quality issue.

## v1.2.0

- Adds a preview-owned `schemas/preview/mid-ir-adapter.schema.json` ingest contract for evidence-backed mid-fidelity structured IR adaptation.
- Updates package validation so declared schema files are driven by `schemas/preview/contract.json` instead of a hard-coded schema file list.

## v1.1.0

- Replaces the six preview commands with one `speckit.preview` command.
- Requires `low`, `mid`, or `high` as the first command argument.
- Makes HTML the only generated artifact at `specs/<feature>/preview/wireflow.html`.
- Adds a unified `templates/preview/wireflow.html` template.
- Adds explicit Input-to-Design Synthesis Pass rules for `spec.md` and `uc.md`.
- Adds schema-backed validation contracts under `schemas/preview/` for single-command and single-template checks.
- Strengthens package validation for command/template responsibility separation, output boundaries, and documentation alignment.

## v1.0.0

- Initial release.
- Adds an initial self-contained interactive HTML preview flow for Spec Kit feature artifacts.

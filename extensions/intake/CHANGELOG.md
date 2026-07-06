# Changelog

## [0.1.5] - 2026-07-03

### Added

- Added `capture_figma_metadata_shards.py` to stage sharded Figma `get_metadata` captures into canonical raw metadata shards, index, and node inventory artifacts without passing large provider responses through agent context.
- Added `normalize_figma_layout.py`, `figma-normalized-tree.yaml`, and schema-backed readiness checks for Figma rename, grouping, and visual re-sort normalization after raw metadata parity passes.
- Added HTML mock readiness checks that require rendered mock page surfaces, page visual-state enumerations, page IA matrices, component visual-state enumerations, component IA matrices with interaction refs, and coverage evidence conclusions.
- Added HTML mock readiness checks for adjacent visual spec package readiness, `visual-spec-package/visual-spec.yaml` refs, visualized component node kinds, and preview-local screenshot refs.
- Added structured UI/visual asset source-of-truth checks that block evidence packets, preview HTML, screenshots, and visual diffs from being used as `source_refs` or `evidence_refs`.

### Changed

- Repositioned `previews/preview.html` as the static HTML/CSS mock equivalent for the visual input design generated from upstream intake artifacts, with coverage YAML preserving machine-checkable traceability.
- Kept Figma layout normalization as a derived artifact that does not rewrite raw metadata or replace `visual-requirements.yaml` source-backed facts.

## [0.1.4] - 2026-07-01

### Added

- Added visual-design visual spec package artifacts for CI-friendly DOM, ARIA, token, state, locator, relation, and assertion evidence.
- Added visual spec package schemas and `validate_visual_spec_package.py` for source readiness, cross-reference, provider-evidence, product-ambiguity, locator, downstream-ownership, and CI assertion checks.
- Added `visual-design/previews/` with `preview.html` as the visual-equivalent HTML delivery and `component-coverage.yaml` / `viewport-coverage.yaml` for machine-checkable coverage evidence under `/speckit.intake.visual-design`.

## [0.1.3] - 2026-06-29

### Added

- Added Figma-derived HTML mock coverage evidence with component-state, page, asset, viewport, screenshot, and known-gap readiness checks.
- Added bounded visual inference statuses for irregular Figma and visual-design sources, including `candidate` and `unsupported` claim handling.
- Added readiness blocking for unbounded visual inference and unsupported visual claims.

## [0.1.2] - 2026-06-23

### Changed

- Added release installation and runtime dependency documentation.
- Shortened manifest description and reduced tags for community catalog submission.

## [0.1.1] - 2026-06-23

### Changed

- Added community catalog metadata for category and effect.

## [0.1.0] - 2026-06-23

### Added

- Initial Spec Kit extension manifest.
- Intake commands for visual design, PRD, and test-case sources.
- Intake contracts and evidence packet templates for visual design, PRD, and test-case sources.
- Local readiness validators for PRD, test-case, visual design, and Figma metadata intake artifacts.

### Changed

- Repositioned the extension as the generic `intake` extension with domain commands for visual design, PRD, and test-case sources.
- Expanded the extension goal from Figma-only metadata intake to visual design requirement intake.
- Added support contracts for image, PDF, Markdown, and Figma sources across low, medium, and high-fidelity drafts.
- Added readiness concepts for source integrity, visual requirement traceability, fidelity rules, and delivery parity planning.
- Updated the validator to support generic visual sources while preserving Figma metadata parity validation.

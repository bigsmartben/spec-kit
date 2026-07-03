---
description: Capture or validate visual design intake for the active Spec Kit feature.
---

## User Input

```text
$ARGUMENTS
```

Classify the input before proceeding:

- `source`: image, PDF, Markdown design brief, Figma URL, file, page, frame, node, or exported design asset
- `intake_dir`: existing visual-design intake artifact directory
- `validation_request`: validate, check, gate, readiness, validate-spec-package, or validate-previews
- `asset_request`: build-spec-package, build-previews, downstream delivery asset request, preview coverage asset request, or CI-low-cost assertion asset request
- `review_guidance`: target platform, required fidelity, capture scope, source precedence, Figma-backed resource requirements, or reviewer instructions

## Goal

Create, update, or validate high-confidence provider-neutral structured UI/visual assets for the active Spec Kit feature. The structured UI/visual asset is the source of truth for this intake: it records pages, regions, components, states, styles, resources, and interaction cues from high-fidelity UI or visual design sources so downstream product specification, implementation, and acceptance workflows can consume source-backed visual facts.

Evidence chain and preview artifacts are supporting artifacts only: evidence supports confidence; preview supports human reading of page-component IA. Neither may create, override, or replace structured asset records.

Default artifact directory:

```text
specs/<feature>/intake/visual-design/
```

Normative authority:

- `templates/schemas/*.json` defines machine-readable structure, required fields, types, and enums.
- `scripts/python/validate_visual_design_intake.py` defines readiness evaluation and blocker emission for the core structured UI/visual asset.
- `scripts/python/capture_figma_metadata_shards.py` stages already-sharded Figma metadata captures into raw shard, index, and inventory artifacts.
- `scripts/python/validate_visual_spec_package.py` defines downstream structured visual spec package readiness after the core asset passes.
- `scripts/python/validate_visual_previews.py` defines supporting IA matrix preview and coverage readiness only for preview artifacts.
- `templates/intake-visual-design-contract.md` defines semantic extraction policy, fidelity policy, and provider evidence policy.
- `templates/intake-visual-spec-package-contract.md` defines the visual requirements/spec structured asset package.
- `templates/intake-visual-previews-contract.md` defines preview coverage helper artifact structure, boundaries, and blocker semantics.
- This command only performs input routing, context loading, capture orchestration, validation invocation, and reporting.

## Operating Boundaries

- Preserve original design sources and record checksums before extraction.
- For Figma sources, implementation resources, images, exported assets, and token refs must trace back to Figma source refs.
- Extract structured UI/visual asset records as traceable engineering input, not as unsupported prose summaries or downstream-specific schema projections.
- Treat `visual-spec-package/` as the downstream structured UI/visual asset package for delivery and CI-low-cost checks.
- Treat `previews/component-matrix-preview.html`, screenshots, and visual diffs as optional human-review helper evidence only, not the target deliverable.
- Treat `previews/component-coverage.yaml` and `previews/viewport-coverage.yaml` as structured coverage evidence for reviewer completeness checks; they may support readiness but do not replace `visual-spec-package/`.
- Do not place `visual-evidence-packet.md`, `visual-spec-evidence-packet.md`, `component-matrix-preview.html`, screenshots, visual diffs, or other preview artifacts in `source_refs` or `evidence_refs` as source-of-truth records. Use preview-specific helper fields such as `preview_refs` instead.
- Use bounded inference for dirty or incomplete design sources: observed claims are source-backed facts; inferred claims require explicit rules and high confidence; candidate claims are reference-only; unsupported claims must remain blocked.
- Mark low, medium, or high fidelity explicitly and apply the matching extraction rules.
- Use stable provider-neutral evidence IDs and source refs. Do not invent downstream-owned item IDs, requirement IDs, schema fields, code component names, or product semantics.
- Do not mark intake ready unless source integrity, source refs, fidelity rules, bounded inference checks, and intake parity plan pass the validator readiness gates.
- Preserve raw Figma metadata exactly in `figma-metadata.part-*.xml` for Figma sources.
- Do not request complete metadata for a broad Figma page, canvas, or board in one MCP response. Split large Figma scopes into smaller frame/component/node captures and stage them with `capture_figma_metadata_shards.py`.
- Do not modify application source, tests, package manifests, feature implementation files, or existing Spec Kit core templates.
- If required tooling is unavailable, create a blocked evidence packet that records the missing tool and stop before claiming readiness.

## Context Loading

1. Verify the current directory is a Spec Kit project by checking for `.specify/`, unless `$ARGUMENTS` points to a standalone artifact directory for extension development.
2. Identify the active feature:
   - Prefer `SPECIFY_FEATURE` when set.
   - Otherwise use the current Git branch name when it matches a directory under `specs/`.
   - Otherwise inspect `specs/` and choose the most recently modified feature directory only when exactly one feature directory exists.
   - If the feature cannot be identified and no standalone artifact directory was provided, stop and ask the user to set `SPECIFY_FEATURE` or run from the feature branch.
3. Read `.specify/extensions/intake/intake-config.yml` when present.
4. Read `templates/intake-visual-design-contract.md` and the referenced JSON Schemas from this extension before creating or validating artifacts.
5. Read any existing intake artifacts and preserve valid evidence unless the user explicitly asks to recapture it.

## Mode Routing

Apply routing precedence before executing a mode:

- If both a `source` and `build-spec-package` intent are present, run capture then validate first. Continue to Build spec package mode only when the updated visual-design intake validator returns `PASS`; otherwise stop and report the visual-design blockers.
- If both a `source` and `build-previews` intent are present, run capture then validate first. Continue to Build previews mode only when the updated visual-design intake validator returns `PASS`; otherwise stop and report the visual-design blockers.
- If build-spec-package, validate-spec-package, build-previews, or validate-previews intent is present without a resolvable source or existing intake directory, stop and ask for the visual-design intake directory.

- Capture mode: use when `$ARGUMENTS` names an image, PDF, Markdown design brief, Figma URL, frame, node, platform, fidelity level, or asks to capture, ingest, update, or recapture visual evidence.
- Build spec package mode: use when `$ARGUMENTS` includes `build-spec-package`, `with spec package`, `structured visual spec`, `CI-low-cost assertions`, or asks for downstream delivery/acceptance assets.
- Validate spec package mode: use when `$ARGUMENTS` includes `validate-spec-package`, `check spec package`, `visual spec readiness`, or only names an existing `visual-spec-package` directory.
- Build previews mode: use when `$ARGUMENTS` includes `build-previews`, `IA matrix`, `preview coverage`, `coverage review`, `component-coverage`, or `viewport-coverage`.
- Validate previews mode: use when `$ARGUMENTS` includes `validate-previews`, `check previews`, `preview readiness`, or only names an existing `previews` directory.
- Validate mode: use when `$ARGUMENTS` includes `validate`, `check`, `gate`, `readiness`, or only names an existing visual-design intake directory.
- Capture then validate: use when both a source and validation intent are present, or after capture artifacts are updated.

## Capture Procedure

1. Resolve the source from `$ARGUMENTS` or existing artifact metadata:
   - source type: `image`, `pdf`, `markdown`, or `figma`
   - source path, URL, file key, page, frame, node, region, or Markdown section scope
   - required fidelity: `low`, `medium`, or `high`
   - design version or timestamp
2. Create `design-source-manifest.yaml` with contract-required source identity, integrity, coverage, capture method, and fidelity fields.
3. Preserve file-based originals under `source-files/`; for remote or Figma sources, record stable URLs and exported screenshots or assets, or record a structured gap/blocker when unavailable.
4. For Figma sources, preserve raw provider evidence before deriving normalized requirements:
   - capture metadata in bounded node batches instead of one broad page/canvas response
   - store raw responses outside the target intake directory before staging; do not point `--metadata-source` at the target `visual-design/` directory
   - for multiple selected roots, pass `--node-id` once per root and avoid overlapping node scopes because duplicate or missing node parity blocks readiness
   - stage raw metadata files with:

```bash
python .specify/extensions/intake/scripts/python/capture_figma_metadata_shards.py <visual-design-intake-dir> \
  --metadata-source <raw-get-metadata-file-or-directory> \
  --file-url <figma-file-url> \
  --file-key <figma-file-key> \
  --page-id <figma-page-id> \
  --node-id <selected-root-node-id> \
  --overwrite
```

   - write raw metadata shards as `figma-metadata.part-NNN.xml`
   - build `figma-metadata.index.yaml`
   - build `figma-node-inventory.yaml`
   - validate metadata and inventory parity before deriving visual requirements
   - if any shard is truncated or lacks detectable node ids, keep the intake `BLOCKED` and retry with a smaller node scope or a direct file-based provider export
5. Extract source-specific evidence:
   - image: dimensions, regions, OCR status, visual hierarchy, assets, and region coverage
   - pdf: original file hash, page count, rendered page refs, text extraction status, and page coverage
   - markdown: heading structure, design notes, embedded or linked assets, and visual requirement mappings
   - figma: complete descendant metadata, node inventory, variables/styles/components, screenshots, and assets
6. Record source coverage and extraction gaps using `design-source-manifest.yaml`, `visual-requirements.yaml`, and `templates/intake-visual-design-contract.md`; do not define scenario categories in this command.
7. Build `visual-requirements.yaml` according to `templates/schemas/visual-requirements.schema.json` and the semantic policies in `templates/intake-visual-design-contract.md`.
   - Record direct facts as `evidence_type: observed`.
   - Promote only rule-backed, high-confidence derived claims to `evidence_type: inferred` with `inference_rule`, `confidence_method`, `score_breakdown`, `downstream_use: accepted_claim`, and `blocking_conditions`.
   - Keep low- or medium-confidence completions as `evidence_type: candidate` with `downstream_use: reference_only` and `missing_evidence`.
   - Record unsupported or conflicting claims as `evidence_type: unsupported` with `blocker_code`, `reason`, `missing_evidence`, and `blockers`.
8. For unavailable required evidence, record a structured gap or blocker instead of omitting the field. Do not infer business rules, permissions, form validation, error copy, dynamic states, data sources, analytics, security, or compliance behavior from visual appearance alone.
9. Create or update `visual-evidence-packet.md` from `templates/intake-visual-design-evidence-packet-template.md` with readiness front matter and human-readable evidence notes; keep structured records in `visual-requirements.yaml`. The evidence packet must summarize validator-backed confidence only and must not create, override, or replace structured asset records. Preserve an existing `figma-evidence-packet.md` only as a legacy compatibility alias when already configured by the host project.
10. Add an intake parity plan that records source-side comparison targets, methods, thresholds, accepted exceptions, and blocking difference categories without defining implementation capture artifacts or downstream delivery approval.
11. Run validation before reporting readiness.

## Visual Spec Package Procedure

1. Resolve the upstream visual-design intake directory and target `visual-spec-package/` directory.
2. Ensure visual-design intake passes readiness before building or validating the package:

```bash
python .specify/extensions/intake/scripts/python/validate_visual_design_intake.py <visual-design-intake-dir>
```

3. Create or update the `visual-spec-package/` artifact family according to `templates/intake-visual-spec-package-contract.md`, `templates/schemas/visual-spec-package.schema.json`, and `templates/schemas/visual-spec-assertions.schema.json`.
4. Keep provider/source traceability, downstream-ownership exclusions, assertion coverage, and optional preview helper refs aligned with the visual spec package contract. Do not restate or invent package fields in this command.
5. Do not use `component-matrix-preview.html` or preview rendering output as the source of truth for assets, tokens, product behavior, or requirements. Use source refs and structured visual-design intake records as authority.
6. Validate before reporting readiness:

```bash
python .specify/extensions/intake/scripts/python/validate_visual_spec_package.py <visual-spec-package-dir>
```

## Preview Coverage Procedure

1. Resolve the upstream visual-design intake directory and target `previews/` directory.
2. Ensure visual-design intake passes readiness before building or validating preview coverage:

```bash
python .specify/extensions/intake/scripts/python/validate_visual_design_intake.py <visual-design-intake-dir>
```

3. Create or update the `previews/` artifact family according to `templates/intake-visual-previews-contract.md`, `templates/schemas/component-coverage.schema.json`, and `templates/schemas/viewport-coverage.schema.json`.
4. Keep IA matrix structure, preview refs, interaction refs, source refs, screenshot/diff refs, missing coverage records, and known-gap semantics aligned with the preview contract. Do not restate or invent preview fields in this command.
5. Do not use preview HTML as a requirements source, implementation HTML, product semantic source, token source, or replacement for `visual-spec.yaml`.
6. Validate before reporting readiness:

```bash
python .specify/extensions/intake/scripts/python/validate_visual_previews.py <previews-dir>
```

## Validation Procedure

1. Resolve the visual-design intake directory from `$ARGUMENTS` or the active feature.
2. Run:

```bash
python .specify/extensions/intake/scripts/python/validate_visual_design_intake.py <intake-dir>
```

3. Prefer `--json` when a machine-readable result is needed. Report the validator result exactly:
   - `PASS` means the structured UI/visual asset passed JSON Schema structure checks and validator readiness checks, with evidence chain used only to support confidence.
   - `BLOCKED` means downstream workflows must keep design-derived requirements blocked, unresolved, or marked `[NEEDS CLARIFICATION]` instead of promoting unsupported design facts.

## Readiness Authority

Use this precedence when sources disagree:

1. JSON Schemas are canonical for structural validity in all modes.
2. `validate_visual_design_intake.py` is canonical for core structured UI/visual asset readiness status and blocker codes.
3. `validate_visual_spec_package.py` is canonical only for downstream visual spec package readiness status and blocker codes.
4. `validate_visual_previews.py` is canonical only for supporting preview coverage readiness status and blocker codes.
5. `templates/intake-visual-design-contract.md` is canonical for semantic extraction, fidelity, and provider evidence policy.
6. `templates/intake-visual-spec-package-contract.md` and `templates/intake-visual-previews-contract.md` are canonical for their artifact families.

Do not restate, reinterpret, or override blocker codes in this command.

## Report

Return:

- mode executed or sequence executed: capture, validate, capture_then_validate, build_spec_package, validate_spec_package, build_previews, validate_previews, or an ordered combination when source capture precedes build
- output or validated directory
- source type and source refs captured, or the recorded gap/blocker
- required fidelity, or the recorded gap/blocker
- source file count and processed count, or the recorded gap/blocker
- visual requirement count
- visual spec package item count when built or validated
- visual spec package assertion count and CI-low-cost assertion count when built or validated
- preview component coverage count and viewport coverage count when built or validated
- Figma-backed resource traceability result when source is Figma
- readiness result
- blocker lint errors
- next corrective action when blocked
- open questions that must remain `[NEEDS CLARIFICATION]`

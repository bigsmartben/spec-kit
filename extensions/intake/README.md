# Spec Kit Intake Extension

Extract, normalize, and validate SDD-ready intake artifacts from PRDs, visual designs, final static HTML delivery bundles, test cases, and other software sources before downstream Spec Kit workflows project them into requirements.

For visual intake, `/speckit.intake.visual-design` is the only external command. It internally captures source evidence, builds visual IR, asks user clarification questions when operation or visual behavior is under-specified, generates `delivery/index.html`, and validates the final static HTML delivery.

The visual intake goal is high-information source restoration: preserve original evidence, keep unsupported behavior explicit, and produce an offline-runnable static HTML artifact whose visual surfaces and user operations trace back to source evidence or user confirmation.

Intake artifacts are validated in two layers: JSON Schema checks enforce required structure, field types, and enums; readiness validators then check source integrity, traceability, hashes, clarification status, operation replay, assets, screenshots, visual diff records, and cross-file parity.

## Supported Intake Sources

- PRDs, product briefs, Markdown documents, PDFs, and exported docs
- Low-fidelity, medium-fidelity, and high-fidelity design drafts
- Static images such as PNG, JPG, WebP, and exported screens
- PDF design packs and annotated review documents
- Figma files, pages, frames, nodes, components, variables, and exported screenshots
- Final static HTML delivery bundles with visual IR, operation replay, motion anchors, viewport screenshots, and visual diff evidence
- Existing test cases, Gherkin files, QA exports, and test management spreadsheets

## Intake Scenario Coverage

| Domain | Vertical scenarios | Normalized artifact | Primary readiness focus |
| --- | --- | --- | --- |
| PRD | product briefs, Markdown PRDs, exported docs, PDFs, issue or epic links, mixed stakeholder notes | `prd-intake.yaml` | source identity, product intent traceability, scope boundaries, acceptance evidence, clarification gaps |
| Visual design | static images, wireframes, PDF design packs, Markdown design briefs, Figma files or selected nodes | `visual-requirements.yaml`, `visual-ir/`, `delivery/index.html` | source integrity, full resource traceability, layout/box restoration, component/page/state coverage, user-operation replay, motion anchors, viewport screenshots, visual diff readiness |
| Test cases | automated tests, Gherkin files, manual QA cases, spreadsheets, test management exports, bug or issue repro steps | `test-case-intake.yaml` | scenario traceability, assertion extraction, fixture evidence, coverage gaps, flaky or skipped case reporting |

Vertical instructions must not convert source evidence directly into downstream-owned requirement IDs, implementation tasks, or code component names.

## Commands

- `/speckit.intake.visual-design <source or intake dir or user answer>` orchestrates visual source capture, visual IR, user clarification, static HTML delivery generation, and delivery validation through one external command.
- `/speckit.intake.prd` captures or validates PRD evidence and normalizes product intent, scope, business rules, acceptance criteria, and clarification items.
- `/speckit.intake.test-cases` captures or validates test case evidence and normalizes scenarios, assertions, fixtures, and coverage gaps.

## Artifact Layout

```text
specs/<feature>/intake/
├── prd/
│   ├── source-manifest.yaml
│   ├── source-files/
│   ├── prd-intake.yaml
│   └── evidence-packet.md
├── visual-design/
│   ├── design-source-manifest.yaml
│   ├── source-files/
│   ├── visual-requirements.yaml
│   ├── figma-metadata.part-001.xml
│   ├── figma-metadata.index.yaml
│   ├── figma-node-inventory.yaml
│   ├── figma-normalized-tree.yaml
│   ├── visual-evidence-packet.md
│   ├── visual-ir/
│   │   ├── asset-inventory.yaml
│   │   ├── layout-tree.yaml
│   │   ├── component-model.yaml
│   │   ├── page-route-model.yaml
│   │   ├── interaction-model.yaml
│   │   ├── motion-anchor-model.yaml
│   │   └── clarification-log.yaml
│   └── delivery/
│       ├── index.html
│       ├── assets/
│       ├── screenshots/
│       ├── render-replay-report.yaml
│       └── evidence-packet.md
└── test-cases/
    ├── source-manifest.yaml
    ├── source-files/
    ├── test-case-intake.yaml
    └── evidence-packet.md
```

Figma metadata artifacts and `figma-normalized-tree.yaml` are required for Figma visual-design sources. Image, PDF, and Markdown visual-design sources use `design-source-manifest.yaml`, source-file checksums, visual requirements, visual IR, and delivery parity evidence.

Machine-readable JSON Schemas live under `templates/schemas/`. Static HTML delivery validation uses `templates/schemas/static-html-delivery.schema.json` and `scripts/python/validate_static_html_delivery.py`.

## Requirements

- Spec Kit `>=0.8.10.dev0`
- Python validator dependencies: `PyYAML` and `jsonschema`
- Optional: `figma-mcp` for Figma metadata capture

## Install for Local Development

From a Spec Kit project:

```bash
specify extension add --dev C:/Users/24598/Documents/github/spec-kit-intake
```

## Install from Release

From a Spec Kit project:

```bash
specify extension add intake --from https://github.com/bigsmartben/spec-kit-intake/archive/refs/tags/v0.2.0.zip
```

Release artifacts must include source-backed provenance for the `bigsmartben/spec-kit` integration fork. The release workflow uploads `release-provenance.json` with:

- `repository_url`
- `release_version`
- `source_commit_sha`
- `download_url`
- `validation_evidence`

Then run:

```text
/speckit.intake.visual-design <image|pdf|markdown|figma source, intake dir, or user confirmation answer>
/speckit.intake.prd capture <prd source and scope>
/speckit.intake.prd validate
/speckit.intake.test-cases capture <test source>
/speckit.intake.test-cases validate
```

## Visual Design Readiness Gate

Visual design intake passes only when:

- source identity, fidelity level, and source-file integrity are proven
- low, medium, or high-fidelity extraction rules are applied consistently
- extracted requirements preserve layout hierarchy, spacing, typography, color, assets, states, responsive behavior, and accessibility evidence at the fidelity level supplied
- non-observed visual claims use bounded inference fields and stay auditable
- candidate completions remain reference-only and unsupported claims emit blocker codes
- source-side parity evidence explains how final delivery output is compared with the original design artifact
- Figma sources pass raw metadata completeness, node-inventory parity, and layout normalization coverage
- no blocker lint errors exist

## Static HTML Delivery Readiness Gate

Static HTML delivery passes only when:

- upstream visual-design intake is ready
- all required visual IR artifacts exist and report `ready_gate: PASS`
- required user clarification questions are answered or explicitly out of scope
- `delivery/index.html` is static and offline-runnable
- all assets resolve under `delivery/assets/`
- every page, route state, component state, user operation, motion anchor, viewport, and visual diff record resolves through `render-replay-report.yaml`
- operation replay records have `replay_status: pass`
- required screenshots exist under `delivery/screenshots/`
- visual diff records are `pass`
- `delivery/evidence-packet.md` reports `ready_gate: PASS` with no blockers

The static HTML delivery validator emits blocker codes such as `STATIC_HTML_SOURCE_INTAKE_BLOCKED`, `STATIC_HTML_REQUIRED_ARTIFACT_MISSING`, `STATIC_HTML_SCHEMA_INVALID`, `STATIC_HTML_IR_BLOCKED`, `STATIC_HTML_CLARIFICATION_REQUIRED`, `STATIC_HTML_ASSET_INCOMPLETE`, `STATIC_HTML_OPERATION_REPLAY_INCOMPLETE`, `STATIC_HTML_MOTION_ANCHOR_INCOMPLETE`, `STATIC_HTML_VIEWPORT_CAPTURE_INCOMPLETE`, and `STATIC_HTML_VISUAL_DIFF_BLOCKED`.

## Development

Validate the manifest from the local `spec-kit` checkout:

```bash
python -c "from pathlib import Path; from specify_cli.extensions import ExtensionManifest; ExtensionManifest(Path('extension.yml')); print('manifest ok')"
```

Validate visual-design source artifacts:

```bash
python scripts/python/validate_visual_design_intake.py specs/<feature>/intake/visual-design
```

Validate static HTML delivery artifacts:

```bash
python scripts/python/validate_static_html_delivery.py specs/<feature>/intake/visual-design/delivery
```

Validate PRD artifacts:

```bash
python scripts/python/validate_prd_intake.py specs/<feature>/intake/prd
```

Validate test-case artifacts:

```bash
python scripts/python/validate_test_cases_intake.py specs/<feature>/intake/test-cases
```

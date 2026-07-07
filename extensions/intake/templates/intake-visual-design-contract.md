# Visual Design Intake Contract

Required visual design intake artifacts and readiness gates. The visual intake workflow captures design evidence, derives visual IR, asks the user to confirm missing operation semantics, and produces a final static HTML delivery.

Intake does not generate downstream requirement IDs, implementation tasks, code component names, or product-owned selectors. It restores design evidence into source-backed artifacts that downstream Spec Kit workflows can consume.

## Artifact Families

Default root:

```text
specs/<feature>/intake/visual-design/
```

Source intake artifacts:

- `design-source-manifest.yaml`
- `source-files/`
- `visual-requirements.yaml`
- `visual-evidence-packet.md`
- Figma sources: `figma-metadata.part-*.xml`, `figma-metadata.index.yaml`, `figma-node-inventory.yaml`, `figma-normalized-tree.yaml`

Visual IR artifacts:

- `visual-ir/asset-inventory.yaml`
- `visual-ir/layout-tree.yaml`
- `visual-ir/component-model.yaml`
- `visual-ir/page-route-model.yaml`
- `visual-ir/interaction-model.yaml`
- `visual-ir/motion-anchor-model.yaml`
- `visual-ir/clarification-log.yaml`

Static HTML delivery artifacts:

- `delivery/index.html`
- `delivery/assets/`
- `delivery/screenshots/`
- `delivery/render-replay-report.yaml`
- `delivery/evidence-packet.md`

JSON Schemas are canonical for field shapes. This contract defines semantic policy and readiness ownership.

## Supported Sources

`design-source-manifest.yaml` must identify the original design source and preserve source integrity.

Required source fields:

- `source_type: image|pdf|markdown|figma`
- `required_fidelity: low|medium|high`
- `source_files`
- `source_integrity_complete`
- `captured_at`
- `capture_method`
- `page_or_frame_count`
- `processed_count`
- `extraction_scope`

Source-specific requirements:

- Image sources record dimensions, region coverage, OCR status, and asset refs.
- PDF sources record original hash, page count, rendered pages, and text extraction status.
- Markdown sources record heading structure, embedded assets, linked assets, and design-note parsing status.
- Figma sources additionally satisfy the Figma provider contract.

## Fidelity Profile

- Low fidelity: page intent, rough hierarchy, major regions, rough content, interaction hints, and explicit gaps.
- Medium fidelity: low-fidelity facts plus key spacing, sizing, typography categories, color roles, assets, states, and responsive clues.
- High fidelity: medium-fidelity facts plus exact or bounded dimensions, spacing, typography, tokens, asset export contracts, component variants, page coverage, operation replay, and comparison thresholds.

The intake must record `fidelity_rules_applied: true`.

## Visual Requirements

`visual-requirements.yaml` records source-backed facts that seed the visual IR and delivery.

Each requirement must include:

- `id`
- `category: layout|spacing|sizing|typography|color|asset|component|state|interaction|responsive|accessibility|content`
- `requirement`
- `source_refs`
- `evidence_type: observed|inferred|candidate|unsupported|missing|out_of_scope`
- `confidence`
- `confidence_rationale`
- `engineering_action`
- `acceptance_check`
- `fidelity_level`

`source_refs` must point to original design sources, provider metadata, source files, or structured source-intake records. They must not point to delivery HTML, screenshots, visual diffs, evidence packets, or generated implementation artifacts as source-of-truth records.

## Bounded Inference

Visual intake may preserve direct observations, rule-backed inferred claims, and candidate completions. It must not smooth missing or contradictory evidence into confirmed behavior.

- `observed`: direct source-backed fact.
- `inferred`: high-confidence derived claim with `inference_rule`, `confidence_method`, `score_breakdown`, `downstream_use: accepted_claim`, and `blocking_conditions`.
- `candidate`: low/medium confidence completion with `downstream_use: reference_only` and `missing_evidence`.
- `unsupported`: rejected or blocked claim with `downstream_use: blocked`, `blocker_code`, `reason`, `missing_evidence`, and `blockers`.
- `missing` and `out_of_scope`: explicit absence or excluded surface.

Do not infer business rules, permissions, form validation, error copy, loading/disabled/focus states, data sources, analytics, security, compliance, route results, or animation timing without source evidence or user confirmation.

## Visual IR

Visual IR is the deterministic internal structure used to build the final static HTML. It is not a downstream implementation schema.

Every visual IR file must include:

- `ready_gate: PASS|BLOCKED`
- `blockers`
- source refs or upstream refs for every ready record

The visual IR must cover:

- assets/resources: full inventory, local delivery paths, checksums, usage refs, missing resources, substitutions
- layout/boxes: hierarchy, bounding boxes, constraints, z-order, overflow, scroll, responsive rules
- components/states/IA: component sets, instances, variants, props, visual states, accessibility expectations, state evidence, missing states
- pages/routes/IA: pages, route states, overlays, navigation targets, viewport variants, missing route behavior
- interactions: events, targets, preconditions, system feedback, state changes, route changes, exception branches, replay steps
- motion anchors: trigger, affected surface, initial/end state, duration, easing, delay, repeat behavior

## Clarification Gate

When evidence is missing and affects static HTML visual parity or user-operation replay, the command must ask the user instead of inventing behavior.

`visual-ir/clarification-log.yaml` must record each question:

- `id`
- `target_artifact`
- `blocked_delivery_surface`
- `blocker_code`
- `question`
- `allowed_answer_shape`
- `required_for_html`
- `status: unanswered|answered|out_of_scope`
- `answer`
- `confirmed_by_user`
- `source_refs`

Readiness is blocked when any required question is unanswered.

## Static HTML Delivery

`delivery/index.html` is the final delivery artifact. It must be static and offline-runnable. It may include embedded CSS and vanilla JavaScript to replay source-backed or user-confirmed operations.

Delivery readiness requires:

- all required source intake gates pass
- all required visual IR files exist and pass
- all required clarifications are answered or out of scope
- every page, route state, component state, operation, motion anchor, and viewport referenced by `render-replay-report.yaml` resolves to an anchor in `index.html`
- every required local asset resolves under `delivery/assets/`
- every required operation has replay evidence
- screenshots exist for required viewports
- visual diff records pass or are explicitly blocked
- `delivery/evidence-packet.md` front matter reports `ready_gate: PASS` with no blockers

## Figma Provider Contract

For `source_type: figma`, raw `get_metadata` output must be preserved in `figma-metadata.part-*.xml`.

Readiness requires:

- complete descendant subtree coverage for selected roots
- no truncated raw evidence
- `figma-metadata.index.yaml` proves source identity and shard integrity
- `figma-node-inventory.yaml` reconciles raw node count, exclusions, missing nodes, duplicates, and truncation
- `figma-normalized-tree.yaml` derives visual order without rewriting raw provider metadata

`figma-normalized-tree.yaml` may record only provider-neutral layout normalization fields. It must not include delivery refs, selectors, implementation tasks, code component names, route semantics, or product behavior.

## Blocker Codes

Source-intake blockers:

- `VISUAL_SOURCE_MANIFEST_MISSING`
- `VISUAL_SOURCE_TYPE_UNSUPPORTED`
- `VISUAL_FIDELITY_LEVEL_UNSUPPORTED`
- `VISUAL_SOURCE_FILE_MISSING`
- `VISUAL_SOURCE_HASH_MISMATCH`
- `VISUAL_SOURCE_INTEGRITY_INCOMPLETE`
- `VISUAL_REQUIREMENTS_MISSING`
- `VISUAL_REQUIREMENTS_UNTRACEABLE`
- `VISUAL_FIDELITY_RULES_MISSING`
- `VISUAL_PARITY_PLAN_MISSING`
- `VISUAL_READY_WITHOUT_EVIDENCE`
- `VISUAL_EVIDENCE_PACKET_MISSING`
- `VISUAL_BLOCKER_LINT_ERRORS`
- `VISUAL_INFERENCE_CONTRACT_INVALID`
- `VISUAL_SCHEMA_INVALID`

Figma blockers:

- `FIGMA_RAW_METADATA_MISSING`
- `FIGMA_RAW_METADATA_SUMMARY_SUBSTITUTION`
- `FIGMA_RAW_METADATA_TRUNCATED`
- `FIGMA_SELECTED_SUBTREE_INCOMPLETE`
- `FIGMA_METADATA_INDEX_MISSING`
- `FIGMA_METADATA_PARITY_FAILED`
- `FIGMA_READY_WITHOUT_COMPLETENESS_PROOF`
- `FIGMA_NORMALIZED_TREE_MISSING`
- `FIGMA_NORMALIZED_TREE_INCOMPLETE`
- `FIGMA_RENDER_NODE_MISMATCH`
- `FIGMA_HIDDEN_LAYER_POLLUTION`
- `FIGMA_NON_INSTANCE_COMPONENT`
- `FIGMA_PROTOTYPE_METADATA_MISSING`
- `FIGMA_UNSUPPORTED_STATE_INFERENCE`
- `FIGMA_BUSINESS_RULE_UNSUPPORTED`
- `FIGMA_INTERACTION_CONFLICT`
- `FIGMA_RESPONSIVE_RULE_MISSING`
- `FIGMA_LOW_CONFIDENCE_CANDIDATE`

Static delivery blockers are defined in `templates/intake-static-html-delivery-contract.md`.

## Evidence Packet Metadata

`visual-evidence-packet.md` and `delivery/evidence-packet.md` must start with YAML front matter:

- `ready_gate: PASS|BLOCKED`
- `blockers`
- `source_ref_count`
- `extracted_item_count`
- `generated_at`

Evidence packets summarize validator-backed readiness. They are not source-of-truth records.

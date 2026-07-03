# Visual Preview Coverage Contract

Required IA-matrix preview helper artifacts and readiness gates. Preview coverage artifacts help reviewers inspect whether design-source pages, components, visual states, component states, interaction events, resources, content samples, and viewports were enumerated before downstream implementation, but they are not the target visual requirements/spec asset package.

Preview coverage does not generate requirements, implementation HTML, product semantics, downstream-owned selectors, tasks, code component names, or design tokens. It preserves source-backed coverage evidence that points back to design-source refs and forward to `visual-spec-package/` records.

Preview coverage is assembled from the structured UI/visual asset and source-backed records. It must not create, override, replace, or backfill `visual-requirements.yaml`, `visual-spec.yaml`, or `visual-spec-assertions.yaml`; do not infer specifications from `component-matrix-preview.html`.

## Artifact Family

Default directory:

```text
specs/<feature>/intake/visual-design/previews/
```

Required files:

- `component-matrix-preview.html`
- `component-coverage.yaml`
- `viewport-coverage.yaml`
- `known-gaps.md`
- `screenshots/`

## Source Boundary

Preview coverage is downstream of visual-design intake and adjacent to the visual spec package:

1. Visual-design intake records source-backed facts, limitations, Figma metadata, node inventory, and visual requirements.
2. Visual Spec Package records the target structured visual requirements/spec facts.
3. Preview coverage records reviewer-oriented matrix surfaces and machine-readable coverage evidence.

If Figma or design-source evidence is missing, truncated, contradictory, or blocked, preview coverage must record a `VISUAL_PREVIEW_*` blocker and keep the affected coverage cell missing. Do not silently complete a missing state, variant, resource, or viewport in preview HTML.

## `component-matrix-preview.html`

The file is a human-review panel only. Each preview cell should expose stable anchors such as `id` or `data-preview-id` so `component-coverage.yaml` can reference the cell.

The preview panel must use an IA matrix structure that fuses interaction evidence into page and component review surfaces. Do not create a standalone interaction matrix that is disconnected from the visual states it exercises.

Required top-level order:

1. IA matrix overview for fused interactions.
2. For each required page:
   - page visual state enumeration
   - page IA matrix
3. For each required component:
   - component visual state enumeration
   - component IA matrix with event interaction information
4. Coverage evidence conclusion

The HTML must expose these stable section anchors so readiness can be checked:

- `data-preview-section="ia-matrix-overview"`
- `data-preview-section="page-state-enumeration"`
- `data-preview-section="page-ia-matrix"`
- `data-preview-section="component-state-enumeration"`
- `data-preview-section="component-ia-matrix"`
- `data-preview-section="coverage-evidence-conclusion"`

Each visual-state enumeration cell must render the state visually or point to source-backed screenshot evidence. A prose-only state row is a missing coverage cell unless the state is explicitly blocked or out of scope.

Each page IA matrix row must fuse the current interaction matrix information into the page state that owns it. Required IA fields:

- `page_region`
- `visual_state`
- `user_event`
- `precondition`
- `system_response`
- `state_change`
- `transition_or_overlay`
- `exception_branch`
- `evidence_ref`
- `coverage_status`

Each component IA matrix row must include event interaction information for the component state. Required IA fields:

- `component_state`
- `visible_elements`
- `action_target`
- `user_event`
- `precondition`
- `immediate_feedback`
- `state_change`
- `affected_surface`
- `disabled_or_error_rule`
- `evidence_ref`
- `coverage_status`

Use stable anchors such as `id`, `data-preview-id`, or `data-interaction-id` for every visual-state cell and IA matrix row that a coverage record references.

The preview panel may display:

- pages and page regions
- component sets and component instances
- variant props
- states
- page IA rows and component IA rows
- event, precondition, feedback, transition, exception, and return-path evidence
- size, density, and theme dimensions
- content samples, including long copy, empty, overflow, and error-like visual states when source-backed
- viewport-specific snapshots or links
- missing, blocked, and out-of-scope labels

The preview panel must not define product semantics, downstream component names, implementation selectors, design tokens, or source-backed facts that are absent from the design source.

## `component-coverage.yaml`

The file is the machine-readable component coverage evidence.

`source_ref` fields must point to original design sources, provider metadata, or structured asset records. Preview HTML, screenshots, visual diffs, and evidence packets may be referenced only by preview-specific or screenshot-specific fields.

Top-level fields:

- ready_gate: PASS|BLOCKED
- blockers: array of `VISUAL_PREVIEW_*` or allowed upstream `VISUAL_SPEC_*` blocker codes
- components: array

Each component must include:

- id
- source_ref
- name
- required_dimensions
- covered
- missing

Each covered record must include:

- visual_spec_ref
- preview_ref
- interaction_ref
- optional source_ref
- optional screenshot_refs
- dimension values matching the component's required dimensions when applicable

Each missing record must include:

- missing_type: state|variant|viewport|resource|asset|token|screenshot|visual_diff|source_evidence|visual_spec_ref|preview_ref
- reason
- blocker

## `viewport-coverage.yaml`

The file is the machine-readable viewport coverage evidence.

`source_refs` must point to original design sources, provider metadata, or structured asset records. `page_refs`, `screenshot_refs`, and diff outputs are supporting preview evidence and must not replace source refs.

Each viewport record must include:

- id
- width
- height
- covered
- source_refs
- visual_spec_refs
- page_refs
- screenshot_refs
- visual_diff_status: pass|blocked|not_applicable

Missing viewport evidence must stay explicit in `missing` records or top-level blockers.

## Readiness

Preview coverage is ready only when:

- upstream visual-design intake readiness is PASS
- required preview artifacts exist
- `component-coverage.yaml` validates against `component-coverage.schema.json`
- `viewport-coverage.yaml` validates against `viewport-coverage.schema.json`
- every covered component record has a `visual_spec_ref`
- every covered component record has a `preview_ref` that resolves inside `component-matrix-preview.html`
- every covered component record has an `interaction_ref` that resolves inside `component-matrix-preview.html`
- `component-matrix-preview.html` contains the required IA matrix sections and required IA field markers
- page refs in `viewport-coverage.yaml` resolve inside `component-matrix-preview.html`
- no missing record remains for required component states, variants, resources, assets, tokens, screenshots, visual diffs, source evidence, visual spec refs, or preview refs
- every viewport record is covered and has existing screenshot refs
- at least one viewport has page refs
- `known-gaps.md` has no unresolved `BLOCKED`, `UNRESOLVED`, or `TODO` marker

## Blocker Codes

- `VISUAL_PREVIEW_SOURCE_INTAKE_BLOCKED`
- `VISUAL_PREVIEW_REQUIRED_ARTIFACT_MISSING`
- `VISUAL_PREVIEW_SCHEMA_INVALID`
- `VISUAL_PREVIEW_FIGMA_NODE_COVERAGE_INCOMPLETE`
- `VISUAL_PREVIEW_COMPONENT_STATE_COVERAGE_INCOMPLETE`
- `VISUAL_PREVIEW_IA_MATRIX_INCOMPLETE`
- `VISUAL_PREVIEW_PAGE_COVERAGE_INCOMPLETE`
- `VISUAL_PREVIEW_ASSET_TRACEABILITY_INCOMPLETE`
- `VISUAL_PREVIEW_VIEWPORT_CAPTURE_INCOMPLETE`
- `VISUAL_PREVIEW_VISUAL_DIFF_BLOCKED`
- `VISUAL_PREVIEW_KNOWN_GAP_UNRESOLVED`

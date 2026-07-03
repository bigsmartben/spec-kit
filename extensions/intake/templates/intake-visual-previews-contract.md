# HTML Mock Delivery Contract

Required HTML mock equivalent delivery page and coverage readiness gates. `preview.html` is the static HTML/CSS mock equivalent for the visual input design, generated from upstream intake artifacts. It renders intake-backed pages, layout regions, components, visual states, interaction states, content samples, and viewport surfaces before downstream implementation. Coverage artifacts prove whether those rendered mock surfaces are traceable and complete, but they are not the target visual requirements/spec asset package.

HTML mock delivery does not generate requirements, production implementation HTML, product semantics, downstream-owned selectors, tasks, code component names, or design tokens. It preserves source-backed coverage evidence that points back to design-source refs and forward to `visual-spec-package/` records.

HTML mock delivery is assembled from the structured UI/visual asset, visual spec package records, coverage YAML, screenshot refs, and source-backed records. It must not create, override, replace, or backfill `visual-requirements.yaml`, `visual-spec.yaml`, or `visual-spec-assertions.yaml`; `preview.html` may implement only existing structured facts and explicit missing or blocked records as the HTML mock equivalent.

## Artifact Family

Default directory:

```text
specs/<feature>/intake/visual-design/previews/
```

Required files:

- `preview.html`
- `component-coverage.yaml`
- `viewport-coverage.yaml`
- `known-gaps.md`
- `screenshots/`

## Source Boundary

HTML mock delivery is downstream of visual-design intake and adjacent to the visual spec package:

1. Visual-design intake records source-backed facts, limitations, Figma metadata, node inventory, and visual requirements.
2. Visual Spec Package records the target structured visual requirements/spec facts.
3. HTML mock delivery records the generated visual-equivalent mock page plus machine-readable coverage evidence.

If Figma or design-source evidence is missing, truncated, contradictory, or blocked, HTML mock delivery must record a `VISUAL_PREVIEW_*` blocker and keep the affected coverage cell missing. Do not silently complete a missing state, variant, resource, viewport, or page behavior in preview HTML.

## `preview.html`

The file is the generated static HTML/CSS mock equivalent for UI intake. It implements the visual input design from upstream intake artifacts as rendered mock pages, regions, components, states, interaction surfaces, content samples, and viewport surfaces. Each visualized mock surface that coverage records reference must expose a stable anchor such as `id`, `data-preview-id`, or `data-interaction-id`.

The IA matrix is the coverage and interaction evidence layer for the HTML mock. Do not let IA matrix tables replace the visualized page and component mock surfaces, and do not create a standalone interaction matrix that is disconnected from the visual states it exercises.

Required top-level order:

1. Rendered mock page surfaces, including required page regions, component instances, content samples, and viewport-specific surfaces.
2. IA matrix overview for fused interactions.
3. For each required page:
   - page visual state enumeration
   - page IA matrix
4. For each required component:
   - component visual state enumeration
   - component IA matrix with event interaction information
5. Coverage evidence conclusion

The HTML must expose these stable section anchors so readiness can be checked:

- `data-preview-section="mock-page"`
- `data-preview-section="ia-matrix-overview"`
- `data-preview-section="page-state-enumeration"`
- `data-preview-section="page-ia-matrix"`
- `data-preview-section="component-state-enumeration"`
- `data-preview-section="component-ia-matrix"`
- `data-preview-section="coverage-evidence-conclusion"`

Each visual-state enumeration cell must render the state visually or point to source-backed screenshot evidence. A prose-only state row is a missing coverage cell unless the state is explicitly blocked or out of scope.

Stable anchors must be unambiguous. Values used in `id`, `data-preview-id`, or `data-interaction-id` must not resolve to multiple HTML elements.

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

Use stable anchors such as `id`, `data-preview-id`, or `data-interaction-id` for every visualized mock page, visualized component/state node, visual-state cell, and IA matrix row that a coverage record references. Component `preview_ref` values must resolve to visualized component or state nodes, not only explanatory text or IA matrix rows.

Every visualized component or state node referenced by `component-coverage.yaml` `preview_ref` must expose `data-preview-kind` with one of these values:

- `component`
- `component-state`
- `component-instance`
- `mock-component`
- `mock-component-state`
- `visual-state`

The preview page may display:

- rendered pages and page regions
- component sets and component instances as HTML/CSS mock nodes
- variant props
- states
- page IA rows and component IA rows
- event, precondition, feedback, transition, exception, and return-path evidence
- size, density, and theme dimensions
- content samples, including long copy, empty, overflow, and error-like visual states when source-backed
- viewport-specific snapshots or links
- missing, blocked, and out-of-scope labels

The preview page must not define product semantics, downstream component names, production implementation selectors, design tokens, or source-backed facts that are absent from upstream intake artifacts. Its equivalence is bounded by the validated intake facts and explicit missing or blocked records.

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

`visual_spec_ref` values must point to `../visual-spec-package/visual-spec.yaml#<item-id>` and resolve to existing `visual-spec-package/visual-spec.yaml` item IDs. `screenshot_refs`, when present, must resolve to existing files under the preview artifact directory.

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

HTML mock delivery is ready only when:

- upstream visual-design intake readiness is PASS
- adjacent `visual-spec-package/` readiness is PASS
- required preview artifacts exist
- `component-coverage.yaml` validates against `component-coverage.schema.json`
- `viewport-coverage.yaml` validates against `viewport-coverage.schema.json`
- every covered component record has a `visual_spec_ref`
- every covered component record has a `preview_ref` that resolves to a visualized mock component or state node inside `preview.html`
- every covered component record has an `interaction_ref` that resolves inside `preview.html`
- every covered component `visual_spec_ref` points to `visual-spec-package/visual-spec.yaml` and resolves to an existing item
- component screenshot refs resolve to existing files when present
- `preview.html` contains the required mock page section, IA matrix sections, and required IA field markers
- each page and component IA matrix row contains the full required IA field set
- preview anchors are unique across `id`, `data-preview-id`, and `data-interaction-id`
- page refs and visual spec refs in `viewport-coverage.yaml` resolve to mock page surfaces and visual spec items
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

# Static HTML Delivery Contract

Required final static HTML delivery artifacts and readiness gates for visual intake. This contract replaces the previous preview/mock interpretation: `delivery/index.html` is the final generated static HTML artifact for the submitted design source.

The delivery bundle must restore the design source as source-backed, offline-runnable HTML. It must render the visual design and replay user operations that are present in the source evidence or confirmed by the user. Missing source evidence must remain explicit through blockers and clarification questions.

## Artifact Family

Default directory:

```text
specs/<feature>/intake/visual-design/delivery/
```

Required files:

- `index.html`
- `assets/`
- `screenshots/`
- `render-replay-report.yaml`
- `evidence-packet.md`

Required adjacent visual IR files:

- `../visual-ir/asset-inventory.yaml`
- `../visual-ir/layout-tree.yaml`
- `../visual-ir/component-model.yaml`
- `../visual-ir/page-route-model.yaml`
- `../visual-ir/interaction-model.yaml`
- `../visual-ir/motion-anchor-model.yaml`
- `../visual-ir/clarification-log.yaml`

## Source Boundary

Static HTML delivery is downstream of visual-design source intake and visual IR:

1. Source intake preserves original design sources, provider metadata, checksums, source refs, and visual requirements.
2. Visual IR records assets, layout, boxes, components, pages, routes, states, interactions, motion anchors, and clarification decisions.
3. Static HTML delivery renders the IR into offline HTML and validates operation replay, viewport screenshots, and visual diff evidence.

The delivery bundle must not become a source-of-truth substitute for missing design evidence. When source evidence is incomplete, the delivery must render a visible blocked or unresolved surface and emit a `STATIC_HTML_*` blocker rather than inventing behavior.

## `index.html`

`index.html` must be static and offline-runnable. It may include embedded CSS and vanilla JavaScript for replaying source-backed or user-confirmed states, routes, interactions, and motion anchors.

Required HTML anchors:

- `data-delivery-root`
- `data-visual-id`
- `data-page-id`
- `data-route-id`
- `data-component-id`
- `data-state-id`
- `data-operation-id`
- `data-motion-id` when motion records exist

Every page, route state, component state, interaction target, operation result, and motion surface referenced by `render-replay-report.yaml` must resolve to an element in `index.html` with the matching anchor namespace. Page refs resolve through `id`, `data-page-id`, or `data-route-id`; component refs resolve through `id`, `data-component-id`, or `data-state-id`; operation targets resolve through `id`, `data-operation-id`, or `data-component-id`; motion refs resolve through `id`, `data-motion-id`, `data-state-id`, or `data-component-id`; visual asset refs resolve through `id` or `data-visual-id`.

The HTML must render actual UI surfaces first. Evidence tables, reports, or summaries may appear after rendered UI surfaces, but they must not replace rendered pages, components, states, or interaction surfaces.

## Visual IR Expectations

`asset-inventory.yaml` must record:

- `ready_gate`
- `blockers`
- `assets`
- each asset id, source refs, local path when available, role, media type, hash status, usage refs, and replacement/blocker status

`layout-tree.yaml` must record:

- `ready_gate`
- `blockers`
- pages/frames, regions, boxes, coordinates, z-order, scroll/overflow, responsive constraints, and source refs

`component-model.yaml` must record:

- `ready_gate`
- `blockers`
- components, instances, variants, props, visual states, state source refs, accessibility expectations, and missing states

`page-route-model.yaml` must record:

- `ready_gate`
- `blockers`
- pages, routes, IA regions, route states, overlays, navigation targets, responsive viewports, and missing route behavior

`interaction-model.yaml` must record:

- `ready_gate`
- `blockers`
- operations, event targets, user events, preconditions, feedback, state changes, route changes, exception branches, and replay steps

`motion-anchor-model.yaml` must record:

- `ready_gate`
- `blockers`
- motion anchors, triggers, affected surfaces, initial/end states, duration, easing, delay, repeat behavior, and source refs

`clarification-log.yaml` must record:

- `ready_gate`
- `blockers`
- questions
- each question id, target artifact, blocked delivery surface, blocker code, allowed answer shape, status, answer, source/user confirmation refs, and whether it is required for HTML readiness
- `blocker_code` must be a `STATIC_HTML_*` blocker code, `status` must be `unanswered|answered|out_of_scope`, answered required questions must include `answer` and `confirmed_by_user: true`, and report clarification counts must match this log.

## `render-replay-report.yaml`

`render-replay-report.yaml` is the machine-readable readiness record for static HTML delivery.

Required top-level fields:

- `ready_gate: PASS|BLOCKED`
- `blockers`
- `html_entry`
- `source_intake_ref`
- `visual_ir_refs`
- `assets`
- `pages`
- `components`
- `operations`
- `motion_anchors`
- `viewports`
- `visual_diffs`
- `clarifications`

Each asset record must include:

- `id`
- `inventory_ref`
- `html_refs`
- `local_paths`
- `source_refs`
- `status: covered|blocked|out_of_scope`
- `blockers`

Each page record must include:

- `id`
- `route`
- `html_ref`
- `state_refs`
- `layout_refs`
- `source_refs`
- `status`
- `blockers`

Each component record must include:

- `id`
- `component_model_ref`
- `html_ref`
- `state_refs`
- `operation_refs`
- `source_refs`
- `status`
- `blockers`

Each operation record must include:

- `id`
- `interaction_model_ref`
- `event`
- `target_ref`
- `result_ref`
- `precondition`
- `replay_status: pass|blocked|not_applicable`
- `source_refs`
- `blockers`

Each motion record must include:

- `id`
- `motion_model_ref`
- `trigger_ref`
- `affected_ref`
- `end_state_ref`
- `replay_status: pass|blocked|not_applicable`
- `source_refs`
- `blockers`

Each viewport record must include:

- `id`
- `width`
- `height`
- `page_refs`
- `screenshot_refs`
- `render_status: pass|blocked`
- `blockers`

Each visual diff record must include:

- `id`
- `source_ref`
- `screenshot_ref`
- `status: pass|blocked`
- `thresholds`
- `diff_summary`
- `blockers`

Clarification summary must include:

- `required_question_count`
- `answered_required_question_count`
- `unanswered_required_question_ids`

## Readiness

Static HTML delivery is ready only when:

- upstream visual-design intake readiness is `PASS`
- every required visual IR artifact exists
- every visual IR artifact has `ready_gate: PASS`
- `visual_ir_refs` exactly matches the required visual IR file set, `source_intake_ref` resolves to upstream intake evidence, and every `inventory_ref`, `layout_ref`, `state_ref`, `component_model_ref`, `interaction_model_ref`, and `motion_model_ref` resolves to a real visual IR record
- all required clarification questions are answered or explicitly out of scope
- `index.html` exists and contains `data-delivery-root`
- every `html_ref`, `target_ref`, `result_ref`, `trigger_ref`, `affected_ref`, and `page_ref` resolves inside `index.html` with the expected anchor namespace
- all local asset paths resolve under `delivery/assets/`
- every required component, component state, page state, route state, operation, motion anchor, and viewport is covered or blocked explicitly
- every required operation has `replay_status: pass`
- every source-backed motion anchor has `replay_status: pass` or is explicitly out of scope
- every required viewport has an existing screenshot
- visual diff records are `pass`; unavailable source comparison must be recorded as `STATIC_HTML_VISUAL_DIFF_BLOCKED` and keeps readiness blocked
- `evidence-packet.md` front matter reports `ready_gate: PASS` with no blockers

## Blocker Codes

- `STATIC_HTML_SOURCE_INTAKE_BLOCKED`
- `STATIC_HTML_REQUIRED_ARTIFACT_MISSING`
- `STATIC_HTML_SCHEMA_INVALID`
- `STATIC_HTML_IR_BLOCKED`
- `STATIC_HTML_CLARIFICATION_REQUIRED`
- `STATIC_HTML_ASSET_INCOMPLETE`
- `STATIC_HTML_LAYOUT_INCOMPLETE`
- `STATIC_HTML_COMPONENT_STATE_INCOMPLETE`
- `STATIC_HTML_PAGE_ROUTE_INCOMPLETE`
- `STATIC_HTML_OPERATION_REPLAY_INCOMPLETE`
- `STATIC_HTML_MOTION_ANCHOR_INCOMPLETE`
- `STATIC_HTML_VIEWPORT_CAPTURE_INCOMPLETE`
- `STATIC_HTML_VISUAL_DIFF_BLOCKED`
- `STATIC_HTML_READY_WITHOUT_EVIDENCE`

---
description: Orchestrate visual intake into a source-backed static HTML delivery for the active Spec Kit feature.
---

## User Input

```text
$ARGUMENTS
```

Treat this command as the only external visual-intake entrypoint. Do not expose or require user-facing subcommands. `$ARGUMENTS` may contain a design source, an existing visual-intake directory, reviewer guidance, fidelity constraints, platform constraints, or answers to previously emitted clarification questions.

## Goal

Produce a final static HTML delivery that can be opened offline and that restores the submitted design source as faithfully as the available evidence allows:

- visual parity with the design source
- complete asset/resource traceability
- layout and box-model reconstruction
- component inventory with exhaustive source-backed states
- page, route, and information-architecture state coverage
- user-operation replay coverage
- motion/event anchors with source-backed timing or explicit blockers

The final delivery artifact is:

```text
specs/<feature>/intake/visual-design/delivery/index.html
```

The command must continue internally until the delivery is `PASS` or until a stable blocker requires user confirmation, missing source access, or unavailable tooling.

## Normative Authority

- JSON Schemas under `templates/schemas/` define machine-readable structure.
- `templates/intake-visual-design-contract.md` defines source intake, visual IR, clarification, static HTML delivery, and readiness policy.
- `templates/intake-static-html-delivery-contract.md` defines the static HTML delivery contract.
- `scripts/python/validate_visual_design_intake.py` validates core source integrity and source-backed visual requirements.
- `scripts/python/validate_static_html_delivery.py` validates the static HTML delivery bundle.
- Figma helpers (`capture_figma_metadata_shards.py` and `normalize_figma_layout.py`) preserve raw provider evidence and derive deterministic layout order before visual IR extraction.

This command routes and orchestrates. Contracts, schemas, and validators own artifact structure and readiness decisions.

## Artifact Family

Default directory:

```text
specs/<feature>/intake/visual-design/
```

Required source artifacts:

- `design-source-manifest.yaml`
- `source-files/`
- `visual-requirements.yaml`
- `visual-evidence-packet.md`
- Figma sources additionally require raw metadata, node inventory, and `figma-normalized-tree.yaml`

Required visual IR artifacts:

- `visual-ir/asset-inventory.yaml`
- `visual-ir/layout-tree.yaml`
- `visual-ir/component-model.yaml`
- `visual-ir/page-route-model.yaml`
- `visual-ir/interaction-model.yaml`
- `visual-ir/motion-anchor-model.yaml`
- `visual-ir/clarification-log.yaml`

Required static HTML delivery artifacts:

- `delivery/index.html`
- `delivery/assets/`
- `delivery/screenshots/`
- `delivery/render-replay-report.yaml`
- `delivery/evidence-packet.md`

## Operating Boundaries

- Preserve original sources and checksums before extraction.
- Build visual IR from source-backed evidence only. Do not invent product behavior, hidden states, routes, animation timing, data validation, permissions, analytics, or business rules from visual appearance.
- Use user confirmation to resolve missing operational behavior, route transitions, interaction outcomes, responsive rules, resource substitution, or animation details.
- Record each question in `visual-ir/clarification-log.yaml` with a stable `CQ-*` id, target artifact, blocker code, status, and whether the answer is required for static HTML readiness.
- When `$ARGUMENTS` answers prior questions, update the clarification log and the affected IR artifact before rebuilding delivery.
- Candidate completions may be rendered only when explicitly labeled as blocked/reference-only in the delivery and evidence. They cannot satisfy readiness.
- The final HTML must be static: no backend, no build step, no network-only asset dependency, and no runtime dependency that prevents offline inspection.
- Vanilla JavaScript may be embedded when needed to replay user operations, route state, component state, overlays, forms, or motion anchors.
- Do not modify application source, package manifests, feature implementation files, or Spec Kit core templates.
- Do not create downstream-owned requirement IDs, code component names, production selectors, implementation tasks, or product semantics.

## Internal Workflow

Run these phases internally. Do not ask the user to invoke a phase name.

### 1. Resolve Context

1. Verify a Spec Kit workspace by checking for `.specify/`, unless `$ARGUMENTS` points to a standalone artifact directory.
2. Resolve the active feature from `SPECIFY_FEATURE`, the current branch, or the only feature directory under `specs/`.
3. Load `.specify/extensions/intake/intake-config.yml` when present.
4. Load this extension's visual contracts and schemas before writing artifacts.
5. Read existing visual artifacts and preserve valid source-backed evidence.

### 2. Capture Source Evidence

1. Resolve source type: `image`, `pdf`, `markdown`, or `figma`.
2. Create or update `design-source-manifest.yaml` and preserve source files under `source-files/`.
3. For Figma, capture bounded raw metadata shards and derive `figma-normalized-tree.yaml` only after metadata parity passes.
4. Update `visual-requirements.yaml` with source-backed visual facts, bounded inference status, and source-side parity plan.
5. Run `validate_visual_design_intake.py`.

If source intake is blocked, stop and report validator blocker codes plus the next concrete recovery action.

### 3. Build Visual IR

Create or update the required files under `visual-ir/`:

- asset inventory: every font, raster, vector, icon, color resource, media resource, external dependency, local copy path, hash, and substitution gap
- layout tree: page/frame hierarchy, layers, groups, boxes, coordinates, constraints, z-order, overflow, scroll regions, and responsive rules
- component model: component identity, instances, variants, props, visual states, state evidence, accessibility expectations, and missing states
- page-route model: pages, route states, IA regions, navigation targets, overlays, modals, drawers, empty/error/loading states, and viewport variants
- interaction model: user events, targets, preconditions, state changes, route changes, feedback, exception branches, and replay steps
- motion anchor model: trigger, event anchor, affected surface, initial state, end state, duration, easing, delay, repeat behavior, and source refs
- clarification log: unanswered questions, answered confirmations, assumptions, and blockers

### 4. Clarification Gate

Before building `delivery/index.html`, scan visual IR for missing information that affects visual parity or operation replay.

Emit `ready_gate: BLOCKED` with `next_action: USER_CONFIRMATION_REQUIRED` when any required confirmation is unanswered. Ask concise, concrete questions. Each question must name:

- `question_id`
- `target_artifact`
- `blocked_delivery_surface`
- `blocker_code`
- `allowed_answer_shape`

Do not continue to final delivery readiness while required questions are unanswered.

### 5. Build Static HTML Delivery

Generate or update `delivery/index.html` from validated source intake and visual IR.

The HTML must:

- render all required pages, regions, layout boxes, component instances, component states, page states, routes, overlays, and viewport surfaces
- include local asset references under `delivery/assets/` unless an explicitly blocked resource gap exists
- expose stable anchors using `id`, `data-visual-id`, `data-component-id`, `data-state-id`, `data-route-id`, `data-operation-id`, and `data-motion-id`
- implement user-operation replay with static HTML/CSS/vanilla JS when operation behavior is source-backed or user-confirmed
- expose blocked or unresolved surfaces visibly without substituting guessed behavior
- avoid evidence tables replacing the rendered UI; evidence may follow the rendered surfaces but cannot be the only representation

### 6. Validate Delivery

Run:

```bash
python .specify/extensions/intake/scripts/python/validate_static_html_delivery.py <visual-design-intake-dir>/delivery
```

The validator is canonical for static HTML delivery readiness. Prefer `--json` when machine-readable output is needed.

Delivery is ready only when:

- source intake is `PASS`
- required visual IR artifacts exist and have no readiness blockers
- all required clarification questions are answered or marked out of scope with source-backed rationale
- `delivery/index.html` exists and contains required static delivery anchors
- all local assets resolve under `delivery/assets/` or are recorded as blockers
- component, page, route, interaction, motion, and viewport coverage records resolve to rendered HTML anchors
- operation replay steps resolve to event targets and expected result surfaces
- screenshots exist for required viewports
- visual diff status is `pass`; unavailable source comparison must be recorded as `STATIC_HTML_VISUAL_DIFF_BLOCKED` and keeps readiness blocked
- `delivery/evidence-packet.md` reports `ready_gate: PASS` with no blockers

### 7. Report

Return:

- resolved directory
- source type and source refs captured
- fidelity level
- internal workflow phases completed
- visual IR readiness summary
- clarification status and unanswered question count
- static HTML path
- asset count and missing asset count
- page/route/state/component/operation/motion counts
- viewport screenshot count
- visual diff result
- readiness result
- blocker codes
- next corrective action when blocked

Use exact blocker codes from validators and schemas. Keep unresolved gaps as `[NEEDS CLARIFICATION]` rather than converting them into requirements.

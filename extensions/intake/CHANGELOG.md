# Changelog

## [0.2.0] - 2026-07-07

### Breaking Reset

- Rebuilt `/speckit.intake.visual-design` as the only external visual-intake entrypoint. Workflow phases are internal orchestration only; users do not invoke visual subcommands.
- Removed legacy preview/mock and visual spec package delivery surfaces from the extension source. The final visual deliverable is now `specs/<feature>/intake/visual-design/delivery/index.html`.
- Replaced preview/spec-package readiness with static HTML delivery readiness across `README.md`, `extension.yml`, `config-template.yml`, contracts, schemas, validators, and tests.

### Added

- Added `templates/intake-static-html-delivery-contract.md` as the static HTML delivery contract.
- Added `templates/schemas/static-html-delivery.schema.json` for `delivery/render-replay-report.yaml`.
- Added `scripts/python/validate_static_html_delivery.py` for static HTML delivery readiness.
- Added validator checks for visual IR readiness, exact `visual_ir_refs` parity, IR fragment resolution, source-intake ref resolution, typed HTML anchor namespaces, clarification-log structure, asset resolution, operation replay, motion anchors, viewport screenshots, visual diffs, and delivery evidence packets.

### Changed

- Visual intake now requires source-backed visual IR artifacts for assets/resources, layout/boxes, component states, page/route/IA states, user-operation replay, motion/event anchors, and clarification questions.
- Static delivery readiness now blocks when user-confirmed operation behavior, route behavior, responsive rules, resource substitutions, or motion timing is missing.
- Source refs now reject generated delivery HTML, delivery screenshots, visual diff outputs, and evidence packets as source-of-truth records.

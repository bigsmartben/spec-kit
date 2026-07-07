import os
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "python" / "validate_visual_design_intake.py"
PRD_VALIDATOR = ROOT / "scripts" / "python" / "validate_prd_intake.py"
TEST_CASE_VALIDATOR = ROOT / "scripts" / "python" / "validate_test_cases_intake.py"
STATIC_HTML_DELIVERY_VALIDATOR = ROOT / "scripts" / "python" / "validate_static_html_delivery.py"
FIGMA_METADATA_CAPTURE = ROOT / "scripts" / "python" / "capture_figma_metadata_shards.py"
FIGMA_LAYOUT_NORMALIZE = ROOT / "scripts" / "python" / "normalize_figma_layout.py"


def write_visual_intake_fixture(intake: Path, source_type: str, fidelity: str, file_name: str):
    intake.mkdir(parents=True, exist_ok=True)
    source_dir = intake / "source-files"
    source_dir.mkdir()
    source = source_dir / file_name
    source.write_bytes(f"{source_type}:{fidelity}:source".encode("utf-8"))

    import hashlib

    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    rel_source = f"source-files/{file_name}"
    if source_type == "image":
        source_details = [
            "source_details:",
            "  image_dimensions:",
            "    width_px: 100",
            "    height_px: 100",
            "  region_coverage: full",
            "  ocr_status: not_applicable",
        ]
    elif source_type == "pdf":
        source_details = [
            "source_details:",
            "  page_count: 1",
            "  processed_page_count: 1",
            "  rendered_page_refs:",
            f"    - {rel_source}#page=1",
            "  text_extraction_status: complete",
        ]
    elif source_type == "markdown":
        source_details = [
            "source_details:",
            "  heading_structure:",
            "    - Design brief",
            "  embedded_or_linked_asset_refs: []",
            "  design_note_parsing_status: complete",
        ]
    elif source_type == "figma":
        source_details = [
            "source_details:",
            "  file_url: https://www.figma.com/file/example",
            "  file_key: example",
            "  selected_node_ids:",
            "    - '1'",
        ]
    else:
        source_details = []

    (intake / "design-source-manifest.yaml").write_text(
        "\n".join(
            [
                f"source_type: {source_type}",
                f"required_fidelity: {fidelity}",
                "source_integrity_complete: true",
                "captured_at: '2026-06-23T00:00:00Z'",
                "capture_method: local_fixture",
                "page_or_frame_count: 1",
                "processed_count: 1",
                "extraction_scope: full",
                "source_files:",
                f"  - path: {rel_source}",
                "    mime_type: application/octet-stream",
                f"    byte_size: {source.stat().st_size}",
                f"    sha256: {digest}",
                "    role: original",
                *source_details,
                "",
            ]
        ),
        encoding="utf-8",
    )

    (intake / "visual-requirements.yaml").write_text(
        "\n".join(
            [
                "visual_requirements_complete: true",
                "visual_requirements_count: 1",
                "source_refs_complete: true",
                "fidelity_rules_applied: true",
                "visual_parity_plan_complete: true",
                "blocker_lint_errors: []",
                "parity_plan:",
                "  comparison_targets:",
                "    - primary_surface",
                f"  original_refs: ['{rel_source}#full']",
                "  comparison_method: manual_review",
                "  thresholds:",
                "    manual_review_checklist:",
                "      - compare primary hierarchy",
                "  accepted_exceptions: []",
                "  blocking_difference_categories:",
                "    - missing_required_visual_fact",
                "requirements:",
                "  - id: VR-001",
                "    category: layout",
                "    requirement: Preserve primary content hierarchy",
                f"    source_refs: ['{rel_source}#full']",
                "    evidence_type: observed",
                "    confidence: high",
                "    confidence_rationale: Source artifact directly shows the primary hierarchy.",
                "    engineering_action: Implement matching hierarchy",
                "    acceptance_check: Compare implementation screenshot with source",
                f"    fidelity_level: {fidelity}",
                "",
            ]
        ),
        encoding="utf-8",
    )

    (intake / "visual-evidence-packet.md").write_text(
        "---\n"
        "ready_gate: PASS\n"
        "blockers: []\n"
        "source_ref_count: 1\n"
        "extracted_item_count: 1\n"
        "generated_at: '2026-06-23T00:00:00Z'\n"
        "---\n"
        "# Visual Design Evidence Packet\n",
        encoding="utf-8",
    )


def write_figma_metadata_fixture(intake: Path):
    import hashlib

    metadata = intake / "figma-metadata.part-001.xml"
    metadata.write_text(
        '<figma><node id="1" name="Root"><node id="2" name="Save button" /></node></figma>\n',
        encoding="utf-8",
    )
    digest = hashlib.sha256(metadata.read_bytes()).hexdigest()
    (intake / "figma-metadata.index.yaml").write_text(
        "\n".join(
            [
                "file_url: https://www.figma.com/file/example",
                "file_key: example",
                "page_id: page-1",
                "selected_node_ids: ['1']",
                "captured_at: '2026-06-23T00:00:00Z'",
                "mcp_tool: get_metadata",
                "design_version_or_timestamp: '2026-06-23T00:00:00Z'",
                "selected_subtree_complete: true",
                "raw_metadata_complete: true",
                "expected_root_node_ids: ['1']",
                "captured_root_node_ids: ['1']",
                "missing_root_node_ids: []",
                "gap_count: 0",
                "gaps: []",
                "shards:",
                "  - path: figma-metadata.part-001.xml",
                f"    byte_size: {metadata.stat().st_size}",
                f"    sha256: {digest}",
                "    root_node_ids: ['1']",
                "    node_count: 2",
                "    truncated: false",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (intake / "figma-node-inventory.yaml").write_text(
        "\n".join(
            [
                "raw_node_count: 2",
                "inventory_node_count: 2",
                "excluded_node_count: 0",
                "missing_node_count: 0",
                "duplicate_node_count: 0",
                "truncated_raw_evidence: false",
                "node_inventory_coverage: 100%",
                "parity_passed: true",
                "",
            ]
        ),
        encoding="utf-8",
    )
    write_figma_normalized_tree_fixture(intake, ["1", "2"])


def write_figma_normalized_tree_fixture(intake: Path, source_node_ids=None):
    source_node_ids = source_node_ids or ["1"]
    nodes = []
    for index, node_id in enumerate(source_node_ids, start=1):
        parent_id = source_node_ids[0] if index > 1 else None
        nodes.append(
            {
                "source_node_id": str(node_id),
                "parent_source_node_id": parent_id,
                "original_name": "Root" if index == 1 else f"Node {node_id}",
                "normalized_name": "Root" if index == 1 else f"Node {node_id}",
                "node_type": "node",
                "role_hint": "node",
                "group_key": f"{index:04d}-node-{str(node_id).replace(':', '-')}",
                "parent_group_key": "0001-node-1" if parent_id else None,
                "sort_key": {
                    "method": "top_to_bottom_left_to_right_depth_sibling_id",
                    "value": [0, 0, index - 1, index - 1, str(node_id)],
                },
                "visual_order": index,
                "source_refs": [f"figma-metadata.part-001.xml#node={node_id}"],
            }
        )
    (intake / "figma-normalized-tree.yaml").write_text(
        yaml.safe_dump(
            {
                "normalization_complete": True,
                "source_metadata_refs": ["figma-metadata.part-001.xml"],
                "source_index_ref": "figma-metadata.index.yaml",
                "source_inventory_ref": "figma-node-inventory.yaml",
                "normalization_rules_applied": [
                    "rename: preserve source_node_id and original_name while writing normalized_name",
                    "grouper: group_key and parent_group_key mirror source containment",
                    "re-sort: visual_order follows top-to-bottom left-to-right source order",
                ],
                "rename_rule": "preserve source_node_id and original_name",
                "group_rule": "derive group_key without changing source identity",
                "sort_rule": "top_to_bottom_left_to_right_depth_sibling_id",
                "raw_node_count": len(source_node_ids),
                "normalized_node_count": len(source_node_ids),
                "node_coverage": "100%",
                "selected_node_ids": [str(source_node_ids[0])] if source_node_ids else [],
                "gaps": [],
                "nodes": nodes,
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
def write_prd_intake_fixture(intake: Path):
    intake.mkdir(parents=True, exist_ok=True)
    source_dir = intake / "source-files"
    source_dir.mkdir()
    source = source_dir / "feature-prd.md"
    source.write_text("# Feature PRD\n\nUsers can save draft content.\n", encoding="utf-8")

    import hashlib

    digest = hashlib.sha256(source.read_bytes()).hexdigest()

    (intake / "source-manifest.yaml").write_text(
        "\n".join(
            [
                "source_type: markdown",
                "source_integrity_complete: true",
                "captured_at: '2026-06-23T00:00:00Z'",
                "capture_method: local_fixture",
                "document_version: fixture-v1",
                "extraction_scope: full",
                "source_files:",
                "  - path: source-files/feature-prd.md",
                "    mime_type: text/markdown",
                f"    byte_size: {source.stat().st_size}",
                f"    sha256: {digest}",
                "    role: original",
                "source_details:",
                "  heading_coverage: full",
                "  parsed_section_coverage: full",
                "  linked_asset_refs: []",
                "",
            ]
        ),
        encoding="utf-8",
    )

    (intake / "prd-intake.yaml").write_text(
        "\n".join(
            [
                "prd_intake_complete: true",
                "source_refs_complete: true",
                "extracted_fact_count: 1",
                "acceptance_evidence_complete: true",
                "unresolved_ambiguity_marked: true",
                "acceptance_gaps: []",
                "open_questions:",
                "  - '[NEEDS CLARIFICATION] Pricing rules are outside this fixture.'",
                "blocker_lint_errors: []",
                "facts:",
                "  - id: PI-001",
                "    category: acceptance",
                "    statement: Users can save draft content.",
                "    source_refs: ['source-files/feature-prd.md#L3']",
                "    evidence_type: observed",
                "    confidence: high",
                "    confidence_rationale: Source statement directly describes the accepted behavior.",
                "    downstream_hint: candidate_acceptance_input",
                "    acceptance_or_validation_signal: Draft save behavior is explicitly stated.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    (intake / "evidence-packet.md").write_text(
        "---\n"
        "ready_gate: PASS\n"
        "blockers: []\n"
        "source_ref_count: 1\n"
        "extracted_item_count: 1\n"
        "generated_at: '2026-06-23T00:00:00Z'\n"
        "---\n"
        "# PRD Evidence Packet\n",
        encoding="utf-8",
    )


def write_test_case_intake_fixture(intake: Path):
    intake.mkdir(parents=True, exist_ok=True)
    source_dir = intake / "source-files"
    source_dir.mkdir()
    source = source_dir / "test_feature.py"
    source.write_text("def test_save_draft():\n    assert True\n", encoding="utf-8")

    import hashlib

    digest = hashlib.sha256(source.read_bytes()).hexdigest()

    (intake / "source-manifest.yaml").write_text(
        "\n".join(
            [
                "source_type: code",
                "source_integrity_complete: true",
                "captured_at: '2026-06-23T00:00:00Z'",
                "capture_method: local_fixture",
                "framework_or_format: pytest",
                "execution_scope: unit",
                "source_files:",
                "  - path: source-files/test_feature.py",
                "    mime_type: text/x-python",
                f"    byte_size: {source.stat().st_size}",
                f"    sha256: {digest}",
                "    role: original",
                "source_details:",
                "  test_names:",
                "    - test_save_draft",
                "  execution_status: passed",
                "  skipped_markers: []",
                "  fixture_refs:",
                "    - local pytest fixture",
                "",
            ]
        ),
        encoding="utf-8",
    )

    (intake / "test-case-intake.yaml").write_text(
        "\n".join(
            [
                "test_case_intake_complete: true",
                "source_refs_complete: true",
                "scenario_count: 1",
                "assertions_complete: true",
                "fixture_evidence_complete: true",
                "coverage_gaps_recorded: true",
                "assertion_gaps: []",
                "fixture_or_test_data_gaps: []",
                "coverage_gaps:",
                "  - Error-state coverage is not present in the fixture.",
                "flaky_or_skipped_cases: []",
                "blocker_lint_errors: []",
                "scenarios:",
                "  - id: TC-001",
                "    category: unit",
                "    scenario: Saving draft content succeeds.",
                "    source_refs: ['source-files/test_feature.py#L1']",
                "    evidence_type: observed",
                "    confidence: high",
                "    confidence_rationale: Test source directly exercises the scenario.",
                "    actors: ['registered_user']",
                "    preconditions: ['draft content exists']",
                "    actions: ['save draft']",
                "    expected_outcomes: ['draft is persisted']",
                "    assertions: ['save path returns success']",
                "    fixtures_or_test_data: ['local pytest fixture']",
                "    coverage_signal: happy_path_present_error_path_missing",
                "",
            ]
        ),
        encoding="utf-8",
    )

    (intake / "evidence-packet.md").write_text(
        "---\n"
        "ready_gate: PASS\n"
        "blockers: []\n"
        "source_ref_count: 1\n"
        "extracted_item_count: 1\n"
        "generated_at: '2026-06-23T00:00:00Z'\n"
        "---\n"
        "# Test Case Evidence Packet\n",
        encoding="utf-8",
    )


def write_image_visual_intake_fixture(intake: Path):
    write_visual_intake_fixture(intake, "image", "low", "wireframe.png")


def write_static_html_delivery_fixture(delivery_dir: Path):
    visual_intake = delivery_dir.parent
    write_visual_intake_fixture(visual_intake, "figma", "high", "figma-source.txt")
    write_figma_metadata_fixture(visual_intake)
    ir_dir = visual_intake / "visual-ir"
    ir_dir.mkdir(parents=True, exist_ok=True)
    delivery_dir.mkdir(parents=True, exist_ok=True)
    assets = delivery_dir / "assets"
    screenshots = delivery_dir / "screenshots"
    assets.mkdir(exist_ok=True)
    screenshots.mkdir(exist_ok=True)
    (assets / "logo.svg").write_text("<svg xmlns=\"http://www.w3.org/2000/svg\" />\n", encoding="utf-8")
    (screenshots / "home-desktop.png").write_bytes(b"fake-png")

    ir_common = "ready_gate: PASS\nblockers: []\n"
    (ir_dir / "asset-inventory.yaml").write_text(
        ir_common
        + "assets:\n"
        + "  - id: asset-logo\n"
        + "    source_refs: [figma://node/asset-logo]\n"
        + "    local_path: ../delivery/assets/logo.svg\n",
        encoding="utf-8",
    )
    (ir_dir / "layout-tree.yaml").write_text(
        ir_common
        + "boxes:\n"
        + "  - id: box-home\n"
        + "    source_refs: [figma://node/1]\n",
        encoding="utf-8",
    )
    (ir_dir / "component-model.yaml").write_text(
        ir_common
        + "components:\n"
        + "  - id: cmp-save\n"
        + "    states: [default, submitted]\n"
        + "    source_refs: [figma://node/2]\n",
        encoding="utf-8",
    )
    (ir_dir / "page-route-model.yaml").write_text(
        ir_common
        + "pages:\n"
        + "  - id: page-home\n"
        + "    route: /\n"
        + "    source_refs: [figma://node/1]\n",
        encoding="utf-8",
    )
    (ir_dir / "interaction-model.yaml").write_text(
        ir_common
        + "operations:\n"
        + "  - id: op-save\n"
        + "    event: click\n"
        + "    target_ref: delivery/index.html#save-button\n"
        + "    result_ref: delivery/index.html#save-result\n",
        encoding="utf-8",
    )
    (ir_dir / "motion-anchor-model.yaml").write_text(
        ir_common
        + "motion_anchors:\n"
        + "  - id: motion-save-feedback\n"
        + "    trigger_ref: delivery/index.html#save-button\n"
        + "    affected_ref: delivery/index.html#save-result\n"
        + "    end_state_ref: delivery/index.html#save-result\n",
        encoding="utf-8",
    )
    (ir_dir / "clarification-log.yaml").write_text(
        ir_common + "questions: []\n",
        encoding="utf-8",
    )

    (delivery_dir / "index.html").write_text(
        '<main data-delivery-root>'
        '<section data-page-id="page-home" data-route-id="route-home" data-visual-id="box-home">'
        '<img data-visual-id="asset-logo" src="assets/logo.svg" alt="Logo">'
        '<button id="save-button" data-component-id="cmp-save" data-state-id="cmp-save-default" '
        'data-operation-id="op-save" data-motion-id="motion-save-feedback">Save</button>'
        '<output id="save-result" data-state-id="cmp-save-submitted" aria-live="polite">Saved</output>'
        "</section>"
        "</main>",
        encoding="utf-8",
    )
    (delivery_dir / "render-replay-report.yaml").write_text(
        "\n".join(
            [
                "ready_gate: PASS",
                "blockers: []",
                "html_entry: index.html",
                "source_intake_ref: ../visual-requirements.yaml",
                "visual_ir_refs:",
                "  - ../visual-ir/asset-inventory.yaml",
                "  - ../visual-ir/layout-tree.yaml",
                "  - ../visual-ir/component-model.yaml",
                "  - ../visual-ir/page-route-model.yaml",
                "  - ../visual-ir/interaction-model.yaml",
                "  - ../visual-ir/motion-anchor-model.yaml",
                "  - ../visual-ir/clarification-log.yaml",
                "assets:",
                "  - id: asset-logo",
                "    inventory_ref: ../visual-ir/asset-inventory.yaml#asset-logo",
                "    html_refs: [index.html#asset-logo]",
                "    local_paths: [assets/logo.svg]",
                "    source_refs: [figma://node/asset-logo]",
                "    status: covered",
                "    blockers: []",
                "pages:",
                "  - id: page-home",
                "    route: /",
                "    html_ref: index.html#page-home",
                "    state_refs: [../visual-ir/page-route-model.yaml#page-home]",
                "    layout_refs: [../visual-ir/layout-tree.yaml#box-home]",
                "    source_refs: [figma://node/1]",
                "    status: covered",
                "    blockers: []",
                "components:",
                "  - id: cmp-save",
                "    component_model_ref: ../visual-ir/component-model.yaml#cmp-save",
                "    html_ref: index.html#cmp-save",
                "    state_refs: [../visual-ir/component-model.yaml#cmp-save-default]",
                "    operation_refs: [op-save]",
                "    source_refs: [figma://node/2]",
                "    status: covered",
                "    blockers: []",
                "operations:",
                "  - id: op-save",
                "    interaction_model_ref: ../visual-ir/interaction-model.yaml#op-save",
                "    event: click",
                "    target_ref: index.html#save-button",
                "    result_ref: index.html#save-result",
                "    precondition: enabled",
                "    replay_status: pass",
                "    source_refs: [figma://node/2]",
                "    blockers: []",
                "motion_anchors:",
                "  - id: motion-save-feedback",
                "    motion_model_ref: ../visual-ir/motion-anchor-model.yaml#motion-save-feedback",
                "    trigger_ref: index.html#save-button",
                "    affected_ref: index.html#save-result",
                "    end_state_ref: index.html#save-result",
                "    replay_status: pass",
                "    source_refs: [figma://prototype/save-feedback]",
                "    blockers: []",
                "viewports:",
                "  - id: desktop",
                "    width: 1440",
                "    height: 900",
                "    page_refs: [index.html#page-home]",
                "    screenshot_refs: [screenshots/home-desktop.png]",
                "    render_status: pass",
                "    blockers: []",
                "visual_diffs:",
                "  - id: diff-desktop",
                "    source_ref: figma://node/1",
                "    screenshot_ref: screenshots/home-desktop.png",
                "    status: pass",
                "    thresholds:",
                "      max_pixel_diff_percent: 0.5",
                "    diff_summary:",
                "      pixel_diff_percent: 0",
                "    blockers: []",
                "clarifications:",
                "  required_question_count: 0",
                "  answered_required_question_count: 0",
                "  unanswered_required_question_ids: []",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (delivery_dir / "evidence-packet.md").write_text(
        "---\n"
        "ready_gate: PASS\n"
        "blockers: []\n"
        "source_ref_count: 1\n"
        "extracted_item_count: 6\n"
        "generated_at: '2026-07-01T00:00:00Z'\n"
        "---\n"
        "# Static HTML Delivery Evidence Packet\n",
        encoding="utf-8",
    )


def test_manifest_loads_with_spec_kit_checkout():
    spec_kit_src = ROOT.parent / "spec-kit" / "src"
    if not spec_kit_src.exists():
        pytest.skip("spec-kit checkout not available next to extension")

    env = os.environ.copy()
    env["PYTHONPATH"] = str(spec_kit_src)

    code = (
        "from pathlib import Path; "
        "from specify_cli.extensions import ExtensionManifest; "
        "m=ExtensionManifest(Path('extension.yml')); "
        "assert m.id == 'intake'; "
        "assert len(m.commands) == 3; "
        "assert {c['name'] for c in m.commands} == {'speckit.intake.visual-design', 'speckit.intake.prd', 'speckit.intake.test-cases'}; "
        "assert m.hooks"
    )

    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0, result.stderr


def test_config_template_matches_extension_defaults():
    extension = yaml.safe_load((ROOT / "extension.yml").read_text(encoding="utf-8-sig"))
    config = yaml.safe_load((ROOT / "config-template.yml").read_text(encoding="utf-8"))

    defaults = extension["defaults"]
    assert defaults["artifacts"] == config["artifacts"]
    assert defaults["readiness"] == config["readiness"]
    assert defaults["capture"] == config["capture"]


def test_manifest_declared_files_exist():
    extension = yaml.safe_load((ROOT / "extension.yml").read_text(encoding="utf-8-sig"))

    for command in extension["provides"]["commands"]:
        assert (ROOT / command["file"]).exists(), command["file"]
    for config in extension["provides"].get("config", []):
        assert (ROOT / config["template"]).exists(), config["template"]

    for value in extension["defaults"]["artifacts"].values():
        if not isinstance(value, str):
            continue
        if value.startswith(("commands/", "templates/", "scripts/python/")):
            assert (ROOT / value).exists(), value


def test_release_provenance_contract_is_documented_and_generated():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    workflow = (ROOT / ".github" / "workflows" / "extension-artifact.yml").read_text(encoding="utf-8")
    for field in [
        "repository_url",
        "release_version",
        "source_commit_sha",
        "download_url",
        "validation_evidence",
    ]:
        assert field in readme
        assert field in workflow
    assert "release-provenance.json" in workflow


def test_readme_release_url_matches_extension_version():
    extension = yaml.safe_load((ROOT / "extension.yml").read_text(encoding="utf-8-sig"))
    version = extension["extension"]["version"]
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert f"archive/refs/tags/v{version}.zip" in readme


def test_static_html_delivery_schema_and_validator_paths_are_declared():
    extension = ROOT / "extension.yml"
    config = ROOT / "config-template.yml"
    for document in (extension.read_text(encoding="utf-8-sig"), config.read_text(encoding="utf-8")):
        assert "scripts/python/validate_static_html_delivery.py" in document
        assert "templates/intake-static-html-delivery-contract.md" in document
        assert "templates/schemas/static-html-delivery.schema.json" in document
        assert "scripts/python/validate_visual_previews.py" not in document
        assert "templates/intake-visual-previews-contract.md" not in document

    assert STATIC_HTML_DELIVERY_VALIDATOR.exists()
    assert (ROOT / "templates" / "intake-static-html-delivery-contract.md").exists()
    assert (ROOT / "templates" / "schemas" / "static-html-delivery.schema.json").exists()


def test_visual_design_command_is_single_entrypoint():
    command = (ROOT / "commands" / "speckit.intake.visual-design.md").read_text(encoding="utf-8")

    assert "build-previews" not in command
    assert "validate-previews" not in command
    assert "build-html-mock" not in command
    assert "validate-html-mock" not in command
    assert "Do not expose or require user-facing subcommands" in command


def test_visual_spec_package_paths_are_not_declared_as_static_html_authority():
    extension = ROOT / "extension.yml"
    config = ROOT / "config-template.yml"
    for document in (extension.read_text(encoding="utf-8-sig"), config.read_text(encoding="utf-8")):
        assert "visual-spec-package" not in document
        assert "validate_visual_spec_package.py" not in document


def test_figma_layout_normalization_schema_and_script_paths_are_declared():
    extension = ROOT / "extension.yml"
    config = ROOT / "config-template.yml"
    for document in (extension.read_text(encoding="utf-8-sig"), config.read_text(encoding="utf-8")):
        assert "scripts/python/normalize_figma_layout.py" in document
        assert "templates/schemas/figma-normalized-tree.schema.json" in document
        assert "figma-normalized-tree.yaml" in document
        assert "require_figma_layout_normalization_for_figma" in document

    assert FIGMA_LAYOUT_NORMALIZE.exists()
    assert (ROOT / "templates" / "schemas" / "figma-normalized-tree.schema.json").exists()


def test_validator_blocks_missing_directory():
    result = subprocess.run(
        [sys.executable, str(VALIDATOR), "missing-dir"],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 1
    assert "VISUAL_SOURCE_MANIFEST_MISSING" in result.stdout
    assert "VISUAL_REQUIREMENTS_MISSING" in result.stdout
    assert "VISUAL_EVIDENCE_PACKET_MISSING" in result.stdout


def test_prd_validator_blocks_missing_directory():
    result = subprocess.run(
        [sys.executable, str(PRD_VALIDATOR), "missing-dir"],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 1
    assert "PRD_SOURCE_MANIFEST_MISSING" in result.stdout
    assert "PRD_INTAKE_MISSING" in result.stdout
    assert "PRD_EVIDENCE_PACKET_MISSING" in result.stdout


def test_test_case_validator_blocks_missing_directory():
    result = subprocess.run(
        [sys.executable, str(TEST_CASE_VALIDATOR), "missing-dir"],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 1
    assert "TEST_SOURCE_MANIFEST_MISSING" in result.stdout
    assert "TEST_CASE_INTAKE_MISSING" in result.stdout
    assert "TEST_EVIDENCE_PACKET_MISSING" in result.stdout


@pytest.mark.parametrize(
    ("source_type", "fidelity", "file_name"),
    [
        ("image", "low", "wireframe.png"),
        ("pdf", "medium", "design-pack.pdf"),
        ("markdown", "high", "design-brief.md"),
    ],
)
def test_validator_passes_visual_source_matrix(source_type, fidelity, file_name):
    work_dir = ROOT / ".tmp" / f"test-validator-{source_type}-{fidelity}"
    if work_dir.exists():
        shutil.rmtree(work_dir)
    intake = work_dir / "visual-design"
    write_visual_intake_fixture(intake, source_type, fidelity, file_name)

    result = subprocess.run(
        [sys.executable, str(VALIDATOR), str(intake)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "Visual design intake readiness: PASS" in result.stdout

    shutil.rmtree(work_dir)

def test_visual_validator_allows_remote_source_gap_but_blocks_integrity():
    work_dir = ROOT / ".tmp" / "test-validator-remote-source-gap"
    if work_dir.exists():
        shutil.rmtree(work_dir)
    intake = work_dir / "visual-design"
    write_visual_intake_fixture(intake, "figma", "high", "figma-source.txt")

    (intake / "design-source-manifest.yaml").write_text(
        "\n".join(
            [
                "source_type: figma",
                "required_fidelity: high",
                "source_integrity_complete: false",
                "captured_at: '2026-07-01T00:00:00Z'",
                "capture_method: figma_url",
                "page_or_frame_count: 1",
                "processed_count: 1",
                "extraction_scope: selected_node",
                "snapshot_status: not_available",
                "integrity_gap_reason: Figma source URL was provided without a local export snapshot.",
                "retrieval_metadata:",
                "  retrieved_at: '2026-07-01T00:00:00Z'",
                "  stable_url: https://www.figma.com/file/example",
                "  visible_title: Fixture design",
                "source_files:",
                "  - path: figma://file/example",
                "    mime_type: application/x-figma",
                "    checksum_status: unavailable",
                "    role: original",
                "source_details:",
                "  file_url: https://www.figma.com/file/example",
                "  file_key: example",
                "  selected_node_ids:",
                "    - '1'",
                "",
            ]
        ),
        encoding="utf-8",
    )

    result = subprocess.run(
        [sys.executable, str(VALIDATOR), "--json", str(intake)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert "VISUAL_SOURCE_INTEGRITY_INCOMPLETE" in payload["blockers"]
    assert "VISUAL_SCHEMA_INVALID" not in payload["blockers"]
    assert "VISUAL_SOURCE_FILE_MISSING" not in payload["blockers"]
    assert payload["details"]["source_files"][0]["remote_ref"] is True

    shutil.rmtree(work_dir)


def test_prd_validator_passes_complete_minimal_intake():
    work_dir = ROOT / ".tmp" / "test-prd-validator-pass"
    if work_dir.exists():
        shutil.rmtree(work_dir)
    intake = work_dir / "prd"
    write_prd_intake_fixture(intake)

    result = subprocess.run(
        [sys.executable, str(PRD_VALIDATOR), str(intake)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "PRD intake readiness: PASS" in result.stdout

    shutil.rmtree(work_dir)


def test_prd_validator_allows_remote_source_gap_but_blocks_integrity():
    work_dir = ROOT / ".tmp" / "test-prd-validator-remote-source-gap"
    if work_dir.exists():
        shutil.rmtree(work_dir)
    intake = work_dir / "prd"
    write_prd_intake_fixture(intake)

    (intake / "source-manifest.yaml").write_text(
        "\n".join(
            [
                "source_type: url",
                "source_integrity_complete: false",
                "captured_at: '2026-07-01T00:00:00Z'",
                "capture_method: remote_url",
                "document_version: remote-v1",
                "extraction_scope: full",
                "snapshot_status: not_available",
                "integrity_gap_reason: Source URL was accessible but no local snapshot was provided.",
                "retrieval_metadata:",
                "  retrieved_at: '2026-07-01T00:00:00Z'",
                "  stable_url: https://example.com/prd",
                "  visible_title: Remote PRD",
                "  author_or_owner: product",
                "source_files:",
                "  - path: https://example.com/prd",
                "    mime_type: text/html",
                "    checksum_status: unavailable",
                "    role: original",
                "",
            ]
        ),
        encoding="utf-8",
    )

    result = subprocess.run(
        [sys.executable, str(PRD_VALIDATOR), "--json", str(intake)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert "PRD_SOURCE_INTEGRITY_INCOMPLETE" in payload["blockers"]
    assert "PRD_READY_WITHOUT_EVIDENCE" in payload["blockers"]
    assert "PRD_SCHEMA_INVALID" not in payload["blockers"]
    assert "PRD_SOURCE_FILE_MISSING" not in payload["blockers"]
    assert payload["details"]["source_files"][0]["remote_ref"] is True

    shutil.rmtree(work_dir)


def test_prd_validator_blocks_untraceable_facts():
    work_dir = ROOT / ".tmp" / "test-prd-validator-untraceable"
    if work_dir.exists():
        shutil.rmtree(work_dir)
    intake = work_dir / "prd"
    write_prd_intake_fixture(intake)

    text = (intake / "prd-intake.yaml").read_text(encoding="utf-8")
    text = text.replace("source_refs_complete: true", "source_refs_complete: false")
    text = text.replace("source_refs: ['source-files/feature-prd.md#L3']", "source_refs: []")
    (intake / "prd-intake.yaml").write_text(text, encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(PRD_VALIDATOR), "--json", str(intake)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert "PRD_FACTS_UNTRACEABLE" in payload["blockers"]
    assert "PRD_READY_WITHOUT_EVIDENCE" in payload["blockers"]
    assert "PRD_SCHEMA_INVALID" in payload["blockers"]
    assert payload["details"]["schema_validation"]["prd_intake"]["valid"] is False

    shutil.rmtree(work_dir)


def test_prd_validator_blocks_invalid_confidence_enum():
    work_dir = ROOT / ".tmp" / "test-prd-validator-confidence"
    if work_dir.exists():
        shutil.rmtree(work_dir)
    intake = work_dir / "prd"
    write_prd_intake_fixture(intake)

    text = (intake / "prd-intake.yaml").read_text(encoding="utf-8")
    text = text.replace("    confidence: high", "    confidence: certain")
    (intake / "prd-intake.yaml").write_text(text, encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(PRD_VALIDATOR), "--json", str(intake)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert "PRD_SCHEMA_INVALID" in payload["blockers"]
    assert payload["details"]["schema_validation"]["prd_intake"]["valid"] is False

    shutil.rmtree(work_dir)


@pytest.mark.parametrize(
    (
        "kind",
        "writer",
        "validator",
        "artifact",
        "source_refs_line",
        "schema_blocker",
        "detail_key",
    ),
    [
        (
            "prd",
            write_prd_intake_fixture,
            PRD_VALIDATOR,
            "prd-intake.yaml",
            "    source_refs: ['source-files/feature-prd.md#L3']",
            "PRD_SCHEMA_INVALID",
            "prd_intake",
        ),
        (
            "test-case",
            write_test_case_intake_fixture,
            TEST_CASE_VALIDATOR,
            "test-case-intake.yaml",
            "    source_refs: ['source-files/test_feature.py#L1']",
            "TEST_SCHEMA_INVALID",
            "test_case_intake",
        ),
        (
            "visual",
            write_image_visual_intake_fixture,
            VALIDATOR,
            "visual-requirements.yaml",
            "    source_refs: ['source-files/wireframe.png#full']",
            "VISUAL_SCHEMA_INVALID",
            "visual_requirements",
        ),
    ],
)
def test_validators_require_string_source_refs(
    kind,
    writer,
    validator,
    artifact,
    source_refs_line,
    schema_blocker,
    detail_key,
):
    work_dir = ROOT / ".tmp" / f"test-{kind}-validator-numeric-source-ref"
    if work_dir.exists():
        shutil.rmtree(work_dir)
    intake = work_dir / kind
    writer(intake)

    path = intake / artifact
    text = path.read_text(encoding="utf-8")
    text = text.replace(source_refs_line, "    source_refs: [123]")
    path.write_text(text, encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(validator), "--json", str(intake)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert schema_blocker in payload["blockers"]
    assert payload["details"]["schema_validation"][detail_key]["valid"] is False

    shutil.rmtree(work_dir)


@pytest.mark.parametrize(
    (
        "kind",
        "writer",
        "validator",
        "artifact",
        "anchor_line",
        "schema_blocker",
        "detail_key",
    ),
    [
        (
            "prd",
            write_prd_intake_fixture,
            PRD_VALIDATOR,
            "prd-intake.yaml",
            "    acceptance_or_validation_signal: Draft save behavior is explicitly stated.",
            "PRD_SCHEMA_INVALID",
            "prd_intake",
        ),
        (
            "test-case",
            write_test_case_intake_fixture,
            TEST_CASE_VALIDATOR,
            "test-case-intake.yaml",
            "    coverage_signal: happy_path_present_error_path_missing",
            "TEST_SCHEMA_INVALID",
            "test_case_intake",
        ),
        (
            "visual",
            write_image_visual_intake_fixture,
            VALIDATOR,
            "visual-requirements.yaml",
            "    fidelity_level: low",
            "VISUAL_SCHEMA_INVALID",
            "visual_requirements",
        ),
    ],
)
def test_validators_reject_unknown_blocker_codes(
    kind,
    writer,
    validator,
    artifact,
    anchor_line,
    schema_blocker,
    detail_key,
):
    work_dir = ROOT / ".tmp" / f"test-{kind}-validator-unknown-blocker"
    if work_dir.exists():
        shutil.rmtree(work_dir)
    intake = work_dir / kind
    writer(intake)

    path = intake / artifact
    text = path.read_text(encoding="utf-8")
    text = text.replace(anchor_line, f"{anchor_line}\n    blockers: [NOT_A_BLOCKER]")
    path.write_text(text, encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(validator), "--json", str(intake)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert schema_blocker in payload["blockers"]
    assert payload["details"]["schema_validation"][detail_key]["valid"] is False

    shutil.rmtree(work_dir)


@pytest.mark.parametrize(
    (
        "kind",
        "writer",
        "validator",
        "artifact",
        "rationale_line",
        "schema_blocker",
    ),
    [
        (
            "prd",
            write_prd_intake_fixture,
            PRD_VALIDATOR,
            "prd-intake.yaml",
            "    confidence_rationale: Source statement directly describes the accepted behavior.\n",
            "PRD_SCHEMA_INVALID",
        ),
        (
            "test-case",
            write_test_case_intake_fixture,
            TEST_CASE_VALIDATOR,
            "test-case-intake.yaml",
            "    confidence_rationale: Test source directly exercises the scenario.\n",
            "TEST_SCHEMA_INVALID",
        ),
        (
            "visual",
            write_image_visual_intake_fixture,
            VALIDATOR,
            "visual-requirements.yaml",
            "    confidence_rationale: Source artifact directly shows the primary hierarchy.\n",
            "VISUAL_SCHEMA_INVALID",
        ),
    ],
)
def test_validators_require_confidence_rationale(
    kind,
    writer,
    validator,
    artifact,
    rationale_line,
    schema_blocker,
):
    work_dir = ROOT / ".tmp" / f"test-{kind}-validator-missing-confidence-rationale"
    if work_dir.exists():
        shutil.rmtree(work_dir)
    intake = work_dir / kind
    writer(intake)

    path = intake / artifact
    text = path.read_text(encoding="utf-8")
    text = text.replace(rationale_line, "")
    path.write_text(text, encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(validator), "--json", str(intake)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert schema_blocker in payload["blockers"]

    shutil.rmtree(work_dir)


@pytest.mark.parametrize(
    (
        "kind",
        "writer",
        "validator",
        "artifact",
        "count_line",
        "blocker",
        "detail_key",
        "match_key",
    ),
    [
        (
            "prd",
            write_prd_intake_fixture,
            PRD_VALIDATOR,
            "prd-intake.yaml",
            "extracted_fact_count: 1",
            "PRD_INTAKE_MISSING",
            "prd_intake",
            "count_matches_facts",
        ),
        (
            "test-case",
            write_test_case_intake_fixture,
            TEST_CASE_VALIDATOR,
            "test-case-intake.yaml",
            "scenario_count: 1",
            "TEST_CASE_INTAKE_MISSING",
            "test_case_intake",
            "count_matches_scenarios",
        ),
        (
            "visual",
            write_image_visual_intake_fixture,
            VALIDATOR,
            "visual-requirements.yaml",
            "visual_requirements_count: 1",
            "VISUAL_REQUIREMENTS_MISSING",
            "visual_requirements",
            "count_matches_requirements",
        ),
    ],
)
def test_validators_block_declared_count_mismatch(
    kind,
    writer,
    validator,
    artifact,
    count_line,
    blocker,
    detail_key,
    match_key,
):
    work_dir = ROOT / ".tmp" / f"test-{kind}-validator-count-mismatch"
    if work_dir.exists():
        shutil.rmtree(work_dir)
    intake = work_dir / kind
    writer(intake)

    path = intake / artifact
    text = path.read_text(encoding="utf-8")
    text = text.replace(count_line, count_line.replace(": 1", ": 2"))
    path.write_text(text, encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(validator), "--json", str(intake)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert blocker in payload["blockers"]
    assert payload["details"][detail_key][match_key] is False

    shutil.rmtree(work_dir)


def test_prd_validator_blocks_incomplete_evidence_front_matter():
    work_dir = ROOT / ".tmp" / "test-prd-validator-front-matter"
    if work_dir.exists():
        shutil.rmtree(work_dir)
    intake = work_dir / "prd"
    write_prd_intake_fixture(intake)

    (intake / "evidence-packet.md").write_text(
        "---\nready_gate: PASS\n---\n# PRD Evidence Packet\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [sys.executable, str(PRD_VALIDATOR), "--json", str(intake)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert "PRD_READY_WITHOUT_EVIDENCE" in payload["blockers"]

    shutil.rmtree(work_dir)


@pytest.mark.parametrize(
    ("kind", "writer", "validator", "packet_name", "ready_blocker"),
    [
        ("prd", write_prd_intake_fixture, PRD_VALIDATOR, "evidence-packet.md", "PRD_READY_WITHOUT_EVIDENCE"),
        (
            "test-case",
            write_test_case_intake_fixture,
            TEST_CASE_VALIDATOR,
            "evidence-packet.md",
            "TEST_READY_WITHOUT_EVIDENCE",
        ),
        (
            "visual",
            write_image_visual_intake_fixture,
            VALIDATOR,
            "visual-evidence-packet.md",
            "VISUAL_READY_WITHOUT_EVIDENCE",
        ),
    ],
)
def test_validators_block_blocked_evidence_packet(
    kind,
    writer,
    validator,
    packet_name,
    ready_blocker,
):
    work_dir = ROOT / ".tmp" / f"test-{kind}-validator-blocked-packet"
    if work_dir.exists():
        shutil.rmtree(work_dir)
    intake = work_dir / kind
    writer(intake)

    packet = intake / packet_name
    text = packet.read_text(encoding="utf-8")
    text = text.replace("ready_gate: PASS", "ready_gate: BLOCKED")
    packet.write_text(text, encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(validator), "--json", str(intake)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert ready_blocker in payload["blockers"]

    shutil.rmtree(work_dir)


def test_test_case_validator_passes_complete_minimal_intake():
    work_dir = ROOT / ".tmp" / "test-case-validator-pass"
    if work_dir.exists():
        shutil.rmtree(work_dir)
    intake = work_dir / "test-cases"
    write_test_case_intake_fixture(intake)

    result = subprocess.run(
        [sys.executable, str(TEST_CASE_VALIDATOR), str(intake)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "Test-case intake readiness: PASS" in result.stdout

    shutil.rmtree(work_dir)


def test_test_case_validator_allows_remote_source_gap_but_blocks_integrity():
    work_dir = ROOT / ".tmp" / "test-case-validator-remote-source-gap"
    if work_dir.exists():
        shutil.rmtree(work_dir)
    intake = work_dir / "test-cases"
    write_test_case_intake_fixture(intake)

    (intake / "source-manifest.yaml").write_text(
        "\n".join(
            [
                "source_type: issue",
                "source_integrity_complete: false",
                "captured_at: '2026-07-01T00:00:00Z'",
                "capture_method: remote_issue",
                "framework_or_format: issue",
                "execution_scope: regression",
                "snapshot_status: not_available",
                "integrity_gap_reason: Issue was referenced without a local exported snapshot.",
                "retrieval_metadata:",
                "  retrieved_at: '2026-07-01T00:00:00Z'",
                "  stable_url: https://example.com/issues/1",
                "  visible_title: Regression case",
                "source_files:",
                "  - path: https://example.com/issues/1",
                "    mime_type: text/html",
                "    checksum_status: unavailable",
                "    role: original",
                "",
            ]
        ),
        encoding="utf-8",
    )

    result = subprocess.run(
        [sys.executable, str(TEST_CASE_VALIDATOR), "--json", str(intake)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert "TEST_SOURCE_INTEGRITY_INCOMPLETE" in payload["blockers"]
    assert "TEST_READY_WITHOUT_EVIDENCE" in payload["blockers"]
    assert "TEST_SCHEMA_INVALID" not in payload["blockers"]
    assert "TEST_SOURCE_FILE_MISSING" not in payload["blockers"]
    assert payload["details"]["source_files"][0]["remote_ref"] is True

    shutil.rmtree(work_dir)


def test_test_case_validator_blocks_missing_assertions_and_coverage():
    work_dir = ROOT / ".tmp" / "test-case-validator-missing-assertions"
    if work_dir.exists():
        shutil.rmtree(work_dir)
    intake = work_dir / "test-cases"
    write_test_case_intake_fixture(intake)

    text = (intake / "test-case-intake.yaml").read_text(encoding="utf-8")
    text = text.replace("assertions_complete: true", "assertions_complete: false")
    text = text.replace("coverage_gaps_recorded: true", "coverage_gaps_recorded: false")
    text = text.replace("    assertions: ['save path returns success']", "    assertions: []")
    text = text.replace("coverage_gaps:\n  - Error-state coverage is not present in the fixture.\n", "coverage_gaps: []\n")
    text = text.replace("    coverage_signal: happy_path_present_error_path_missing", "    coverage_signal: ''")
    (intake / "test-case-intake.yaml").write_text(text, encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(TEST_CASE_VALIDATOR), str(intake)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 1
    assert "TEST_ASSERTIONS_MISSING" in result.stdout
    assert "TEST_COVERAGE_GAPS_MISSING" in result.stdout
    assert "TEST_READY_WITHOUT_EVIDENCE" in result.stdout

    shutil.rmtree(work_dir)


def test_test_case_validator_reports_schema_errors_in_json():
    work_dir = ROOT / ".tmp" / "test-case-validator-schema-error"
    if work_dir.exists():
        shutil.rmtree(work_dir)
    intake = work_dir / "test-cases"
    write_test_case_intake_fixture(intake)

    text = (intake / "test-case-intake.yaml").read_text(encoding="utf-8")
    text = text.replace("    category: unit", "    category: smoke")
    (intake / "test-case-intake.yaml").write_text(text, encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(TEST_CASE_VALIDATOR), "--json", str(intake)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert "TEST_SCHEMA_INVALID" in payload["blockers"]
    assert "TEST_READY_WITHOUT_EVIDENCE" in payload["blockers"]
    assert payload["details"]["schema_validation"]["test_case_intake"]["valid"] is False

    shutil.rmtree(work_dir)


def test_visual_validator_blocks_missing_source_type_details():
    work_dir = ROOT / ".tmp" / "test-validator-missing-source-details"
    if work_dir.exists():
        shutil.rmtree(work_dir)
    intake = work_dir / "visual-design"
    write_visual_intake_fixture(intake, "image", "low", "wireframe.png")

    text = (intake / "design-source-manifest.yaml").read_text(encoding="utf-8")
    text = text.split("source_details:", 1)[0]
    (intake / "design-source-manifest.yaml").write_text(text, encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(VALIDATOR), "--json", str(intake)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert "VISUAL_SCHEMA_INVALID" in payload["blockers"]
    assert payload["details"]["schema_validation"]["visual_source_manifest"]["valid"] is False

    shutil.rmtree(work_dir)


def test_validator_blocks_unsupported_visual_source_type():
    work_dir = ROOT / ".tmp" / "test-validator-unsupported-source"
    if work_dir.exists():
        shutil.rmtree(work_dir)
    intake = work_dir / "visual-design"
    write_visual_intake_fixture(intake, "sketch", "high", "design.sketch")

    result = subprocess.run(
        [sys.executable, str(VALIDATOR), str(intake)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 1
    assert "VISUAL_SOURCE_TYPE_UNSUPPORTED" in result.stdout
    assert "VISUAL_SCHEMA_INVALID" in result.stdout
    assert "VISUAL_READY_WITHOUT_EVIDENCE" in result.stdout

    shutil.rmtree(work_dir)


def test_visual_validator_blocks_unbounded_inferred_claim():
    work_dir = ROOT / ".tmp" / "test-validator-unbounded-inference"
    if work_dir.exists():
        shutil.rmtree(work_dir)
    intake = work_dir / "visual-design"
    write_visual_intake_fixture(intake, "image", "medium", "wireframe.png")

    text = (intake / "visual-requirements.yaml").read_text(encoding="utf-8")
    text = text.replace("    evidence_type: observed", "    evidence_type: inferred")
    (intake / "visual-requirements.yaml").write_text(text, encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(VALIDATOR), "--json", str(intake)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert "VISUAL_SCHEMA_INVALID" in payload["blockers"]
    assert "VISUAL_INFERENCE_CONTRACT_INVALID" in payload["blockers"]
    assert payload["details"]["visual_requirements"]["evidence_type_counts"]["inferred"] == 1

    shutil.rmtree(work_dir)


def test_visual_validator_blocks_candidate_promoted_to_accepted_claim():
    work_dir = ROOT / ".tmp" / "test-validator-candidate-promoted"
    if work_dir.exists():
        shutil.rmtree(work_dir)
    intake = work_dir / "visual-design"
    write_visual_intake_fixture(intake, "image", "medium", "wireframe.png")

    text = (intake / "visual-requirements.yaml").read_text(encoding="utf-8")
    text = text.replace("    evidence_type: observed", "    evidence_type: candidate")
    text = text.replace("    confidence: high", "    confidence: medium")
    text = text.replace(
        f"    fidelity_level: medium",
        "\n".join(
            [
                "    inference_rule: visual_button_shape + short_text_label",
                "    confidence_method: rule_score_v1",
                "    score_breakdown:",
                "      - signal: visual_button_shape",
                "        weight: 0.25",
                "      - signal: short_text_label",
                "        weight: 0.2",
                "    downstream_use: accepted_claim",
                "    missing_evidence:",
                "      - component_instance",
                "    blocking_conditions:",
                "      - promote only after component or prototype evidence exists",
                "    fidelity_level: medium",
            ]
        ),
    )
    (intake / "visual-requirements.yaml").write_text(text, encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(VALIDATOR), "--json", str(intake)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert "VISUAL_SCHEMA_INVALID" in payload["blockers"]
    assert "VISUAL_INFERENCE_CONTRACT_INVALID" in payload["blockers"]

    shutil.rmtree(work_dir)


def test_visual_validator_blocks_unsupported_claim_even_when_packet_says_pass():
    work_dir = ROOT / ".tmp" / "test-validator-unsupported-claim"
    if work_dir.exists():
        shutil.rmtree(work_dir)
    intake = work_dir / "visual-design"
    write_visual_intake_fixture(intake, "figma", "high", "figma-source.txt")

    text = (intake / "visual-requirements.yaml").read_text(encoding="utf-8")
    text = text.replace("    evidence_type: observed", "    evidence_type: unsupported")
    text = text.replace(
        "    engineering_action: Implement matching hierarchy",
        "\n".join(
            [
                "    blocker_code: FIGMA_UNSUPPORTED_STATE_INFERENCE",
                "    reason: No variant, prototype state, naming convention, or source note defines loading behavior.",
                "    downstream_use: blocked",
                "    missing_evidence:",
                "      - variant_state",
                "      - prototype_state",
                "    blockers:",
                "      - FIGMA_UNSUPPORTED_STATE_INFERENCE",
                "    engineering_action: Keep the loading state unresolved",
            ]
        ),
    )
    (intake / "visual-requirements.yaml").write_text(text, encoding="utf-8")

    metadata = intake / "figma-metadata.part-001.xml"
    metadata.write_text("<figma><node id=\"1\" name=\"Root\" /></figma>\n", encoding="utf-8")

    import hashlib

    digest = hashlib.sha256(metadata.read_bytes()).hexdigest()
    (intake / "figma-metadata.index.yaml").write_text(
        "\n".join(
            [
                "file_url: https://www.figma.com/file/example",
                "file_key: example",
                "page_id: page-1",
                "selected_node_ids: ['1']",
                "captured_at: '2026-06-22T00:00:00Z'",
                "mcp_tool: get_metadata",
                "design_version_or_timestamp: '2026-06-22T00:00:00Z'",
                "selected_subtree_complete: true",
                "raw_metadata_complete: true",
                "expected_root_node_ids: ['1']",
                "captured_root_node_ids: ['1']",
                "missing_root_node_ids: []",
                "gap_count: 0",
                "gaps: []",
                "shards:",
                "  - path: figma-metadata.part-001.xml",
                f"    byte_size: {metadata.stat().st_size}",
                f"    sha256: {digest}",
                "    root_node_ids: ['1']",
                "    node_count: 1",
                "    truncated: false",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (intake / "figma-node-inventory.yaml").write_text(
        "\n".join(
            [
                "raw_node_count: 1",
                "inventory_node_count: 1",
                "excluded_node_count: 0",
                "missing_node_count: 0",
                "duplicate_node_count: 0",
                "truncated_raw_evidence: false",
                "node_inventory_coverage: 100%",
                "parity_passed: true",
                "",
            ]
        ),
        encoding="utf-8",
    )
    write_figma_normalized_tree_fixture(intake, ["1"])

    result = subprocess.run(
        [sys.executable, str(VALIDATOR), "--json", str(intake)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert "VISUAL_BLOCKER_LINT_ERRORS" in payload["blockers"]
    assert "VISUAL_READY_WITHOUT_EVIDENCE" in payload["blockers"]
    assert payload["details"]["visual_requirements"]["evidence_type_counts"]["unsupported"] == 1

    shutil.rmtree(work_dir)


def test_visual_validator_blocks_helper_artifacts_as_source_refs():
    work_dir = ROOT / ".tmp" / "test-visual-helper-artifact-source-refs"
    if work_dir.exists():
        shutil.rmtree(work_dir)
    intake = work_dir / "visual-design"
    write_visual_intake_fixture(intake, "image", "medium", "wireframe.png")

    requirements = yaml.safe_load((intake / "visual-requirements.yaml").read_text(encoding="utf-8"))
    requirements["requirements"][0]["source_refs"] = [
        "delivery/index.html#home-page",
        "source-files/wireframe.png#full",
    ]
    (intake / "visual-requirements.yaml").write_text(yaml.safe_dump(requirements), encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(VALIDATOR), "--json", str(intake)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert "VISUAL_SCHEMA_INVALID" in payload["blockers"]
    assert "VISUAL_REQUIREMENTS_UNTRACEABLE" in payload["blockers"]
    helper_refs = payload["details"]["visual_requirements"]["supporting_artifact_source_refs"]
    assert helper_refs[0]["refs"] == ["delivery/index.html#home-page"]

    shutil.rmtree(work_dir)


def test_figma_metadata_capture_stages_shards_and_passes_validator():
    work_dir = ROOT / ".tmp" / "test-figma-metadata-capture-pass"
    if work_dir.exists():
        shutil.rmtree(work_dir)
    intake = work_dir / "visual-design"
    write_visual_intake_fixture(intake, "figma", "high", "figma-source.txt")
    raw_dir = work_dir / "raw"
    raw_dir.mkdir(parents=True)
    (raw_dir / "root-1.xml").write_text(
        '<figma><node id="1" name="Root"><node id="1:child" name="Child" /></node></figma>\n',
        encoding="utf-8",
    )
    (raw_dir / "root-2.xml").write_text(
        '<figma><node id="2" name="Second root" /></figma>\n',
        encoding="utf-8",
    )

    capture = subprocess.run(
        [
            sys.executable,
            str(FIGMA_METADATA_CAPTURE),
            str(intake),
            "--metadata-source",
            str(raw_dir / "root-1.xml"),
            "--metadata-source",
            str(raw_dir / "root-2.xml"),
            "--file-url",
            "https://www.figma.com/design/example/Foo",
            "--file-key",
            "example",
            "--page-id",
            "page-1",
            "--node-id",
            "1",
            "--node-id",
            "2",
            "--captured-at",
            "2026-07-02T00:00:00Z",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    assert capture.returncode == 0, capture.stdout + capture.stderr
    assert (intake / "figma-metadata.part-001.xml").exists()
    assert (intake / "figma-metadata.part-002.xml").exists()
    index = yaml.safe_load((intake / "figma-metadata.index.yaml").read_text(encoding="utf-8"))
    inventory = yaml.safe_load((intake / "figma-node-inventory.yaml").read_text(encoding="utf-8"))
    assert index["raw_metadata_complete"] is True
    assert index["selected_subtree_complete"] is True
    assert index["captured_root_node_ids"] == ["1", "2"]
    assert index["shards"][0]["sha256"]
    assert inventory["raw_node_count"] == 3
    assert inventory["parity_passed"] is True

    normalize = subprocess.run(
        [sys.executable, str(FIGMA_LAYOUT_NORMALIZE), str(intake)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    assert normalize.returncode == 0, normalize.stdout + normalize.stderr
    normalized = yaml.safe_load((intake / "figma-normalized-tree.yaml").read_text(encoding="utf-8"))
    assert normalized["normalization_complete"] is True
    assert normalized["normalized_node_count"] == 3

    result = subprocess.run(
        [sys.executable, str(VALIDATOR), str(intake)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "Visual design intake readiness: PASS" in result.stdout

    shutil.rmtree(work_dir)


def test_figma_metadata_capture_blocks_truncated_shard():
    work_dir = ROOT / ".tmp" / "test-figma-metadata-capture-truncated"
    if work_dir.exists():
        shutil.rmtree(work_dir)
    intake = work_dir / "visual-design"
    intake.mkdir(parents=True)
    raw = work_dir / "truncated.xml"
    raw.write_text('<figma truncated="true"><node id="1" name="Root" /></figma>\n', encoding="utf-8")

    capture = subprocess.run(
        [
            sys.executable,
            str(FIGMA_METADATA_CAPTURE),
            str(intake),
            "--metadata-source",
            str(raw),
            "--file-url",
            "https://www.figma.com/design/example/Foo",
            "--file-key",
            "example",
            "--page-id",
            "page-1",
            "--node-id",
            "1",
            "--captured-at",
            "2026-07-02T00:00:00Z",
            "--json",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    payload = json.loads(capture.stdout)
    index = yaml.safe_load((intake / "figma-metadata.index.yaml").read_text(encoding="utf-8"))
    assert capture.returncode == 1
    assert payload["status"] == "BLOCKED"
    assert "FIGMA_RAW_METADATA_TRUNCATED" in payload["blockers"]
    assert index["raw_metadata_complete"] is False
    assert index["shards"][0]["truncated"] is True

    shutil.rmtree(work_dir)


def test_validator_passes_complete_minimal_figma_intake():
    work_dir = ROOT / ".tmp" / "test-validator-pass"
    if work_dir.exists():
        shutil.rmtree(work_dir)
    intake = work_dir / "visual-design"
    write_visual_intake_fixture(intake, "figma", "high", "figma-source.txt")

    metadata = intake / "figma-metadata.part-001.xml"
    metadata.write_text("<figma><node id=\"1\" name=\"Root\" /></figma>\n", encoding="utf-8")

    import hashlib

    digest = hashlib.sha256(metadata.read_bytes()).hexdigest()

    (intake / "figma-metadata.index.yaml").write_text(
        "\n".join(
            [
                "file_url: https://www.figma.com/file/example",
                "file_key: example",
                "page_id: page-1",
                "selected_node_ids:",
                "  - '1'",
                "captured_at: '2026-06-22T00:00:00Z'",
                "mcp_tool: get_metadata",
                "design_version_or_timestamp: '2026-06-22T00:00:00Z'",
                "selected_subtree_complete: true",
                "raw_metadata_complete: true",
                "expected_root_node_ids:",
                "  - '1'",
                "captured_root_node_ids:",
                "  - '1'",
                "missing_root_node_ids: []",
                "gap_count: 0",
                "gaps: []",
                "shards:",
                "  - path: figma-metadata.part-001.xml",
                f"    byte_size: {metadata.stat().st_size}",
                f"    sha256: {digest}",
                "    root_node_ids:",
                "      - '1'",
                "    node_count: 1",
                "    truncated: false",
                "",
            ]
        ),
        encoding="utf-8",
    )

    (intake / "figma-node-inventory.yaml").write_text(
        "\n".join(
            [
                "raw_node_count: 1",
                "inventory_node_count: 1",
                "excluded_node_count: 0",
                "missing_node_count: 0",
                "duplicate_node_count: 0",
                "truncated_raw_evidence: false",
                "node_inventory_coverage: 100%",
                "parity_passed: true",
                "",
            ]
        ),
        encoding="utf-8",
    )
    write_figma_normalized_tree_fixture(intake, ["1"])
    result = subprocess.run(
        [sys.executable, str(VALIDATOR), str(intake)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "Visual design intake readiness: PASS" in result.stdout

    shutil.rmtree(work_dir)


def test_visual_validator_blocks_missing_figma_normalized_tree():
    work_dir = ROOT / ".tmp" / "test-validator-missing-figma-normalized-tree"
    if work_dir.exists():
        shutil.rmtree(work_dir)
    intake = work_dir / "visual-design"
    write_visual_intake_fixture(intake, "figma", "high", "figma-source.txt")
    write_figma_metadata_fixture(intake)
    (intake / "figma-normalized-tree.yaml").unlink()

    result = subprocess.run(
        [sys.executable, str(VALIDATOR), "--json", str(intake)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert "FIGMA_NORMALIZED_TREE_MISSING" in payload["blockers"]
    assert payload["details"]["figma_normalized_tree"]["missing"] is True

    shutil.rmtree(work_dir)


def test_visual_validator_blocks_invalid_figma_normalized_tree():
    work_dir = ROOT / ".tmp" / "test-validator-invalid-figma-normalized-tree"
    if work_dir.exists():
        shutil.rmtree(work_dir)
    intake = work_dir / "visual-design"
    write_visual_intake_fixture(intake, "figma", "high", "figma-source.txt")
    write_figma_metadata_fixture(intake)

    normalized = yaml.safe_load((intake / "figma-normalized-tree.yaml").read_text(encoding="utf-8"))
    normalized["node_coverage"] = "incomplete"
    normalized["nodes"][1]["visual_order"] = normalized["nodes"][0]["visual_order"]
    (intake / "figma-normalized-tree.yaml").write_text(yaml.safe_dump(normalized), encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(VALIDATOR), "--json", str(intake)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert "VISUAL_SCHEMA_INVALID" in payload["blockers"]
    assert "FIGMA_NORMALIZED_TREE_INCOMPLETE" in payload["blockers"]
    assert payload["details"]["schema_validation"]["figma_normalized_tree"]["valid"] is False
    assert payload["details"]["figma_layout_normalization"]["duplicate_visual_orders"] == [1]

    shutil.rmtree(work_dir)


def test_visual_validator_blocks_downstream_fields_in_figma_normalized_tree():
    work_dir = ROOT / ".tmp" / "test-validator-downstream-field-figma-normalized-tree"
    if work_dir.exists():
        shutil.rmtree(work_dir)
    intake = work_dir / "visual-design"
    write_visual_intake_fixture(intake, "figma", "high", "figma-source.txt")
    write_figma_metadata_fixture(intake)

    normalized = yaml.safe_load((intake / "figma-normalized-tree.yaml").read_text(encoding="utf-8"))
    normalized["nodes"][0]["delivery_ref"] = "delivery/index.html#root"
    normalized["nodes"][0]["code_component"] = "RootView"
    (intake / "figma-normalized-tree.yaml").write_text(yaml.safe_dump(normalized), encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(VALIDATOR), "--json", str(intake)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert "VISUAL_SCHEMA_INVALID" in payload["blockers"]
    assert payload["details"]["schema_validation"]["figma_normalized_tree"]["valid"] is False

    shutil.rmtree(work_dir)


def test_figma_layout_normalization_blocks_incomplete_raw_metadata():
    work_dir = ROOT / ".tmp" / "test-normalize-blocks-incomplete-raw-metadata"
    if work_dir.exists():
        shutil.rmtree(work_dir)
    intake = work_dir / "visual-design"
    write_visual_intake_fixture(intake, "figma", "high", "figma-source.txt")
    write_figma_metadata_fixture(intake)

    index = yaml.safe_load((intake / "figma-metadata.index.yaml").read_text(encoding="utf-8"))
    index["raw_metadata_complete"] = False
    index["shards"][0]["truncated"] = True
    (intake / "figma-metadata.index.yaml").write_text(yaml.safe_dump(index), encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(FIGMA_LAYOUT_NORMALIZE), "--json", str(intake)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    payload = json.loads(result.stdout)
    normalized = yaml.safe_load((intake / "figma-normalized-tree.yaml").read_text(encoding="utf-8"))
    assert result.returncode == 1
    assert payload["status"] == "BLOCKED"
    assert "FIGMA_NORMALIZED_TREE_INCOMPLETE" in payload["blockers"]
    assert normalized["normalization_complete"] is False
    assert normalized["node_coverage"] == "incomplete"
    assert any(gap["code"] == "FIGMA_RAW_METADATA_TRUNCATED" for gap in normalized["gaps"])

    shutil.rmtree(work_dir)


def test_validator_blocks_legacy_figma_only_without_manifest():
    work_dir = ROOT / ".tmp" / "test-validator-legacy-figma"
    if work_dir.exists():
        shutil.rmtree(work_dir)
    intake = work_dir / "visual-design"
    intake.mkdir(parents=True)

    metadata = intake / "figma-metadata.part-001.xml"
    metadata.write_text("<figma><node id=\"1\" name=\"Root\" /></figma>\n", encoding="utf-8")

    import hashlib

    digest = hashlib.sha256(metadata.read_bytes()).hexdigest()

    (intake / "figma-metadata.index.yaml").write_text(
        "\n".join(
            [
                "file_url: https://www.figma.com/file/example",
                "file_key: example",
                "page_id: page-1",
                "selected_node_ids:",
                "  - '1'",
                "captured_at: '2026-06-22T00:00:00Z'",
                "mcp_tool: get_metadata",
                "design_version_or_timestamp: '2026-06-22T00:00:00Z'",
                "selected_subtree_complete: true",
                "raw_metadata_complete: true",
                "expected_root_node_ids:",
                "  - '1'",
                "captured_root_node_ids:",
                "  - '1'",
                "missing_root_node_ids: []",
                "gap_count: 0",
                "gaps: []",
                "shards:",
                "  - path: figma-metadata.part-001.xml",
                f"    byte_size: {metadata.stat().st_size}",
                f"    sha256: {digest}",
                "    root_node_ids:",
                "      - '1'",
                "    node_count: 1",
                "    truncated: false",
                "",
            ]
        ),
        encoding="utf-8",
    )

    (intake / "figma-node-inventory.yaml").write_text(
        "\n".join(
            [
                "raw_node_count: 1",
                "inventory_node_count: 1",
                "excluded_node_count: 0",
                "missing_node_count: 0",
                "duplicate_node_count: 0",
                "truncated_raw_evidence: false",
                "node_inventory_coverage: 100%",
                "parity_passed: true",
                "",
            ]
        ),
        encoding="utf-8",
    )

    (intake / "figma-evidence-packet.md").write_text(
        "# Figma Evidence Packet\n\n- ready_gate: PASS\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [sys.executable, str(VALIDATOR), str(intake)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 1
    assert "VISUAL_SOURCE_MANIFEST_MISSING" in result.stdout
    assert "FIGMA_READY_WITHOUT_COMPLETENESS_PROOF" in result.stdout

    shutil.rmtree(work_dir)


def test_static_html_delivery_validator_passes_complete_minimal_bundle():
    work_dir = ROOT / ".tmp" / "test-static-html-delivery-validator-pass"
    if work_dir.exists():
        shutil.rmtree(work_dir)
    delivery_dir = work_dir / "visual-design" / "delivery"
    write_static_html_delivery_fixture(delivery_dir)

    result = subprocess.run(
        [sys.executable, str(STATIC_HTML_DELIVERY_VALIDATOR), str(delivery_dir)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "Static HTML delivery readiness: PASS" in result.stdout

    shutil.rmtree(work_dir)


def test_static_html_delivery_validator_blocks_missing_directory():
    result = subprocess.run(
        [sys.executable, str(STATIC_HTML_DELIVERY_VALIDATOR), "missing-dir"],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 1
    assert "STATIC_HTML_REQUIRED_ARTIFACT_MISSING" in result.stdout


def test_static_html_delivery_validator_blocks_source_intake_blocked():
    work_dir = ROOT / ".tmp" / "test-static-html-delivery-source-blocked"
    if work_dir.exists():
        shutil.rmtree(work_dir)
    delivery_dir = work_dir / "visual-design" / "delivery"
    write_static_html_delivery_fixture(delivery_dir)
    packet = delivery_dir.parent / "visual-evidence-packet.md"
    packet.write_text(
        "---\n"
        "ready_gate: BLOCKED\n"
        "blockers: [VISUAL_REQUIREMENTS_MISSING]\n"
        "source_ref_count: 1\n"
        "extracted_item_count: 0\n"
        "generated_at: '2026-06-23T00:00:00Z'\n"
        "---\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [sys.executable, str(STATIC_HTML_DELIVERY_VALIDATOR), "--json", str(delivery_dir)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert "STATIC_HTML_SOURCE_INTAKE_BLOCKED" in payload["blockers"]

    shutil.rmtree(work_dir)


def test_static_html_delivery_validator_reports_schema_errors_in_json():
    work_dir = ROOT / ".tmp" / "test-static-html-delivery-schema-error"
    if work_dir.exists():
        shutil.rmtree(work_dir)
    delivery_dir = work_dir / "visual-design" / "delivery"
    write_static_html_delivery_fixture(delivery_dir)
    report = yaml.safe_load((delivery_dir / "render-replay-report.yaml").read_text(encoding="utf-8"))
    report["operations"][0].pop("target_ref")
    (delivery_dir / "render-replay-report.yaml").write_text(yaml.safe_dump(report), encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(STATIC_HTML_DELIVERY_VALIDATOR), "--json", str(delivery_dir)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert "STATIC_HTML_SCHEMA_INVALID" in payload["blockers"]
    assert payload["details"]["schema_validation"]["static_html_delivery"]["valid"] is False

    shutil.rmtree(work_dir)


@pytest.mark.parametrize(
    ("edit_kind", "expected_blocker"),
    [
        ("missing_html_ref", "STATIC_HTML_REQUIRED_ARTIFACT_MISSING"),
        ("typed_anchor", "STATIC_HTML_REQUIRED_ARTIFACT_MISSING"),
        ("source_intake_ref", "STATIC_HTML_SOURCE_INTAKE_BLOCKED"),
        ("visual_ir_refs", "STATIC_HTML_IR_BLOCKED"),
        ("ir_ref", "STATIC_HTML_IR_BLOCKED"),
        ("missing_asset", "STATIC_HTML_ASSET_INCOMPLETE"),
        ("blocked_ir", "STATIC_HTML_IR_BLOCKED"),
        ("clarification", "STATIC_HTML_CLARIFICATION_REQUIRED"),
        ("operation", "STATIC_HTML_OPERATION_REPLAY_INCOMPLETE"),
        ("motion", "STATIC_HTML_MOTION_ANCHOR_INCOMPLETE"),
        ("viewport", "STATIC_HTML_VIEWPORT_CAPTURE_INCOMPLETE"),
        ("visual_diff", "STATIC_HTML_VISUAL_DIFF_BLOCKED"),
        ("evidence_packet", "STATIC_HTML_READY_WITHOUT_EVIDENCE"),
    ],
)
def test_static_html_delivery_validator_blocks_incomplete_delivery(edit_kind, expected_blocker):
    work_dir = ROOT / ".tmp" / f"test-static-html-delivery-{edit_kind}"
    if work_dir.exists():
        shutil.rmtree(work_dir)
    delivery_dir = work_dir / "visual-design" / "delivery"
    write_static_html_delivery_fixture(delivery_dir)
    report_path = delivery_dir / "render-replay-report.yaml"
    report = yaml.safe_load(report_path.read_text(encoding="utf-8"))

    if edit_kind == "missing_html_ref":
        report["components"][0]["html_ref"] = "index.html#missing-component"
    elif edit_kind == "typed_anchor":
        report["components"][0]["html_ref"] = "index.html#page-home"
    elif edit_kind == "source_intake_ref":
        report["source_intake_ref"] = "../missing-visual-requirements.yaml"
    elif edit_kind == "visual_ir_refs":
        report["visual_ir_refs"] = report["visual_ir_refs"][:-1]
    elif edit_kind == "ir_ref":
        report["pages"][0]["layout_refs"] = ["../visual-ir/layout-tree.yaml#missing-box"]
    elif edit_kind == "missing_asset":
        report["assets"][0]["local_paths"] = ["assets/missing.svg"]
    elif edit_kind == "blocked_ir":
        ir_file = delivery_dir.parent / "visual-ir" / "component-model.yaml"
        ir_file.write_text("ready_gate: BLOCKED\nblockers: [STATIC_HTML_COMPONENT_STATE_INCOMPLETE]\n", encoding="utf-8")
    elif edit_kind == "clarification":
        clarification = delivery_dir.parent / "visual-ir" / "clarification-log.yaml"
        clarification.write_text(
            "ready_gate: PASS\n"
            "blockers: []\n"
            "questions:\n"
            "  - id: CQ-001\n"
            "    required_for_html: true\n"
            "    status: unanswered\n",
            encoding="utf-8",
        )
        report["clarifications"]["required_question_count"] = 1
        report["clarifications"]["unanswered_required_question_ids"] = ["CQ-001"]
    elif edit_kind == "operation":
        report["operations"][0]["replay_status"] = "blocked"
        report["operations"][0]["blockers"] = ["STATIC_HTML_OPERATION_REPLAY_INCOMPLETE"]
    elif edit_kind == "motion":
        report["motion_anchors"][0]["replay_status"] = "blocked"
        report["motion_anchors"][0]["blockers"] = ["STATIC_HTML_MOTION_ANCHOR_INCOMPLETE"]
    elif edit_kind == "viewport":
        report["viewports"][0]["screenshot_refs"] = ["screenshots/missing.png"]
    elif edit_kind == "visual_diff":
        report["visual_diffs"][0]["status"] = "blocked"
        report["visual_diffs"][0]["blockers"] = ["STATIC_HTML_VISUAL_DIFF_BLOCKED"]
    elif edit_kind == "evidence_packet":
        (delivery_dir / "evidence-packet.md").write_text(
            "---\n"
            "ready_gate: BLOCKED\n"
            "blockers: [STATIC_HTML_READY_WITHOUT_EVIDENCE]\n"
            "source_ref_count: 1\n"
            "extracted_item_count: 0\n"
            "generated_at: '2026-07-01T00:00:00Z'\n"
            "---\n",
            encoding="utf-8",
        )

    report_path.write_text(yaml.safe_dump(report, sort_keys=False), encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(STATIC_HTML_DELIVERY_VALIDATOR), "--json", str(delivery_dir)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert expected_blocker in payload["blockers"]

    shutil.rmtree(work_dir)

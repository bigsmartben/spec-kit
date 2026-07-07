#!/usr/bin/env python3
"""Validate Spec Kit visual static HTML delivery bundles."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover - exercised in user environments
    yaml = None

from intake_validator_common import parse_evidence_packet_status, validate_json_schema


BLOCKERS = {
    "SOURCE_INTAKE_BLOCKED": "STATIC_HTML_SOURCE_INTAKE_BLOCKED",
    "REQUIRED_ARTIFACT_MISSING": "STATIC_HTML_REQUIRED_ARTIFACT_MISSING",
    "SCHEMA_INVALID": "STATIC_HTML_SCHEMA_INVALID",
    "IR_BLOCKED": "STATIC_HTML_IR_BLOCKED",
    "CLARIFICATION_REQUIRED": "STATIC_HTML_CLARIFICATION_REQUIRED",
    "ASSET_INCOMPLETE": "STATIC_HTML_ASSET_INCOMPLETE",
    "LAYOUT_INCOMPLETE": "STATIC_HTML_LAYOUT_INCOMPLETE",
    "COMPONENT_STATE_INCOMPLETE": "STATIC_HTML_COMPONENT_STATE_INCOMPLETE",
    "PAGE_ROUTE_INCOMPLETE": "STATIC_HTML_PAGE_ROUTE_INCOMPLETE",
    "OPERATION_REPLAY_INCOMPLETE": "STATIC_HTML_OPERATION_REPLAY_INCOMPLETE",
    "MOTION_ANCHOR_INCOMPLETE": "STATIC_HTML_MOTION_ANCHOR_INCOMPLETE",
    "VIEWPORT_CAPTURE_INCOMPLETE": "STATIC_HTML_VIEWPORT_CAPTURE_INCOMPLETE",
    "VISUAL_DIFF_BLOCKED": "STATIC_HTML_VISUAL_DIFF_BLOCKED",
    "READY_WITHOUT_EVIDENCE": "STATIC_HTML_READY_WITHOUT_EVIDENCE",
}

IR_FILES = {
    "asset_inventory": "asset-inventory.yaml",
    "layout_tree": "layout-tree.yaml",
    "component_model": "component-model.yaml",
    "page_route_model": "page-route-model.yaml",
    "interaction_model": "interaction-model.yaml",
    "motion_anchor_model": "motion-anchor-model.yaml",
    "clarification_log": "clarification-log.yaml",
}

ANCHOR_ATTRS = (
    "id",
    "data-visual-id",
    "data-page-id",
    "data-route-id",
    "data-component-id",
    "data-state-id",
    "data-operation-id",
    "data-motion-id",
)

PAGE_ANCHOR_ATTRS = ("id", "data-page-id", "data-route-id")
COMPONENT_ANCHOR_ATTRS = ("id", "data-component-id", "data-state-id")
OPERATION_TARGET_ANCHOR_ATTRS = ("id", "data-operation-id", "data-component-id")
OPERATION_RESULT_ANCHOR_ATTRS = ("id", "data-state-id", "data-page-id", "data-route-id")
MOTION_ANCHOR_ATTRS = ("id", "data-motion-id", "data-state-id", "data-component-id")
VISUAL_ANCHOR_ATTRS = ("id", "data-visual-id")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("delivery_dir", help="Directory containing delivery/index.html static HTML artifacts")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    args = parser.parse_args()

    delivery_dir = Path(args.delivery_dir)
    blocker_codes: list[str] = []
    warnings: list[str] = []
    details: dict[str, Any] = {"delivery_dir": str(delivery_dir)}

    if not delivery_dir.exists() or not delivery_dir.is_dir():
        blocker_codes.append(BLOCKERS["REQUIRED_ARTIFACT_MISSING"])
        return emit(args.json, details, sorted(set(blocker_codes)), warnings)

    intake_dir = delivery_dir.parent
    validate_source_intake(intake_dir, details, blocker_codes)
    validate_required_artifacts(delivery_dir, details, blocker_codes)
    ir_docs = validate_visual_ir(intake_dir, details, blocker_codes)
    report = load_render_replay_report(delivery_dir, details, blocker_codes)

    html_path = delivery_dir / "index.html"
    html_text = html_path.read_text(encoding="utf-8", errors="replace") if html_path.exists() else ""
    html_index = HtmlIndex.from_text(html_text)
    validate_html_entry(html_text, html_index, details, blocker_codes)
    validate_report_refs(delivery_dir, report, html_index, ir_docs, details, blocker_codes)
    validate_clarifications(ir_docs.get("clarification_log", {}), report, details, blocker_codes)
    validate_evidence_packet(delivery_dir, details, blocker_codes, warnings)

    return emit(args.json, details, sorted(set(blocker_codes)), warnings)


def validate_source_intake(
    intake_dir: Path,
    details: dict[str, Any],
    blocker_codes: list[str],
) -> None:
    validator = Path(__file__).resolve().with_name("validate_visual_design_intake.py")
    result = subprocess.run(
        [sys.executable, str(validator), str(intake_dir), "--json"],
        text=True,
        capture_output=True,
    )
    try:
        payload = json.loads(result.stdout or "{}")
    except json.JSONDecodeError:
        payload = {}
    details["source_intake"] = {
        "path": str(intake_dir),
        "validator": str(validator),
        "status": payload.get("status"),
        "blockers": payload.get("blockers"),
    }
    if result.returncode != 0 or payload.get("status") != "PASS":
        blocker_codes.append(BLOCKERS["SOURCE_INTAKE_BLOCKED"])


def validate_required_artifacts(
    delivery_dir: Path,
    details: dict[str, Any],
    blocker_codes: list[str],
) -> None:
    required = {
        "index_html": delivery_dir / "index.html",
        "render_replay_report": delivery_dir / "render-replay-report.yaml",
        "evidence_packet": delivery_dir / "evidence-packet.md",
        "assets": delivery_dir / "assets",
        "screenshots": delivery_dir / "screenshots",
    }
    missing = [
        name
        for name, path in required.items()
        if not path.exists() or (name in {"assets", "screenshots"} and not path.is_dir())
    ]
    details["required_artifacts"] = {"missing": missing}
    if missing:
        blocker_codes.append(BLOCKERS["REQUIRED_ARTIFACT_MISSING"])


def load_yaml(path: Path, blocker_codes: list[str]) -> dict[str, Any]:
    if yaml is None:
        blocker_codes.append(BLOCKERS["SCHEMA_INVALID"])
        return {}
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError:
        blocker_codes.append(BLOCKERS["SCHEMA_INVALID"])
        return {}
    return data if isinstance(data, dict) else {}


def validate_visual_ir(
    intake_dir: Path,
    details: dict[str, Any],
    blocker_codes: list[str],
) -> dict[str, dict[str, Any]]:
    ir_dir = intake_dir / "visual-ir"
    docs: dict[str, dict[str, Any]] = {}
    summary: dict[str, Any] = {"dir": str(ir_dir), "missing": [], "blocked": []}
    for key, filename in IR_FILES.items():
        path = ir_dir / filename
        if not path.exists():
            summary["missing"].append(filename)
            continue
        doc = load_yaml(path, blocker_codes)
        docs[key] = doc
        blockers = doc.get("blockers")
        ready_gate = str(doc.get("ready_gate") or "").upper()
        if ready_gate != "PASS" or (isinstance(blockers, list) and blockers):
            summary["blocked"].append(filename)
    details["visual_ir"] = summary
    if summary["missing"]:
        blocker_codes.append(BLOCKERS["REQUIRED_ARTIFACT_MISSING"])
    if summary["blocked"]:
        blocker_codes.append(BLOCKERS["IR_BLOCKED"])
    if "asset-inventory.yaml" in summary["missing"] or "asset-inventory.yaml" in summary["blocked"]:
        blocker_codes.append(BLOCKERS["ASSET_INCOMPLETE"])
    if "layout-tree.yaml" in summary["missing"] or "layout-tree.yaml" in summary["blocked"]:
        blocker_codes.append(BLOCKERS["LAYOUT_INCOMPLETE"])
    if "component-model.yaml" in summary["missing"] or "component-model.yaml" in summary["blocked"]:
        blocker_codes.append(BLOCKERS["COMPONENT_STATE_INCOMPLETE"])
    if "page-route-model.yaml" in summary["missing"] or "page-route-model.yaml" in summary["blocked"]:
        blocker_codes.append(BLOCKERS["PAGE_ROUTE_INCOMPLETE"])
    if "interaction-model.yaml" in summary["missing"] or "interaction-model.yaml" in summary["blocked"]:
        blocker_codes.append(BLOCKERS["OPERATION_REPLAY_INCOMPLETE"])
    if "motion-anchor-model.yaml" in summary["missing"] or "motion-anchor-model.yaml" in summary["blocked"]:
        blocker_codes.append(BLOCKERS["MOTION_ANCHOR_INCOMPLETE"])
    return docs


def load_render_replay_report(
    delivery_dir: Path,
    details: dict[str, Any],
    blocker_codes: list[str],
) -> dict[str, Any]:
    report_path = delivery_dir / "render-replay-report.yaml"
    if not report_path.exists():
        return {}
    validate_json_schema(
        instance_path=report_path,
        schema_name="static-html-delivery.schema.json",
        details_key="static_html_delivery",
        details=details,
        blocker_codes=blocker_codes,
        schema_error_code=BLOCKERS["SCHEMA_INVALID"],
    )
    report = load_yaml(report_path, blocker_codes)
    details["render_replay_report"] = {
        "ready_gate": report.get("ready_gate"),
        "blockers": report.get("blockers"),
        "asset_count": len(report.get("assets", []) if isinstance(report.get("assets"), list) else []),
        "page_count": len(report.get("pages", []) if isinstance(report.get("pages"), list) else []),
        "component_count": len(report.get("components", []) if isinstance(report.get("components"), list) else []),
        "operation_count": len(report.get("operations", []) if isinstance(report.get("operations"), list) else []),
        "motion_count": len(report.get("motion_anchors", []) if isinstance(report.get("motion_anchors"), list) else []),
        "viewport_count": len(report.get("viewports", []) if isinstance(report.get("viewports"), list) else []),
    }
    if report.get("ready_gate") != "PASS" or report.get("blockers"):
        blocker_codes.append(BLOCKERS["READY_WITHOUT_EVIDENCE"])
    return report


class HtmlIndex(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.anchor_tags: dict[str, list[dict[str, Any]]] = {}
        self.anchor_attrs: dict[str, set[str]] = {}
        self.delivery_root_found = False

    @classmethod
    def from_text(cls, html_text: str) -> "HtmlIndex":
        index = cls()
        if html_text:
            index.feed(html_text)
        return index

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = {name: value or "" for name, value in attrs}
        if "data-delivery-root" in attr_map:
            self.delivery_root_found = True
        tag_record = {"tag": tag, "attrs": attr_map}
        for attr in ANCHOR_ATTRS:
            value = attr_map.get(attr)
            if value:
                self.anchor_tags.setdefault(value, []).append(tag_record)
                self.anchor_attrs.setdefault(value, set()).add(attr)

    def has_ref(self, ref: str) -> bool:
        fragment = ref_fragment(ref)
        if not fragment:
            return False
        return fragment in self.anchor_tags

    def has_typed_ref(self, ref: str, allowed_attrs: tuple[str, ...]) -> bool:
        fragment = ref_fragment(ref)
        if not fragment:
            return False
        attrs = self.anchor_attrs.get(fragment, set())
        return bool(attrs.intersection(allowed_attrs))

    def duplicate_anchor_values(self) -> list[str]:
        return sorted(value for value, tags in self.anchor_tags.items() if len(tags) > 1)


def ref_fragment(ref: str) -> str:
    normalized = str(ref or "").strip().replace("\\", "/")
    if "#" in normalized:
        return normalized.rsplit("#", 1)[1].strip()
    return normalized.strip()


def validate_html_entry(
    html_text: str,
    html_index: HtmlIndex,
    details: dict[str, Any],
    blocker_codes: list[str],
) -> None:
    duplicate_anchors = html_index.duplicate_anchor_values()
    details["html_entry"] = {
        "present": bool(html_text),
        "delivery_root_found": html_index.delivery_root_found,
        "duplicate_anchor_values": duplicate_anchors,
    }
    if not html_text or not html_index.delivery_root_found or duplicate_anchors:
        blocker_codes.append(BLOCKERS["REQUIRED_ARTIFACT_MISSING"])


def asset_path_exists(delivery_dir: Path, asset_path: str) -> bool:
    value = str(asset_path or "").strip().replace("\\", "/")
    if not value:
        return False
    candidate = (delivery_dir / value).resolve()
    assets_root = (delivery_dir / "assets").resolve()
    try:
        candidate.relative_to(assets_root)
    except ValueError:
        return False
    return candidate.is_file()


def screenshot_ref_exists(delivery_dir: Path, screenshot_ref: str) -> bool:
    value = str(screenshot_ref or "").strip().replace("\\", "/")
    if not value:
        return False
    candidate = (delivery_dir / value).resolve()
    screenshot_root = (delivery_dir / "screenshots").resolve()
    try:
        candidate.relative_to(screenshot_root)
    except ValueError:
        return False
    return candidate.is_file()


def split_ref(ref: str) -> tuple[str, str]:
    normalized = str(ref or "").strip().replace("\\", "/")
    if "#" not in normalized:
        return normalized, ""
    path_part, fragment = normalized.rsplit("#", 1)
    return path_part.strip(), fragment.strip()


def resolved_local_ref_path(delivery_dir: Path, ref: str) -> Path | None:
    path_part, _fragment = split_ref(ref)
    if not path_part or is_remote_ref(path_part):
        return None
    return (delivery_dir / path_part).resolve()


def is_remote_ref(value: str) -> bool:
    return value.startswith(("http://", "https://", "figma://"))


def collect_ir_ids(value: Any, parent_id: str | None = None) -> set[str]:
    ids: set[str] = set()
    if isinstance(value, dict):
        current_id = value.get("id")
        if isinstance(current_id, str) and current_id:
            ids.add(current_id)
            parent_id = current_id
        for key, child in value.items():
            if key in {"states", "variants"} and isinstance(child, list) and parent_id:
                for item in child:
                    if isinstance(item, str) and item:
                        ids.add(f"{parent_id}-{item}")
                    elif isinstance(item, dict):
                        item_id = item.get("id")
                        if isinstance(item_id, str) and item_id:
                            ids.add(item_id)
            ids.update(collect_ir_ids(child, parent_id))
    elif isinstance(value, list):
        for item in value:
            ids.update(collect_ir_ids(item, parent_id))
    return ids


def build_ir_indexes(delivery_dir: Path, ir_docs: dict[str, dict[str, Any]]) -> tuple[set[Path], dict[Path, set[str]]]:
    ir_dir = delivery_dir.parent / "visual-ir"
    required_paths = {(ir_dir / filename).resolve() for filename in IR_FILES.values()}
    ids_by_path: dict[Path, set[str]] = {}
    for key, filename in IR_FILES.items():
        doc = ir_docs.get(key, {})
        ids_by_path[(ir_dir / filename).resolve()] = collect_ir_ids(doc)
    return required_paths, ids_by_path


def ir_ref_exists(delivery_dir: Path, ids_by_path: dict[Path, set[str]], ref: str) -> bool:
    path_part, fragment = split_ref(ref)
    if not path_part or not fragment:
        return False
    path = (delivery_dir / path_part).resolve()
    return fragment in ids_by_path.get(path, set())


def validate_report_refs(
    delivery_dir: Path,
    report: dict[str, Any],
    html_index: HtmlIndex,
    ir_docs: dict[str, dict[str, Any]],
    details: dict[str, Any],
    blocker_codes: list[str],
) -> None:
    missing_html_refs: list[str] = []
    missing_assets: list[str] = []
    missing_source_refs: list[str] = []
    mismatched_visual_ir_refs: list[str] = []
    missing_ir_refs: list[str] = []
    invalid_operation_refs: list[str] = []
    blocked_assets: list[str] = []
    blocked_pages: list[str] = []
    blocked_components: list[str] = []
    blocked_operations: list[str] = []
    blocked_motion: list[str] = []
    missing_screenshots: list[str] = []
    visual_diff_blocked: list[str] = []

    required_ir_paths, ir_ids_by_path = build_ir_indexes(delivery_dir, ir_docs)
    reported_ir_refs = report.get("visual_ir_refs", []) if isinstance(report.get("visual_ir_refs"), list) else []
    reported_ir_paths = {
        path for ref in reported_ir_refs if (path := resolved_local_ref_path(delivery_dir, str(ref))) is not None
    }
    if reported_ir_paths != required_ir_paths:
        missing_from_report = sorted(str(path) for path in required_ir_paths - reported_ir_paths)
        unexpected_in_report = sorted(str(path) for path in reported_ir_paths - required_ir_paths)
        mismatched_visual_ir_refs.extend(missing_from_report + unexpected_in_report)

    source_intake_path = resolved_local_ref_path(delivery_dir, str(report.get("source_intake_ref") or ""))
    if source_intake_path is None or not source_intake_path.exists():
        missing_source_refs.append(str(report.get("source_intake_ref") or "<missing>"))

    operation_ids = {
        str(operation.get("id"))
        for operation in report.get("operations", [])
        if isinstance(operation, dict) and operation.get("id")
    }

    for asset in report.get("assets", []) if isinstance(report.get("assets"), list) else []:
        if not isinstance(asset, dict):
            continue
        asset_id = str(asset.get("id") or "<unknown>")
        if not ir_ref_exists(delivery_dir, ir_ids_by_path, str(asset.get("inventory_ref") or "")):
            missing_ir_refs.append(str(asset.get("inventory_ref") or asset_id))
        if asset.get("status") == "blocked" or asset.get("blockers"):
            blocked_assets.append(asset_id)
        for html_ref in asset.get("html_refs", []) or []:
            if not html_index.has_typed_ref(str(html_ref), VISUAL_ANCHOR_ATTRS):
                missing_html_refs.append(str(html_ref))
        for local_path in asset.get("local_paths", []) or []:
            if not asset_path_exists(delivery_dir, str(local_path)):
                missing_assets.append(str(local_path))

    for page in report.get("pages", []) if isinstance(report.get("pages"), list) else []:
        if not isinstance(page, dict):
            continue
        page_id = str(page.get("id") or "<unknown>")
        if not html_index.has_typed_ref(str(page.get("html_ref") or ""), PAGE_ANCHOR_ATTRS):
            missing_html_refs.append(str(page.get("html_ref") or page_id))
        for ref in (page.get("state_refs", []) or []) + (page.get("layout_refs", []) or []):
            if not ir_ref_exists(delivery_dir, ir_ids_by_path, str(ref)):
                missing_ir_refs.append(str(ref))
        if page.get("status") == "blocked" or page.get("blockers"):
            blocked_pages.append(page_id)

    for component in report.get("components", []) if isinstance(report.get("components"), list) else []:
        if not isinstance(component, dict):
            continue
        component_id = str(component.get("id") or "<unknown>")
        if not html_index.has_typed_ref(str(component.get("html_ref") or ""), COMPONENT_ANCHOR_ATTRS):
            missing_html_refs.append(str(component.get("html_ref") or component_id))
        if not ir_ref_exists(delivery_dir, ir_ids_by_path, str(component.get("component_model_ref") or "")):
            missing_ir_refs.append(str(component.get("component_model_ref") or component_id))
        for ref in component.get("state_refs", []) or []:
            if not ir_ref_exists(delivery_dir, ir_ids_by_path, str(ref)):
                missing_ir_refs.append(str(ref))
        for operation_ref in component.get("operation_refs", []) or []:
            if str(operation_ref) not in operation_ids:
                invalid_operation_refs.append(str(operation_ref))
        if component.get("status") == "blocked" or component.get("blockers"):
            blocked_components.append(component_id)

    for operation in report.get("operations", []) if isinstance(report.get("operations"), list) else []:
        if not isinstance(operation, dict):
            continue
        operation_id = str(operation.get("id") or "<unknown>")
        if not ir_ref_exists(delivery_dir, ir_ids_by_path, str(operation.get("interaction_model_ref") or "")):
            missing_ir_refs.append(str(operation.get("interaction_model_ref") or operation_id))
        if not html_index.has_typed_ref(str(operation.get("target_ref") or ""), OPERATION_TARGET_ANCHOR_ATTRS):
            missing_html_refs.append(str(operation.get("target_ref") or operation_id))
        if not html_index.has_typed_ref(str(operation.get("result_ref") or ""), OPERATION_RESULT_ANCHOR_ATTRS):
            missing_html_refs.append(str(operation.get("result_ref") or operation_id))
        if operation.get("replay_status") != "pass" or operation.get("blockers"):
            blocked_operations.append(operation_id)

    for motion in report.get("motion_anchors", []) if isinstance(report.get("motion_anchors"), list) else []:
        if not isinstance(motion, dict):
            continue
        motion_id = str(motion.get("id") or "<unknown>")
        if not ir_ref_exists(delivery_dir, ir_ids_by_path, str(motion.get("motion_model_ref") or "")):
            missing_ir_refs.append(str(motion.get("motion_model_ref") or motion_id))
        for key in ("trigger_ref", "affected_ref", "end_state_ref"):
            if not html_index.has_typed_ref(str(motion.get(key) or ""), MOTION_ANCHOR_ATTRS):
                missing_html_refs.append(str(motion.get(key) or motion_id))
        if motion.get("replay_status") not in {"pass", "not_applicable"} or motion.get("blockers"):
            blocked_motion.append(motion_id)

    for viewport in report.get("viewports", []) if isinstance(report.get("viewports"), list) else []:
        if not isinstance(viewport, dict):
            continue
        viewport_id = str(viewport.get("id") or "<unknown>")
        for page_ref in viewport.get("page_refs", []) or []:
            if not html_index.has_typed_ref(str(page_ref), PAGE_ANCHOR_ATTRS):
                missing_html_refs.append(str(page_ref))
        for screenshot_ref in viewport.get("screenshot_refs", []) or []:
            if not screenshot_ref_exists(delivery_dir, str(screenshot_ref)):
                missing_screenshots.append(str(screenshot_ref))
        if viewport.get("render_status") != "pass" or viewport.get("blockers"):
            missing_screenshots.append(viewport_id)

    for visual_diff in report.get("visual_diffs", []) if isinstance(report.get("visual_diffs"), list) else []:
        if not isinstance(visual_diff, dict):
            continue
        diff_id = str(visual_diff.get("id") or "<unknown>")
        screenshot_ref = str(visual_diff.get("screenshot_ref") or "")
        if screenshot_ref and not screenshot_ref_exists(delivery_dir, screenshot_ref):
            missing_screenshots.append(screenshot_ref)
        if visual_diff.get("status") != "pass" or visual_diff.get("blockers"):
            visual_diff_blocked.append(diff_id)

    details["delivery_refs"] = {
        "missing_html_refs": sorted(set(missing_html_refs)),
        "missing_assets": sorted(set(missing_assets)),
        "missing_source_refs": sorted(set(missing_source_refs)),
        "mismatched_visual_ir_refs": sorted(set(mismatched_visual_ir_refs)),
        "missing_ir_refs": sorted(set(missing_ir_refs)),
        "invalid_operation_refs": sorted(set(invalid_operation_refs)),
        "blocked_assets": sorted(set(blocked_assets)),
        "blocked_pages": sorted(set(blocked_pages)),
        "blocked_components": sorted(set(blocked_components)),
        "blocked_operations": sorted(set(blocked_operations)),
        "blocked_motion": sorted(set(blocked_motion)),
        "missing_screenshots": sorted(set(missing_screenshots)),
        "visual_diff_blocked": sorted(set(visual_diff_blocked)),
    }
    if missing_html_refs:
        blocker_codes.append(BLOCKERS["REQUIRED_ARTIFACT_MISSING"])
    if missing_source_refs:
        blocker_codes.append(BLOCKERS["SOURCE_INTAKE_BLOCKED"])
    if mismatched_visual_ir_refs or missing_ir_refs:
        blocker_codes.append(BLOCKERS["IR_BLOCKED"])
    if invalid_operation_refs:
        blocker_codes.append(BLOCKERS["OPERATION_REPLAY_INCOMPLETE"])
    if missing_assets or blocked_assets:
        blocker_codes.append(BLOCKERS["ASSET_INCOMPLETE"])
    if blocked_pages:
        blocker_codes.append(BLOCKERS["PAGE_ROUTE_INCOMPLETE"])
    if blocked_components:
        blocker_codes.append(BLOCKERS["COMPONENT_STATE_INCOMPLETE"])
    if blocked_operations:
        blocker_codes.append(BLOCKERS["OPERATION_REPLAY_INCOMPLETE"])
    if blocked_motion:
        blocker_codes.append(BLOCKERS["MOTION_ANCHOR_INCOMPLETE"])
    if missing_screenshots:
        blocker_codes.append(BLOCKERS["VIEWPORT_CAPTURE_INCOMPLETE"])
    if visual_diff_blocked:
        blocker_codes.append(BLOCKERS["VISUAL_DIFF_BLOCKED"])


def validate_clarifications(
    clarification_log: dict[str, Any],
    report: dict[str, Any],
    details: dict[str, Any],
    blocker_codes: list[str],
) -> None:
    unanswered: list[str] = []
    shape_errors: list[str] = []
    required_count = 0
    resolved_required_count = 0
    valid_blockers = set(BLOCKERS.values())
    for question in clarification_log.get("questions", []) if isinstance(clarification_log.get("questions"), list) else []:
        if not isinstance(question, dict):
            shape_errors.append("<non-object-question>")
            continue
        question_id = str(question.get("id") or "<unknown>")
        required_fields = (
            "id",
            "target_artifact",
            "blocked_delivery_surface",
            "blocker_code",
            "question",
            "allowed_answer_shape",
            "required_for_html",
            "status",
            "confirmed_by_user",
            "source_refs",
        )
        missing_fields = [field for field in required_fields if field not in question]
        if missing_fields:
            shape_errors.append(f"{question_id}:missing:{','.join(missing_fields)}")
        if question.get("status") not in {"unanswered", "answered", "out_of_scope"}:
            shape_errors.append(f"{question_id}:invalid_status")
        if question.get("blocker_code") not in valid_blockers:
            shape_errors.append(f"{question_id}:invalid_blocker_code")
        if not isinstance(question.get("source_refs"), list):
            shape_errors.append(f"{question_id}:invalid_source_refs")
        if question.get("status") in {"answered", "out_of_scope"} and not question.get("answer"):
            shape_errors.append(f"{question_id}:missing_answer")
        if question.get("status") == "answered" and question.get("confirmed_by_user") is not True:
            shape_errors.append(f"{question_id}:missing_user_confirmation")
        if question.get("required_for_html") is True and question.get("status") == "unanswered":
            unanswered.append(question_id)
        if question.get("required_for_html") is True:
            required_count += 1
            if question.get("status") in {"answered", "out_of_scope"}:
                resolved_required_count += 1
    report_unanswered = (
        report.get("clarifications", {}).get("unanswered_required_question_ids", [])
        if isinstance(report.get("clarifications"), dict)
        else []
    )
    for question_id in report_unanswered if isinstance(report_unanswered, list) else []:
        unanswered.append(str(question_id))
    report_required_count = (
        report.get("clarifications", {}).get("required_question_count")
        if isinstance(report.get("clarifications"), dict)
        else None
    )
    report_answered_count = (
        report.get("clarifications", {}).get("answered_required_question_count")
        if isinstance(report.get("clarifications"), dict)
        else None
    )
    if report_required_count != required_count:
        shape_errors.append("report_required_question_count_mismatch")
    if report_answered_count != resolved_required_count:
        shape_errors.append("report_answered_required_question_count_mismatch")
    details["clarifications"] = {
        "required_question_count": required_count,
        "resolved_required_question_count": resolved_required_count,
        "unanswered_required_question_ids": sorted(set(unanswered)),
        "shape_errors": sorted(set(shape_errors)),
    }
    if unanswered or shape_errors:
        blocker_codes.append(BLOCKERS["CLARIFICATION_REQUIRED"])


def validate_evidence_packet(
    delivery_dir: Path,
    details: dict[str, Any],
    blocker_codes: list[str],
    warnings: list[str],
) -> None:
    packet = delivery_dir / "evidence-packet.md"
    if not packet.exists():
        blocker_codes.append(BLOCKERS["READY_WITHOUT_EVIDENCE"])
        return
    status = parse_evidence_packet_status(packet.read_text(encoding="utf-8", errors="replace"))
    details["delivery_evidence_packet"] = status["metadata"]
    warnings.extend(status["warnings"])
    packet_blockers = status["metadata"].get("blockers")
    has_packet_blockers = isinstance(packet_blockers, list) and bool(packet_blockers)
    if status["errors"] or status["ready_gate"] != "PASS" or has_packet_blockers:
        blocker_codes.append(BLOCKERS["READY_WITHOUT_EVIDENCE"])


def emit(json_mode: bool, details: dict[str, Any], blockers: list[str], warnings: list[str]) -> int:
    result = {
        "status": "BLOCKED" if blockers else "PASS",
        "blockers": blockers,
        "warnings": warnings,
        "details": details,
    }
    if json_mode:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"Static HTML delivery readiness: {result['status']}")
        if blockers:
            print("Blockers:")
            for blocker in blockers:
                print(f"- {blocker}")
        if warnings:
            print("Warnings:")
            for warning in warnings:
                print(f"- {warning}")
    return 1 if blockers else 0


if __name__ == "__main__":
    sys.exit(main())

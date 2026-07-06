"""Derive a provider-neutral normalized Figma layout tree from raw metadata shards."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any
from xml.etree import ElementTree

try:
    import yaml
except ImportError:  # pragma: no cover - exercised in user environments
    yaml = None


SHARD_GLOB = "figma-metadata.part-*.xml"
INDEX_NAME = "figma-metadata.index.yaml"
INVENTORY_NAME = "figma-node-inventory.yaml"
NORMALIZED_TREE_NAME = "figma-normalized-tree.yaml"


def load_yaml(path: Path) -> dict[str, Any]:
    if yaml is None:
        raise RuntimeError("PyYAML is required to normalize Figma layout metadata")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def dump_yaml(path: Path, data: dict[str, Any]) -> None:
    if yaml is None:
        raise RuntimeError("PyYAML is required to write normalized Figma layout metadata")
    path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=False), encoding="utf-8")


def slug(value: str) -> str:
    text = re.sub(r"[^a-z0-9]+", "-", value.strip().lower())
    return text.strip("-") or "unnamed"


def normalize_name(name: str, node_id: str) -> str:
    cleaned = re.sub(r"\s+", " ", name.strip())
    if cleaned:
        return cleaned
    return f"unnamed-{slug(node_id)}"


def infer_role_hint(tag: str, name: str, node_type: str) -> str:
    haystack = f"{tag} {name} {node_type}".lower()
    role_markers = [
        ("button", "button"),
        ("input", "input"),
        ("field", "input"),
        ("nav", "navigation"),
        ("header", "header"),
        ("footer", "footer"),
        ("image", "image"),
        ("icon", "icon"),
        ("text", "text"),
        ("frame", "frame"),
        ("component", "component"),
        ("instance", "instance"),
    ]
    for marker, role in role_markers:
        if marker in haystack:
            return role
    return "node"


def numeric_attr(attrs: dict[str, Any], names: tuple[str, ...]) -> float | None:
    for name in names:
        value = attrs.get(name)
        if value is None:
            continue
        try:
            return float(value)
        except (TypeError, ValueError):
            continue
    return None


def bounds_from_attrs(attrs: dict[str, Any]) -> dict[str, float] | None:
    x = numeric_attr(attrs, ("x", "absolute_x", "absoluteBoundingBox.x"))
    y = numeric_attr(attrs, ("y", "absolute_y", "absoluteBoundingBox.y"))
    width = numeric_attr(attrs, ("width", "w", "absoluteBoundingBox.width"))
    height = numeric_attr(attrs, ("height", "h", "absoluteBoundingBox.height"))
    bounds = {
        key: value
        for key, value in {"x": x, "y": y, "width": width, "height": height}.items()
        if value is not None
    }
    return bounds or None


def flatten_json_attrs(value: dict[str, Any]) -> dict[str, Any]:
    attrs = dict(value)
    box = value.get("absoluteBoundingBox")
    if isinstance(box, dict):
        for key in ("x", "y", "width", "height"):
            if key in box:
                attrs[f"absoluteBoundingBox.{key}"] = box[key]
    return attrs


def extract_xml_nodes(text: str, shard_name: str) -> list[dict[str, Any]]:
    root = ElementTree.fromstring(text)
    rows: list[dict[str, Any]] = []

    def walk(element: ElementTree.Element, parent_id: str | None, depth: int, sibling_index: int) -> None:
        attrs = dict(element.attrib)
        node_id = attrs.get("id")
        if node_id:
            name = attrs.get("name") or attrs.get("label") or ""
            node_type = attrs.get("type") or element.tag
            rows.append(
                {
                    "source_node_id": str(node_id),
                    "parent_source_node_id": parent_id,
                    "original_name": str(name),
                    "node_type": str(node_type),
                    "role_hint": infer_role_hint(element.tag, str(name), str(node_type)),
                    "bounds": bounds_from_attrs(attrs),
                    "depth": depth,
                    "sibling_index": sibling_index,
                    "source_refs": [f"{shard_name}#node={node_id}"],
                }
            )
            parent_id = str(node_id)
        for index, child in enumerate(list(element)):
            walk(child, parent_id, depth + 1, index)

    walk(root, None, 0, 0)
    return rows


def extract_json_nodes(text: str, shard_name: str) -> list[dict[str, Any]]:
    data = json.loads(text)
    rows: list[dict[str, Any]] = []

    def node_id_for(value: dict[str, Any]) -> str:
        for key in ("id", "nodeId", "node_id"):
            node_id = value.get(key)
            if isinstance(node_id, (str, int)):
                return str(node_id)
        return ""

    def children_for(value: dict[str, Any]) -> list[Any]:
        children = value.get("children")
        if isinstance(children, list):
            return children
        document = value.get("document")
        if isinstance(document, dict):
            return [document]
        return []

    def walk(value: Any, parent_id: str | None, depth: int, sibling_index: int) -> None:
        if not isinstance(value, dict):
            return
        node_id = node_id_for(value)
        next_parent = parent_id
        if node_id:
            attrs = flatten_json_attrs(value)
            name = value.get("name") or value.get("label") or ""
            node_type = value.get("type") or value.get("node_type") or "node"
            rows.append(
                {
                    "source_node_id": node_id,
                    "parent_source_node_id": parent_id,
                    "original_name": str(name),
                    "node_type": str(node_type),
                    "role_hint": infer_role_hint("node", str(name), str(node_type)),
                    "bounds": bounds_from_attrs(attrs),
                    "depth": depth,
                    "sibling_index": sibling_index,
                    "source_refs": [f"{shard_name}#node={node_id}"],
                }
            )
            next_parent = node_id
        for index, child in enumerate(children_for(value)):
            walk(child, next_parent, depth + 1, index)

    walk(data, None, 0, 0)
    return rows


def extract_nodes(path: Path) -> tuple[list[dict[str, Any]], str | None]:
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    try:
        return extract_xml_nodes(text, path.name), None
    except ElementTree.ParseError:
        try:
            return extract_json_nodes(text, path.name), None
        except json.JSONDecodeError as exc:
            return [], f"{path.name}: metadata is neither parseable XML nor JSON: {exc}"


def sort_key_for(row: dict[str, Any]) -> tuple[float, float, int, int, str]:
    bounds = row.get("bounds")
    if not isinstance(bounds, dict):
        bounds = {}
    y = float(bounds.get("y", 0))
    x = float(bounds.get("x", 0))
    return (y, x, int(row.get("depth", 0)), int(row.get("sibling_index", 0)), row["source_node_id"])


def build_normalized_tree(intake_dir: Path) -> dict[str, Any]:
    index_path = intake_dir / INDEX_NAME
    inventory_path = intake_dir / INVENTORY_NAME
    index = load_yaml(index_path) if index_path.exists() else {}
    inventory = load_yaml(inventory_path) if inventory_path.exists() else {}
    gaps: list[dict[str, str]] = []

    if not index_path.exists():
        gaps.append({"code": "FIGMA_METADATA_INDEX_MISSING", "reason": f"{INDEX_NAME} is required"})
    if not inventory_path.exists():
        gaps.append({"code": "FIGMA_METADATA_PARITY_FAILED", "reason": f"{INVENTORY_NAME} is required"})
    if index and not bool(index.get("raw_metadata_complete")):
        gaps.append({"code": "FIGMA_READY_WITHOUT_COMPLETENESS_PROOF", "reason": "raw_metadata_complete is not true"})
    if index and not bool(index.get("selected_subtree_complete")):
        gaps.append({"code": "FIGMA_SELECTED_SUBTREE_INCOMPLETE", "reason": "selected_subtree_complete is not true"})
    for shard in index.get("shards", []) if isinstance(index.get("shards"), list) else []:
        if isinstance(shard, dict) and bool(shard.get("truncated")):
            gaps.append({"code": "FIGMA_RAW_METADATA_TRUNCATED", "reason": f"{shard.get('path')} is marked truncated"})
    if inventory and not bool(inventory.get("parity_passed")):
        gaps.append({"code": "FIGMA_METADATA_PARITY_FAILED", "reason": "parity_passed is not true"})
    if inventory and str(inventory.get("node_inventory_coverage") or "") != "100%":
        gaps.append({"code": "FIGMA_METADATA_PARITY_FAILED", "reason": "node_inventory_coverage is not 100%"})
    if inventory and bool(inventory.get("truncated_raw_evidence")):
        gaps.append({"code": "FIGMA_RAW_METADATA_TRUNCATED", "reason": "truncated_raw_evidence is true"})

    nodes: list[dict[str, Any]] = []
    for shard in sorted(intake_dir.glob(SHARD_GLOB)):
        shard_nodes, error = extract_nodes(shard)
        if error:
            gaps.append({"code": "FIGMA_NORMALIZED_TREE_INCOMPLETE", "reason": error})
        nodes.extend(shard_nodes)

    seen: set[str] = set()
    deduped: list[dict[str, Any]] = []
    duplicate_ids: list[str] = []
    for node in nodes:
        source_node_id = node["source_node_id"]
        if source_node_id in seen:
            duplicate_ids.append(source_node_id)
            continue
        seen.add(source_node_id)
        deduped.append(node)

    sorted_nodes = sorted(deduped, key=sort_key_for)
    group_keys_by_node: dict[str, str] = {}
    for visual_order, node in enumerate(sorted_nodes, start=1):
        normalized_name = normalize_name(node["original_name"], node["source_node_id"])
        group_key = f"{visual_order:04d}-{slug(normalized_name)}-{slug(node['source_node_id'])}"
        group_keys_by_node[node["source_node_id"]] = group_key
        node["normalized_name"] = normalized_name
        node["group_key"] = group_key
        node["visual_order"] = visual_order
        node["sort_key"] = {
            "method": "top_to_bottom_left_to_right_depth_sibling_id",
            "value": list(sort_key_for(node)),
        }
        if node.get("bounds"):
            node["bounds_ref"] = node["bounds"]

    for node in sorted_nodes:
        parent_id = node.get("parent_source_node_id")
        node["parent_group_key"] = group_keys_by_node.get(parent_id) if parent_id else None
        node.pop("bounds", None)
        node.pop("depth", None)
        node.pop("sibling_index", None)

    raw_node_count = int(inventory.get("raw_node_count") or 0)
    normalized_node_count = len(sorted_nodes)
    coverage = "100%" if raw_node_count and raw_node_count == normalized_node_count and not gaps and not duplicate_ids else "incomplete"
    if duplicate_ids:
        gaps.append(
            {
                "code": "FIGMA_NORMALIZED_TREE_INCOMPLETE",
                "reason": f"duplicate source_node_id values skipped: {', '.join(sorted(duplicate_ids))}",
            }
        )

    return {
        "normalization_complete": coverage == "100%",
        "source_metadata_refs": [shard.name for shard in sorted(intake_dir.glob(SHARD_GLOB))],
        "source_index_ref": INDEX_NAME,
        "source_inventory_ref": INVENTORY_NAME,
        "normalization_rules_applied": [
            "rename: normalized_name is derived from original_name without changing source_node_id",
            "grouper: group_key is stable within the normalized tree and parent_group_key mirrors source containment",
            "re-sort: visual_order uses top-to-bottom, left-to-right, depth, source sibling index, then source_node_id",
        ],
        "rename_rule": "preserve source_node_id and original_name; only normalized_name is provider-neutralized",
        "group_rule": "derive group_key from normalized visual order, normalized_name, and source_node_id; preserve parent_group_key",
        "sort_rule": "top_to_bottom_left_to_right_depth_sibling_id",
        "raw_node_count": raw_node_count,
        "normalized_node_count": normalized_node_count,
        "node_coverage": coverage,
        "selected_node_ids": index.get("selected_node_ids") or [],
        "gaps": gaps,
        "nodes": sorted_nodes,
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("intake_dir", type=Path, help="visual-design intake directory")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON result")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        tree = build_normalized_tree(args.intake_dir)
        dump_yaml(args.intake_dir / NORMALIZED_TREE_NAME, tree)
    except Exception as exc:  # pragma: no cover - command-line guard
        result = {"status": "BLOCKED", "blockers": ["FIGMA_NORMALIZED_TREE_MISSING"], "error": str(exc)}
        if args.json:
            print(json.dumps(result, indent=2, sort_keys=True))
        else:
            print("Figma layout normalization: BLOCKED")
            print(str(exc))
        return 1

    blockers = [] if tree["normalization_complete"] else ["FIGMA_NORMALIZED_TREE_INCOMPLETE"]
    result = {
        "status": "PASS" if not blockers else "BLOCKED",
        "blockers": blockers,
        "output": str(args.intake_dir / NORMALIZED_TREE_NAME),
        "raw_node_count": tree["raw_node_count"],
        "normalized_node_count": tree["normalized_node_count"],
        "node_coverage": tree["node_coverage"],
    }
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"Figma layout normalization: {result['status']}")
        print(f"Output: {result['output']}")
        if blockers:
            print("Blockers:")
            for blocker in blockers:
                print(f"- {blocker}")
    return 0 if not blockers else 1


if __name__ == "__main__":
    raise SystemExit(main())

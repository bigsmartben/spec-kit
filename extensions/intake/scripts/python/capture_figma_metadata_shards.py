"""Stage sharded Figma metadata captures into visual-design intake artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from xml.etree import ElementTree


SHARD_PREFIX = "figma-metadata.part-"
INDEX_NAME = "figma-metadata.index.yaml"
INVENTORY_NAME = "figma-node-inventory.yaml"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def yaml_scalar(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if value is None:
        return "null"
    return json.dumps(str(value), ensure_ascii=False)


def write_mapping(path: Path, rows: list[tuple[str, Any]]) -> None:
    lines: list[str] = []
    for key, value in rows:
        if isinstance(value, list):
            lines.append(f"{key}:")
            if not value:
                lines[-1] = f"{key}: []"
            else:
                for item in value:
                    if isinstance(item, dict):
                        lines.append("  - " + next(iter(item.keys())) + f": {yaml_scalar(next(iter(item.values())))}")
                        for sub_key, sub_value in list(item.items())[1:]:
                            write_nested(lines, sub_key, sub_value, indent="    ")
                    else:
                        lines.append(f"  - {yaml_scalar(item)}")
        else:
            lines.append(f"{key}: {yaml_scalar(value)}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_nested(lines: list[str], key: str, value: Any, *, indent: str) -> None:
    if isinstance(value, list):
        if not value:
            lines.append(f"{indent}{key}: []")
            return
        lines.append(f"{indent}{key}:")
        for item in value:
            if isinstance(item, dict):
                lines.append(f"{indent}  - " + next(iter(item.keys())) + f": {yaml_scalar(next(iter(item.values())))}")
                for sub_key, sub_value in list(item.items())[1:]:
                    write_nested(lines, sub_key, sub_value, indent=indent + "    ")
            else:
                lines.append(f"{indent}  - {yaml_scalar(item)}")
        return
    lines.append(f"{indent}{key}: {yaml_scalar(value)}")


def is_metadata_source(path: Path) -> bool:
    return path.suffix.lower() in {".xml", ".json", ".txt"}


def is_canonical_artifact(path: Path, intake_dir: Path) -> bool:
    try:
        path.relative_to(intake_dir.resolve())
    except ValueError:
        return False
    return path.name in {INDEX_NAME, INVENTORY_NAME} or (
        path.name.startswith(SHARD_PREFIX) and path.suffix.lower() == ".xml"
    )


def expand_sources(sources: list[Path], intake_dir: Path) -> list[Path]:
    expanded: list[Path] = []
    for source in sources:
        if source.is_dir():
            for path in sorted(source.rglob("*")):
                if path.is_file() and is_metadata_source(path) and not is_canonical_artifact(path.resolve(), intake_dir):
                    expanded.append(path)
        elif source.is_file():
            if not is_metadata_source(source):
                raise SystemExit(f"metadata source must be .xml, .json, or .txt: {source}")
            if is_canonical_artifact(source.resolve(), intake_dir):
                raise SystemExit(f"metadata source must not be an existing canonical intake artifact: {source}")
            expanded.append(source)
        else:
            raise SystemExit(f"metadata source does not exist: {source}")
    if not expanded:
        raise SystemExit("at least one metadata source file is required")
    return expanded


def looks_truncated(text: str) -> bool:
    lower = text.lower()
    if "truncated" not in lower:
        return False
    allowed = [
        'truncated="false"',
        "truncated='false'",
        '"truncated": false',
        "'truncated': false",
        "truncated: false",
    ]
    return not any(marker in lower for marker in allowed)


def extract_xml_node_ids(text: str) -> tuple[list[str], list[str], str | None]:
    try:
        root = ElementTree.fromstring(text)
    except ElementTree.ParseError as exc:
        return [], [], f"XML_PARSE_ERROR: {exc}"

    all_ids: list[str] = []
    for element in root.iter():
        node_id = element.attrib.get("id")
        if node_id:
            all_ids.append(str(node_id))

    root_ids: list[str] = []
    root_id = root.attrib.get("id")
    if root_id:
        root_ids.append(str(root_id))
    else:
        for child in list(root):
            child_id = child.attrib.get("id")
            if child_id:
                root_ids.append(str(child_id))
        if not root_ids and all_ids:
            root_ids.append(all_ids[0])
    return root_ids, all_ids, None


def extract_json_node_ids(text: str) -> tuple[list[str], list[str], str | None]:
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        return [], [], f"JSON_PARSE_ERROR: {exc}"

    all_ids: list[str] = []

    def walk(value: Any) -> None:
        if isinstance(value, dict):
            for key in ("id", "nodeId", "node_id"):
                node_id = value.get(key)
                if isinstance(node_id, (str, int)):
                    all_ids.append(str(node_id))
                    break
            for child in value.values():
                walk(child)
        elif isinstance(value, list):
            for item in value:
                walk(item)

    walk(data)
    root_ids: list[str] = []
    if isinstance(data, dict):
        for key in ("id", "nodeId", "node_id"):
            node_id = data.get(key)
            if isinstance(node_id, (str, int)):
                root_ids.append(str(node_id))
                break
        if not root_ids:
            document = data.get("document")
            if isinstance(document, dict):
                node_id = document.get("id")
                if isinstance(node_id, (str, int)):
                    root_ids.append(str(node_id))
    if not root_ids and all_ids:
        root_ids.append(all_ids[0])
    return root_ids, all_ids, None


def extract_node_ids(raw: bytes, source: Path) -> tuple[list[str], list[str], str | None]:
    text = raw.decode("utf-8-sig", errors="replace")
    suffix = source.suffix.lower()
    if suffix == ".json":
        return extract_json_node_ids(text)
    if suffix in {".xml", ".txt", ""}:
        root_ids, all_ids, error = extract_xml_node_ids(text)
        if error and suffix == ".txt":
            return extract_json_node_ids(text)
        return root_ids, all_ids, error
    return extract_xml_node_ids(text)


def sorted_unique(values: list[str]) -> list[str]:
    return sorted(set(values))


def build_artifacts(args: argparse.Namespace) -> dict[str, Any]:
    intake_dir = args.intake_dir
    intake_dir.mkdir(parents=True, exist_ok=True)
    sources = expand_sources(args.metadata_source, intake_dir)
    if args.node_id and len(args.node_id) not in {1, len(sources)}:
        raise SystemExit("--node-id must be supplied once for all shards or once per metadata source")

    if args.overwrite:
        for old in intake_dir.glob(f"{SHARD_PREFIX}*.xml"):
            old.unlink()
        for old_name in [INDEX_NAME, INVENTORY_NAME]:
            old = intake_dir / old_name
            if old.exists():
                old.unlink()

    captured_at = args.captured_at or utc_now()
    design_version = args.design_version or captured_at
    shard_rows: list[dict[str, Any]] = []
    all_node_ids: list[str] = []
    all_root_ids: list[str] = []
    gaps: list[dict[str, Any]] = []
    any_truncated = False

    for index, source in enumerate(sources, start=1):
        raw = source.read_bytes()
        text = raw.decode("utf-8-sig", errors="replace")
        root_ids, node_ids, parse_error = extract_node_ids(raw, source)
        if args.node_id:
            root_ids = [args.node_id[index - 1] if len(args.node_id) == len(sources) else args.node_id[0]]

        truncated = looks_truncated(text)
        any_truncated = any_truncated or truncated
        if truncated:
            gaps.append(
                {
                    "code": "FIGMA_RAW_METADATA_TRUNCATED",
                    "source": str(source),
                    "reason": "metadata source contains a truncation marker",
                }
            )
        if parse_error:
            gaps.append(
                {
                    "code": "FIGMA_METADATA_PARITY_FAILED",
                    "source": str(source),
                    "reason": parse_error,
                }
            )
        if not node_ids:
            gaps.append(
                {
                    "code": "FIGMA_METADATA_PARITY_FAILED",
                    "source": str(source),
                    "reason": "no node ids were found in the metadata source",
                }
            )

        shard_name = f"{SHARD_PREFIX}{index:03d}.xml"
        shard_path = intake_dir / shard_name
        if shard_path.exists() and not args.overwrite:
            raise SystemExit(f"refusing to overwrite existing shard without --overwrite: {shard_path}")
        shutil.copyfile(source, shard_path)
        all_node_ids.extend(node_ids)
        all_root_ids.extend(root_ids)
        shard_rows.append(
            {
                "path": shard_name,
                "byte_size": len(raw),
                "sha256": sha256_bytes(raw),
                "root_node_ids": root_ids,
                "node_count": len(sorted_unique(node_ids)),
                "truncated": truncated,
                "source_path": str(source),
            }
        )

    expected_roots = args.node_id or sorted_unique(all_root_ids)
    captured_roots = sorted_unique(all_root_ids)
    missing_roots = sorted(set(expected_roots) - set(captured_roots))
    duplicate_node_count = len(all_node_ids) - len(set(all_node_ids))
    raw_node_count = len(set(all_node_ids))
    metadata_complete = not any_truncated and not missing_roots and raw_node_count > 0 and not any(
        gap["code"] == "FIGMA_METADATA_PARITY_FAILED" for gap in gaps
    )
    selected_subtree_complete = metadata_complete
    parity_passed = metadata_complete and duplicate_node_count == 0

    index_rows: list[tuple[str, Any]] = [
        ("file_url", args.file_url),
        ("file_key", args.file_key),
        ("page_id", args.page_id),
        ("selected_node_ids", expected_roots),
        ("captured_at", captured_at),
        ("mcp_tool", "get_metadata"),
        ("design_version_or_timestamp", design_version),
        ("selected_subtree_complete", selected_subtree_complete),
        ("raw_metadata_complete", metadata_complete),
        ("expected_root_node_ids", expected_roots),
        ("captured_root_node_ids", captured_roots),
        ("missing_root_node_ids", missing_roots),
        ("gap_count", len(gaps)),
        ("gaps", gaps),
        ("shards", shard_rows),
    ]
    write_mapping(intake_dir / INDEX_NAME, index_rows)

    inventory_rows: list[tuple[str, Any]] = [
        ("raw_node_count", raw_node_count),
        ("inventory_node_count", raw_node_count),
        ("excluded_node_count", 0),
        ("missing_node_count", len(missing_roots)),
        ("duplicate_node_count", duplicate_node_count),
        ("truncated_raw_evidence", any_truncated),
        ("node_inventory_coverage", "100%" if parity_passed else "incomplete"),
        ("parity_passed", parity_passed),
        ("captured_root_node_ids", captured_roots),
        ("missing_root_node_ids", missing_roots),
    ]
    write_mapping(intake_dir / INVENTORY_NAME, inventory_rows)

    return {
        "status": "PASS" if metadata_complete and parity_passed else "BLOCKED",
        "intake_dir": str(intake_dir),
        "metadata_shards": [row["path"] for row in shard_rows],
        "index": INDEX_NAME,
        "inventory": INVENTORY_NAME,
        "raw_node_count": raw_node_count,
        "captured_root_node_ids": captured_roots,
        "missing_root_node_ids": missing_roots,
        "gaps": gaps,
        "blockers": sorted(
            {
                gap["code"]
                for gap in gaps
            }
            | ({"FIGMA_METADATA_PARITY_FAILED"} if not parity_passed else set())
        ),
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Copy already-sharded Figma get_metadata outputs into an intake directory, "
            "then write figma-metadata.index.yaml and figma-node-inventory.yaml."
        )
    )
    parser.add_argument("intake_dir", type=Path, help="visual-design intake directory")
    parser.add_argument(
        "--metadata-source",
        type=Path,
        action="append",
        required=True,
        help="Raw get_metadata response file or directory. Repeat for each shard.",
    )
    parser.add_argument("--file-url", required=True, help="Stable Figma file URL")
    parser.add_argument("--file-key", required=True, help="Figma file key")
    parser.add_argument("--page-id", required=True, help="Figma page or source page id")
    parser.add_argument(
        "--node-id",
        action="append",
        help="Expected selected root node id. Repeat once per metadata source for exact root mapping.",
    )
    parser.add_argument("--captured-at", help="Capture timestamp. Defaults to current UTC time.")
    parser.add_argument("--design-version", help="Design version or timestamp. Defaults to captured-at.")
    parser.add_argument("--overwrite", action="store_true", help="Replace existing canonical metadata artifacts.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON result.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    result = build_artifacts(args)
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True))
    else:
        print(f"Figma metadata shard capture: {result['status']}")
        print(f"Output directory: {result['intake_dir']}")
        print(f"Shards: {', '.join(result['metadata_shards'])}")
        if result["blockers"]:
            print("Blockers:")
            for blocker in result["blockers"]:
                print(f"- {blocker}")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

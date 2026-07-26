"""Contract tests for Preset/Extension coding-standard enforcement."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from specify_cli.component_standard import (
    ComponentTarget,
    discover_component_targets,
    main,
    validate_component,
    validate_targets,
)


def _write_package_evidence(root: Path) -> None:
    for filename in ("README.md", "CHANGELOG.md", "LICENSE"):
        (root / filename).write_text(f"# {filename}\n", encoding="utf-8")
    tests_dir = root / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_contract.py").write_text(
        "def test_contract():\n    assert True\n",
        encoding="utf-8",
    )


def _write_command(path: Path, *, extra: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        """---
description: "Create one deterministic report"
---

## User Input

$ARGUMENTS

## Goal

Create `report.md`.

## Operating Boundaries

Read inputs and only write `report.md`.

## Procedure

1. Read the input.
2. Create the report.

## Validation

PASS when the report exists; otherwise return `REPORT_MISSING`.

## Report

Report changed paths, status, and blockers.
"""
        + extra,
        encoding="utf-8",
    )


def _valid_extension(repo_root: Path) -> ComponentTarget:
    root = repo_root / "extensions" / "demo"
    root.mkdir(parents=True)
    _write_package_evidence(root)
    _write_command(root / "commands" / "speckit.demo.report.md")
    (root / "extension.yml").write_text(
        yaml.safe_dump(
            {
                "schema_version": "1.0",
                "extension": {
                    "id": "demo",
                    "name": "Demo",
                    "version": "1.0.0",
                    "description": "Demonstrates the component contract.",
                },
                "requires": {"speckit_version": ">=0.1.0"},
                "provides": {
                    "commands": [
                        {
                            "name": "speckit.demo.report",
                            "file": "commands/speckit.demo.report.md",
                            "description": "Create one report.",
                        }
                    ]
                },
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    return ComponentTarget("extension", root)


def _valid_preset(repo_root: Path) -> ComponentTarget:
    root = repo_root / "presets" / "demo"
    root.mkdir(parents=True)
    _write_package_evidence(root)
    _write_command(root / "commands" / "speckit.specify.md")
    command_path = root / "commands" / "speckit.specify.md"
    command_path.write_text(
        command_path.read_text(encoding="utf-8") + "\n{CORE_TEMPLATE}\n",
        encoding="utf-8",
    )
    (root / "preset.yml").write_text(
        yaml.safe_dump(
            {
                "schema_version": "1.0",
                "preset": {
                    "id": "demo",
                    "name": "Demo",
                    "version": "1.0.0",
                    "description": "Demonstrates preset composition.",
                },
                "requires": {"speckit_version": ">=0.1.0"},
                "provides": {
                    "templates": [
                        {
                            "type": "command",
                            "name": "speckit.specify",
                            "file": "commands/speckit.specify.md",
                            "description": "Wrap the core specify command.",
                            "strategy": "wrap",
                        }
                    ]
                },
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    return ComponentTarget("preset", root)


def test_valid_extension_and_preset_pass(tmp_path: Path) -> None:
    targets = (_valid_extension(tmp_path), _valid_preset(tmp_path))

    report = validate_targets(targets, tmp_path)

    assert report.status == "PASS"
    assert report.issues == ()
    assert validate_targets(targets, tmp_path) == report


def test_discovers_only_components_owning_changed_paths(tmp_path: Path) -> None:
    extension = _valid_extension(tmp_path)
    preset = _valid_preset(tmp_path)

    targets = discover_component_targets(
        tmp_path,
        [
            "README.md",
            extension.root / "commands" / "speckit.demo.report.md",
            "presets/catalog.json",
            "presets/demo/preset.yml",
        ],
    )

    assert targets == (extension, preset)


def test_blocks_path_traversal_and_platform_specific_prompt(tmp_path: Path) -> None:
    target = _valid_extension(tmp_path)
    manifest = yaml.safe_load(target.manifest_path.read_text(encoding="utf-8"))
    manifest["provides"]["commands"].append(
        {
            "name": "speckit.demo.escape",
            "file": "../escape.md",
            "description": "Invalid path.",
        }
    )
    target.manifest_path.write_text(
        yaml.safe_dump(manifest, sort_keys=False),
        encoding="utf-8",
    )
    command_path = target.root / "commands" / "speckit.demo.report.md"
    command_path.write_text(
        command_path.read_text(encoding="utf-8")
        + "\nWrite the result to .kiro/prompts/report.md.\n",
        encoding="utf-8",
    )

    issues = validate_component(target, tmp_path)

    assert {issue.code for issue in issues} >= {"STD034", "STD043"}


def test_blocks_declared_symlink_escape(tmp_path: Path) -> None:
    target = _valid_extension(tmp_path)
    command_path = target.root / "commands" / "speckit.demo.report.md"
    outside_path = tmp_path / "outside.md"
    outside_path.write_text("outside", encoding="utf-8")
    command_path.unlink()
    try:
        command_path.symlink_to(outside_path)
    except OSError as exc:
        pytest.skip(f"symlinks are unavailable: {exc}")

    issues = validate_component(target, tmp_path)

    assert any(issue.code == "STD034" for issue in issues)


def test_blocks_schema_symlink_escape(tmp_path: Path) -> None:
    target = _valid_extension(tmp_path)
    schema_dir = target.root / "schemas"
    schema_dir.mkdir()
    outside_path = tmp_path / "outside.schema.json"
    outside_path.write_text(
        json.dumps(
            {
                "$id": "https://example.invalid/outside.schema.json",
                "type": "object",
                "additionalProperties": False,
            }
        ),
        encoding="utf-8",
    )
    try:
        (schema_dir / "report.schema.json").symlink_to(outside_path)
    except OSError as exc:
        pytest.skip(f"symlinks are unavailable: {exc}")

    issues = validate_component(target, tmp_path)

    assert any(issue.code == "STD074" for issue in issues)


def test_blocks_wrap_without_required_placeholder(tmp_path: Path) -> None:
    target = _valid_preset(tmp_path)
    command_path = target.root / "commands" / "speckit.specify.md"
    command_path.write_text(
        command_path.read_text(encoding="utf-8").replace(
            "{CORE_TEMPLATE}",
            "Core content goes here.",
        ),
        encoding="utf-8",
    )

    issues = validate_component(target, tmp_path)

    assert any(issue.code == "STD067" for issue in issues)


def test_schema_requires_stable_id(tmp_path: Path) -> None:
    target = _valid_extension(tmp_path)
    schema_dir = target.root / "schemas"
    schema_dir.mkdir()
    (schema_dir / "report.schema.json").write_text(
        json.dumps(
            {
                "$schema": "https://json-schema.org/draft/2020-12/schema",
                "type": "object",
                "additionalProperties": False,
            }
        ),
        encoding="utf-8",
    )

    issues = validate_component(target, tmp_path)

    assert any(issue.code == "STD072" for issue in issues)


def test_malformed_preset_values_return_blockers_instead_of_crashing(
    tmp_path: Path,
) -> None:
    target = _valid_preset(tmp_path)
    manifest = yaml.safe_load(target.manifest_path.read_text(encoding="utf-8"))
    manifest["provides"]["templates"][0]["type"] = ["command"]
    manifest["provides"]["templates"][0]["strategy"] = ["wrap"]
    target.manifest_path.write_text(
        yaml.safe_dump(manifest, sort_keys=False),
        encoding="utf-8",
    )

    issues = validate_component(target, tmp_path)

    assert {issue.code for issue in issues} >= {"STD004", "STD062", "STD066"}


def test_requires_three_part_semantic_version(tmp_path: Path) -> None:
    target = _valid_extension(tmp_path)
    manifest = yaml.safe_load(target.manifest_path.read_text(encoding="utf-8"))
    manifest["extension"]["version"] = "1.0"
    target.manifest_path.write_text(
        yaml.safe_dump(manifest, sort_keys=False),
        encoding="utf-8",
    )

    issues = validate_component(target, tmp_path)

    assert any(issue.code == "STD015" for issue in issues)


def test_rejects_invalid_speckit_version_constraint(tmp_path: Path) -> None:
    target = _valid_extension(tmp_path)
    manifest = yaml.safe_load(target.manifest_path.read_text(encoding="utf-8"))
    manifest["requires"]["speckit_version"] = "newest"
    target.manifest_path.write_text(
        yaml.safe_dump(manifest, sort_keys=False),
        encoding="utf-8",
    )

    issues = validate_component(target, tmp_path)

    assert any(issue.code == "STD016" for issue in issues)


def test_json_cli_output_is_machine_readable(
    tmp_path: Path,
    capsys,
) -> None:
    target = _valid_extension(tmp_path)

    exit_code = main(
        [
            "--repo-root",
            str(tmp_path),
            "--format",
            "json",
            str(target.root),
        ]
    )

    payload = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert payload["status"] == "PASS"
    assert payload["components"] == ["extensions/demo"]


def test_cli_rejects_unmatched_explicit_path(
    tmp_path: Path,
    capsys,
) -> None:
    exit_code = main(
        [
            "--repo-root",
            str(tmp_path),
            "extensions/missing",
        ]
    )

    assert exit_code == 2
    assert "No Preset or Extension component matched" in capsys.readouterr().err


def test_json_cli_errors_remain_machine_readable(
    tmp_path: Path,
    capsys,
) -> None:
    exit_code = main(
        [
            "--repo-root",
            str(tmp_path),
            "--format",
            "json",
            "extensions/missing",
        ]
    )

    payload = json.loads(capsys.readouterr().out)
    assert exit_code == 2
    assert payload["status"] == "ERROR"
    assert payload["issues"][0]["code"] == "STD000"


def test_repository_scaffolds_follow_standard() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    targets = (
        ComponentTarget("extension", repo_root / "extensions" / "template"),
        ComponentTarget("preset", repo_root / "presets" / "scaffold"),
    )

    report = validate_targets(targets, repo_root)

    assert report.status == "PASS", report.as_dict()
    assert report.warnings == ()

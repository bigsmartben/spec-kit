"""Focused contract checks to keep when copying this Preset scaffold."""

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_manifest_declares_existing_files() -> None:
    manifest = yaml.safe_load((ROOT / "preset.yml").read_text(encoding="utf-8"))

    for entry in manifest["provides"]["templates"]:
        assert (ROOT / entry["file"]).is_file()


def test_command_overrides_expose_execution_contract() -> None:
    manifest = yaml.safe_load((ROOT / "preset.yml").read_text(encoding="utf-8"))

    for entry in manifest["provides"]["templates"]:
        if entry["type"] != "command":
            continue
        content = (ROOT / entry["file"]).read_text(encoding="utf-8")
        for heading in (
            "## Goal",
            "## Operating Boundaries",
            "## Validation",
            "## Report",
        ):
            assert heading in content

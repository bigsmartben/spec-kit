"""Contract tests for the lean preset package."""

from pathlib import Path

import yaml


PRESET_DIR = Path(__file__).resolve().parents[1]


def test_lean_preset_replaces_the_five_core_commands():
    manifest = yaml.safe_load(
        (PRESET_DIR / "preset.yml").read_text(encoding="utf-8")
    )
    templates = manifest["provides"]["templates"]
    assert {template["name"] for template in templates} == {
        "speckit.constitution",
        "speckit.specify",
        "speckit.plan",
        "speckit.tasks",
        "speckit.implement",
    }
    assert all(template["replaces"] == template["name"] for template in templates)
    assert all((PRESET_DIR / template["file"]).is_file() for template in templates)

"""Contract tests for the self-test preset package."""

from pathlib import Path

import yaml


PRESET_DIR = Path(__file__).resolve().parents[1]


def test_self_test_preset_declares_existing_test_assets():
    manifest = yaml.safe_load(
        (PRESET_DIR / "preset.yml").read_text(encoding="utf-8")
    )
    assert manifest["preset"]["id"] == "self-test"
    templates = manifest["provides"]["templates"]
    assert len(templates) == 7
    assert all((PRESET_DIR / template["file"]).is_file() for template in templates)

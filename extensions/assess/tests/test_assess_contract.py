"""Contract tests for the assess extension package."""

from pathlib import Path

import yaml


EXTENSION_DIR = Path(__file__).resolve().parents[1]


def test_assess_manifest_declares_each_command_file():
    manifest = yaml.safe_load(
        (EXTENSION_DIR / "extension.yml").read_text(encoding="utf-8")
    )
    assert manifest["extension"]["id"] == "assess"

    commands = manifest["provides"]["commands"]
    assert {command["name"] for command in commands} == {
        "speckit.assess.intake",
        "speckit.assess.research",
        "speckit.assess.define",
        "speckit.assess.shape",
        "speckit.assess.decide",
    }
    assert all((EXTENSION_DIR / command["file"]).is_file() for command in commands)

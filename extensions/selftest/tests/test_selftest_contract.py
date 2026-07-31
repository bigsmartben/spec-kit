"""Contract tests for the selftest extension package."""

from pathlib import Path

import yaml


EXTENSION_DIR = Path(__file__).resolve().parents[1]


def test_selftest_command_uses_its_canonical_filename():
    manifest = yaml.safe_load(
        (EXTENSION_DIR / "extension.yml").read_text(encoding="utf-8")
    )
    command = manifest["provides"]["commands"][0]
    assert command["name"] == "speckit.selftest.extension"
    assert command["file"] == "commands/speckit.selftest.extension.md"
    assert (EXTENSION_DIR / command["file"]).is_file()
